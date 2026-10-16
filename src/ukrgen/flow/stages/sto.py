"""
Tiling every STO with its chosen implementation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ...components.tile import tile, dimension_properties as dimp, dimension_type as dimt
from ...components.operation import operation
from ...generators.tiling import generate_tiling, generators
from ...support.tiles import index_extents, operand_tiles, lane_axes, register_tiles, ONE
from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import sto_kind, block_description


@dataclass
class sto_tiling:
    """
    An STO tiled with its implementation

    :param sto: STO name
    :param order: its indices, outermost first
    :param extents: what one operation covers along each index
    :param tiles: each operand's tile: what one operation covers of it
    :param ops: the operations
    :param registers: each operand's register tile - wider than its tile for
                      an operand used one element at a time
    """
    sto : str
    order : tuple[str, ...]
    extents : dict[str, dimp]
    tiles : dict[str, tile]
    ops : list[operation]
    registers : dict[str, tile] = None
    counts : dict[str, int] = None
    generate_args : dict = None

    def regenerate(self, counts: dict[str, int] | None = None,
                   offset: dict[str, int] | None = None) -> list[operation]:
        """
        The same tiling with other counts or shifted along indices by name:
        the tail of a loop runs one step along the loop index
        """
        args = dict(self.generate_args)
        generate = args.pop("generate")
        return generate(order=self.order, counts={**self.counts, **(counts or {})},
                        offset=offset, **args)


def _shape(tiling: sto_tiling) -> tuple:
    """
    What makes two tilings of an STO the same: extents and register tiles
    """
    return (tuple((i, fmt_dim(e)) for i, e in tiling.extents.items()),
            tuple((o, fmt_dim(t.dima), fmt_dim(t.dimb)) for o, t in tiling.registers.items()))


def fmt_dim(d: dimp) -> str:
    """
    V for a vector length, 2V for two, 4 for four elements
    """
    if dimt.vla == d.dt:
        return "V" if 1 == d.size else f"{d.size}V"
    return str(d.size)


class sto_stage(stage):
    """
    Tiles every STO: its operations over the microtile, in units of what one
    execution of its implementation covers. A store STO tiles its components
    the way the implementation that last wrote them left them.

    --print-stos prints the tilings and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("STO").debug

        self.params["print-stos"] = stage_param(
                value=False,
                default=False,
                description="Print the tiled STOs and exit",
                required=False,
                flag=True)

    def tile_block(self, block, chosen: dict, counts: dict[str, int],
                   left: dict, seen: dict, tilings: dict, label: str = ""):
        """
        Tile one block's STOs: compute STOs with their chosen implementations,
        store STOs the way the implementations before them left what they store
        """
        composition = self.context.composition
        gen = self.context.gen
        order = self.context.order

        for name in block.stos:
            sto = composition.get_sto(name)

            if sto_kind.COMPUTE == sto.kind:
                impl = chosen[name].impl
                found = index_extents(gen, impl)
                extents = {i: found.get(i, ONE) for i in sto.indices}
                tiles = operand_tiles(gen, impl, sto.req)
                lanes = lane_axes(gen, impl, sto.req, self.context.component_layouts)
                registers = register_tiles(tiles, lanes, sto.req)
                operands = sto.operand_indices
                io = {op: sto.io(op) for op in operands}
                opstr = ";".join(part_enc.split("(")[0].split("[")[0]
                                 for part_enc in chosen[name].encoding.split(" ; "))
                generate = generators[sto.generator]
            else:
                operands, tiles, extents = {}, {}, {}
                lanes, opstr = {}, "store"
                for comp in sto.store_components:
                    t, indices = left[comp]
                    operands[comp], tiles[comp] = indices, t
                    live = [i for i in indices if i is not None]
                    extents.update(zip(live, (t.dima, t.dimb)))
                registers = tiles
                io = {comp: (True, False) for comp in operands}
                generate = generate_tiling

            # the microtile has one size: every STO must cover it in the
            # same steps along each index
            for idx, extent in extents.items():
                first = seen.setdefault(idx, (extent, name + label))
                if first[0] != extent:
                    raise stage_error(
                        f"{name}{label} covers {fmt_dim(extent)} along {idx} per operation, "
                        f"but {first[1]} covers {fmt_dim(first[0])}: their tilings "
                        f"of the same microtile would not line up")

            if sto_kind.COMPUTE == sto.kind:
                for op in sto.operands:
                    if sto.io(op)[1]:
                        left[op] = (tiles[op], operands[op])

            sto_order = tuple(i for i in order if i in extents)
            ops = generate(order=sto_order, counts=counts, operands=operands,
                           tiles=registers, io=io, lanes=lanes, opstr=opstr)
            tilings[name] = sto_tiling(sto=name, order=sto_order, extents=extents,
                                       tiles=tiles, ops=ops, registers=registers,
                                       counts=dict(counts),
                                       generate_args=dict(generate=generate,
                                                          operands=operands,
                                                          tiles=registers, io=io,
                                                          lanes=lanes, opstr=opstr))

    def tile_part(self, part: dict, subtail: dict | None = None) \
            -> tuple[dict[str, sto_tiling], dict[str, sto_tiling]]:
        """
        Tile every STO of a part, and the subtail of each loop block whose
        compute STOs all have a subtail implementation: the same block with one
        step along the loop index, lining up with the main tiling along every
        other index - the accumulators it adds to are the same registers

        :return: the tilings and the subtail tilings
        """
        dims = self.context.dims
        seen: dict[str, tuple[dimp, str]] = {}
        left: dict[str, tuple[tile, tuple]] = {}
        tilings: dict[str, sto_tiling] = {}
        subtails: dict[str, sto_tiling] = {}
        composition = self.context.composition

        for block in [b for b in composition.get_blocks() if isinstance(b, block_description)]:
            before = dict(left)
            self.tile_block(block, part, dims, left, seen, tilings)
            computes = [n for n in block.stos
                        if sto_kind.COMPUTE == composition.get_sto(n).kind]
            if block.is_loop and subtail and all(n in subtail for n in computes):
                k = block.loop_index
                self.tile_block(block, subtail, {**dims, k: 1}, before,
                                {i: v for i, v in seen.items() if i != k},
                                subtails, label=" (subtail)")

        # Each case continues from what the blocks before the branch leave. An
        # STO shared by several cases has one implementation, and its tiling
        # must come out the same in each - a store following what different
        # cases leave in registers, say.
        branch = composition.get_branch()
        for case in (branch.cases if branch else ()):
            case_tilings: dict[str, sto_tiling] = {}
            case_left, case_seen = dict(left), dict(seen)
            for block in case.blocks:
                self.tile_block(block, part, dims, case_left, case_seen, case_tilings,
                                label=f" (case {case.label})")
            for name, tiling in case_tilings.items():
                known = tilings.setdefault(name, tiling)
                if _shape(known) != _shape(tiling):
                    raise stage_error(
                        f"{name} is tiled differently in case {case.label} than in an "
                        f"earlier case: the implementations before it leave its operands "
                        f"differently. Give each case its own STO")
        return tilings, subtails

    def render(self, parts: list[dict[str, sto_tiling]]) -> str:
        composition = self.context.composition
        lines = []
        for i, tilings in enumerate(parts):
            if len(parts) > 1:
                lines.append(f"part {i + 1}")
            for name in composition.sto_order():
                if name not in tilings:
                    continue
                t = tilings[name]
                block = composition.block_of(name)
                where = f", inside the loop over {block.loop_index}" if block.is_loop else ""
                ext = " ".join(f"{i}={fmt_dim(e)}" for i, e in t.extents.items())
                tl = "  ".join(f"{o} {fmt_dim(x.dima)}x{fmt_dim(x.dimb)}"
                               for o, x in (t.registers or t.tiles).items())
                lines.append(f"{name}{where}: {len(t.ops)} operations; "
                             f"order {','.join(t.order)}; extents {ext}")
                lines.append(f"  tiles: {tl}")
                lines.extend("  [" + " ".join(f"{i}={p}" for i, p in op.point.items())
                             + f"]  {op}" for op in t.ops)
                lines.append("")
        return "\n".join(lines).rstrip()

    def progress(self):
        if len(self.context.to_parts) > 1:
            raise stage_error(
                "several parts need a partition of the microtile - which index is "
                "split and how far each part reaches - and that is not specified yet")

        subtails = self.context.subtail_parts or [{}] * len(self.context.to_parts)
        results = [self.tile_part(part, sub)
                   for part, sub in zip(self.context.to_parts, subtails)]
        parts = [tilings for tilings, _ in results]
        self.context.stos = parts
        self.context.subtail_stos = [sub for _, sub in results]

        text = self.render(parts)
        if any(self.context.subtail_stos):
            text += "\n\nsubtail\n" + self.render(self.context.subtail_stos)
        if self.params["print-stos"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)

        self.context.params.update(self.params)
        return []
