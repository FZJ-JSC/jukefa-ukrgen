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
from .ukr.ukr import sto_kind


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

    def tile_part(self, part: dict) -> dict[str, sto_tiling]:
        composition = self.context.composition
        gen = self.context.gen
        dims, order = self.context.dims, self.context.order

        seen: dict[str, tuple[dimp, str]] = {}
        left: dict[str, tuple[tile, tuple]] = {}
        tilings: dict[str, sto_tiling] = {}

        for block in composition.get_blocks():
            for name in block.stos:
                sto = composition.get_sto(name)

                if sto_kind.COMPUTE == sto.kind:
                    impl = part[name].impl
                    found = index_extents(gen, impl)
                    extents = {i: found.get(i, ONE) for i in sto.indices}
                    tiles = operand_tiles(gen, impl, sto.req)
                    lanes = lane_axes(gen, impl, sto.req, self.context.component_layouts)
                    registers = register_tiles(tiles, lanes, sto.req)
                    operands = sto.operand_indices
                    io = {op: sto.io(op) for op in operands}
                    opstr = ";".join(part_enc.split("(")[0].split("[")[0]
                                     for part_enc in part[name].encoding.split(" ; "))
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
                    first = seen.setdefault(idx, (extent, name))
                    if first[0] != extent:
                        raise stage_error(
                            f"{name} covers {fmt_dim(extent)} along {idx} per operation, "
                            f"but {first[1]} covers {fmt_dim(first[0])}: their tilings "
                            f"of the same microtile would not line up")

                if sto_kind.COMPUTE == sto.kind:
                    for op in sto.operands:
                        if sto.io(op)[1]:
                            left[op] = (tiles[op], operands[op])

                sto_order = tuple(i for i in order if i in extents)
                ops = generate(order=sto_order, counts=dims, operands=operands,
                               tiles=registers, io=io, lanes=lanes, opstr=opstr)
                tilings[name] = sto_tiling(sto=name, order=sto_order, extents=extents,
                                           tiles=tiles, ops=ops, registers=registers,
                                           counts=dict(dims),
                                           generate_args=dict(generate=generate,
                                                              operands=operands,
                                                              tiles=registers, io=io,
                                                              lanes=lanes, opstr=opstr))
        return tilings

    def render(self, parts: list[dict[str, sto_tiling]]) -> str:
        composition = self.context.composition
        lines = []
        for i, tilings in enumerate(parts):
            if len(parts) > 1:
                lines.append(f"part {i + 1}")
            for block in composition.get_blocks():
                for name in block.stos:
                    t = tilings[name]
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

        parts = [self.tile_part(part) for part in self.context.to_parts]
        self.context.stos = parts

        text = self.render(parts)
        if self.params["print-stos"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)

        self.context.params.update(self.params)
        return []
