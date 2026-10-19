"""
Tiling every STO with its chosen implementation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ...components.tile import tile, dimension_properties as dimp, dimension_type as dimt
from ...lsc_model.addressing import sym
from ...components.operation import operation
from ...generators.tiling import generate_tiling, generators
from ...support.tiles import index_extents, kernel_groups, operand_tiles, lane_axes, register_tiles, ONE
from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import sto_kind, block_description


VLA_ONE = dimp(dt=dimt.vla, size=1)


def resident_components(impl) -> set[str]:
    """
    The components an implementation reaches resident in a tile, slice by
    slice
    """
    return {step.name_mapping.get(hw, hw)
            for res, step in zip(impl.resolved_chain, impl.math_chain)
            for (hw, _), strat in res.operand_strategies.items()
            if getattr(strat.rsln, "resident_rtype", None) is not None}


def resident_slice_loop(impl, operands) -> tuple | None:
    """
    Where an implementation reaches an operand resident in a tile slice by
    slice (slice_vec): the index its slices iterate, their axis, and the
    tile's component - columns span the tile's first index, so a loop over
    them walks its second; rows the other way
    """
    for res, step in zip(impl.resolved_chain, impl.math_chain):
        for (hw, _), strat in res.operand_strategies.items():
            if getattr(strat.rsln, "resident_rtype", None) is None:
                continue
            comp = step.name_mapping.get(hw, hw)
            indices = [i for i in operands.get(comp, ()) if i is not None]
            if len(indices) < 2:
                continue
            axis = "col" if strat.rsln.unique_tag.endswith("_col") else "row"
            return (indices[1] if "col" == axis else indices[0], axis, comp)
    return None


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
                groups = kernel_groups([c.impl for c in chosen.values()
                                        if hasattr(getattr(c, "impl", None), "resolved_chain")])
                found = index_extents(gen, impl, groups)
                extents = {i: found.get(i, ONE) for i in sto.indices}
                tiles = operand_tiles(gen, impl, sto.req, groups)
                lanes = lane_axes(gen, impl, sto.req, self.context.component_layouts)
                registers = register_tiles(tiles, lanes, sto.req)
                operands = sto.operand_indices
                # an operand resident in a tile, reached slice by slice through
                # the operation's vectors: the STO covers the tile, looping over
                # its slices along the index they iterate - columns span the
                # tile's first index, so walk its second
                slice_loop = resident_slice_loop(impl, operands)
                if slice_loop is not None:
                    extents[slice_loop[0]] = VLA_ONE
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
                        # a tile reached slice by slice is left as the tile
                        whole = op in resident_components(impl)
                        left[op] = (tile(VLA_ONE, VLA_ONE) if whole else tiles[op], operands[op])

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
            if sto_kind.COMPUTE == sto.kind and slice_loop is not None:
                tilings[name].slice_loop = slice_loop

    def tile_part(self, part: dict, subtail: dict | None = None, dims: dict | None = None) \
            -> tuple[dict[str, sto_tiling], dict[str, sto_tiling]]:
        """
        Tile every STO of a part, and the subtail of each loop block whose
        compute STOs all have a subtail implementation: the same block with one
        step along the loop index, lining up with the main tiling along every
        other index - the accumulators it adds to are the same registers

        :return: the tilings and the subtail tilings
        """
        dims = dims or self.context.dims
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

    def place_parts(self, parts: list[dict], part_dims: list[dict]):
        """
        The parts of a split microtile, one after another along the split
        index: each starts where the one before ends, in elements. Along every
        other index they cover the same elements - and along a loop index they
        step alike: a part covering a vector length of k (a dota) beside one
        covering one would need a nested loop for the finer one
        """
        split = self.context.split_index
        loops = {b.loop_index for b in self.context.composition.all_blocks() if b.is_loop}
        computes = {s.name for s in self.context.composition.get_sto_descriptions()
                    if sto_kind.COMPUTE == s.kind}
        def cover(tilings, dims, idx):
            extents = [t.extents[idx] for name, t in tilings.items()
                       if name in computes and idx in t.extents]
            return dimp(dt=extents[0].dt, size=extents[0].size * dims[idx]) if extents else None
        # where each part starts along the split index, in elements: a sum of
        # constants and vector lengths (2v rows of outer products, then 2 of
        # fmas)
        offset = sym.const(0)
        for p, (tilings, dims) in enumerate(zip(parts, part_dims)):
            for t in tilings.values():
                t.part_offset = {split: offset}
            here = cover(tilings, dims, split)
            if here is None:
                raise stage_error(f"part {p + 1} computes nothing along {split}")
            offset = offset + sym.extent(here)
        indices = sorted({i for tilings in parts for t in tilings.values() for i in t.extents})
        for idx in indices:
            if idx == split:
                continue
            covers = {str(c) for c in (cover(t, d, idx) for t, d in zip(parts, part_dims)) if c is not None}
            if len(covers) > 1:
                how = "step" if idx in loops else "cover"
                raise stage_error(
                    f"the parts {how} {idx} differently ({', '.join(sorted(covers))})" +
                    (": the finer part would need a loop nested in the loop over it - not "
                     "supported yet" if idx in loops else
                     f": along every index but the split one ({split}) the parts cover the "
                     f"same elements"))

    def progress(self):
        subtails = self.context.subtail_parts or [{}] * len(self.context.to_parts)
        part_dims = getattr(self.context, "part_dims", None) or [self.context.dims] * len(self.context.to_parts)
        if len(self.context.to_parts) > 1 and getattr(self.context, "split_index", None) is None:
            raise stage_error("several parts split the microtile along an index: give that "
                              "index one value per part (--m 2 2)")
        results = [self.tile_part(part, sub, dims)
                   for part, sub, dims in zip(self.context.to_parts, subtails, part_dims)]
        parts = [tilings for tilings, _ in results]
        if len(parts) > 1:
            self.place_parts(parts, part_dims)
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
