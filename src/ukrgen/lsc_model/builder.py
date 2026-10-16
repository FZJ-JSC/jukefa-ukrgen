"""
Building LSC IR from tiled STOs and their chosen implementations.

Each STO operation becomes the data movement its implementation's resolutions
describe - loads on demand, skipped when the register already holds the data -
followed by the computation. A loop block emits one iteration once, as access
groups and computations; preloading is a rearrangement of those items, not a
second run with saved and restored state.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from asmgen.asmblocks.op import operand_modifier as omod
from asmgen.registers import adt_size

from ..flow.stages.ukr.ukr import read_access, sto_kind, block_description
from ..matching.math import get_operand_io
from ..support.data_move import (
    dm_direction as dmd,
    orig_ref,
    filter_by_step_requirements,
)
from ..support.dm_solver import repeat_fits
from ..support.sig_group import group_sigs
from .addressing import sym, offset_db, layout_strides, addr_pattern
from .ir import vreg, addr_ref, ir_op, ir_mem, ir_move, ir_compute, ir_zero, ir_block, ir_program


class model_error(Exception):
    """
    The kernel cannot be built as parameterized, e.g. too few data registers
    for an accumulator
    """


@dataclass
class access_group:
    """
    The data movement bringing one operand tile into a register
    """
    component : str
    reg : vreg
    ops : list[ir_op]
    streamed : bool
    coord : tuple = ()


@dataclass
class compute_item:
    op : ir_compute


@dataclass
class addressing_plan:
    """
    How a component's accesses use its address registers

    :param registers: number of address registers
    :param pattern: which register an access uses
    """
    registers : int = 1
    pattern : addr_pattern = field(default_factory=lambda: addr_pattern("rotate"))


class program_builder:
    """
    Builds the IR program of one part of the microtile

    :param ctx: context after the STO stage
    :param part: index of the part
    :param addressing: component -> address register plan
    :param data_regs: component -> data registers to use; components left out
                      get one per distinct tile they need
    :param preload: whether loop blocks preload streamed operands
    """

    def __init__(self, ctx, part: int = 0,
                 addressing: dict[str, addressing_plan] | None = None,
                 data_regs: dict[str, int] | None = None,
                 preload: bool = True):
        self.ctx = ctx
        self.gen = ctx.gen
        self.comp = ctx.composition
        self.part = ctx.to_parts[part]
        self.stos = ctx.stos[part]
        self.flow = self.comp.dataflow()
        self.addressing = addressing or {}
        self.data_regs = data_regs or {}
        self.preload = preload
        self.components = {c.name for c in self.comp.get_components()}

        self.db = offset_db()
        self.extents: dict[str, sym] = {}
        for tiling in self.stos.values():
            for idx, ext in tiling.extents.items():
                self.extents.setdefault(idx, sym.extent(ext) * ctx.dims[idx])
        self.strides = {
            comp: layout_strides(comp, kinds, ctx.component_packing.get(comp, []), self.extents)
            for comp, kinds in ctx.component_strides.items()}

        # register coordinates of each component over all STOs: their rank
        # names the register, and picks the address register
        self.subtails = ctx.subtail_stos[part] if len(ctx.subtail_stos) > part else {}
        self.subtail_impls = ctx.subtail_parts[part] if len(ctx.subtail_parts) > part else {}
        coords: dict[str, set] = {}
        for tiling in list(self.stos.values()) + list(self.subtails.values()):
            for op in tiling.ops:
                for name in op.tile_strs:
                    if name in self.components:
                        coords.setdefault(name, set()).add(op.coord(name))
        self.coords = {c: sorted(s) for c, s in coords.items()}

        self.holder: dict[vreg, tuple] = {}
        self.used: dict[str, tuple] = {}
        self.phases: dict[str, list] = {}
        self.addr_setup: dict[tuple[str, int], int] = {}

    # --- registers ---------------------------------------------------------

    def reg_of(self, comp: str, rtype, coord: tuple) -> vreg:
        """
        The register holding a component's tile: one per distinct tile, or
        cycling through the data registers the user allowed
        """
        rank = self.coords[comp].index(coord)
        ring = self.data_regs.get(comp, len(self.coords[comp]))
        reg = vreg(comp, rtype, rank % ring)
        self._use(reg)
        return reg

    def _use(self, reg: vreg):
        rtype, count = self.used.get(reg.owner, (reg.rtype, 0))
        self.used[reg.owner] = (rtype, max(count, reg.index + 1))

    def ref_reg(self, ref, rtype, final: vreg) -> vreg:
        """
        Register a step reference names: the operand's own register, or scratch
        space between the steps of a data movement
        """
        if isinstance(ref, orig_ref):
            return final
        tag = str(getattr(ref, "tag", "0"))
        reg = vreg("S", rtype, int(tag) if tag.isdigit() else 0)
        self._use(reg)
        return reg

    # --- addresses ---------------------------------------------------------

    def elements(self, tiling, comp: str, coord: tuple) -> dict[str, sym]:
        """
        Element offsets of a component tile: its register coordinate times the
        register tile's extent along each index
        """
        indices = tiling.generate_args["operands"][comp]
        reg_tile = tiling.registers[comp]
        dims = (reg_tile.dima, reg_tile.dimb)
        live = [(pos, idx) for pos, idx in enumerate(indices) if idx is not None]
        return {idx: sym.extent(dims[pos]) * c for (pos, idx), c in zip(live, coord)}

    def address(self, sto: str, comp: str, direction: str, coord: tuple,
                elements: dict[str, sym]) -> addr_ref:
        """
        Register an access and pick its address register. The pick depends
        only on the tile's rank and the access's phase, so it is the same in
        the prologue as in the loop body, and it cannot drift.
        """
        plan = self.addressing.get(comp, addressing_plan())
        phases = self.phases.setdefault(comp, [])
        key = (sto, direction)
        if key not in phases:
            phases.append(key)
        reg = plan.pattern.select(self.coords[comp].index(coord), phases.index(key),
                                  plan.registers)
        oid = self.db.add(comp, elements)
        self.addr_setup.setdefault((comp, reg), oid)
        return addr_ref(component=comp, reg=reg, offset=oid)

    # --- data movement -----------------------------------------------------

    def step_sigs(self, step, dt):
        sigs = filter_by_step_requirements(getattr(self.gen, step.op).get_signatures(), step, dt)
        return group_sigs([s for s in sigs if repeat_fits(self.gen, s, step, dt)])

    def vector_index(self, tiling, comp: str) -> str | None:
        """
        The index a component's register runs along, for lane-by-lane steps
        """
        indices = tiling.generate_args["operands"][comp]
        reg_tile = tiling.registers[comp]
        for pos, idx in enumerate(indices):
            d = (reg_tile.dima, reg_tile.dimb)[pos]
            if idx is not None and not (1 == d.size and "fixed" == d.dt.name):
                return idx
        return None

    def move_data(self, sto: str, tiling, comp: str, coord: tuple, reg: vreg,
                  steps, direction: str, tag: str) -> list[ir_op]:
        """
        The IR of one data movement: its steps in order, a repeated step once per
        lane, each load or store at the tile's address
        """
        dt = self.ctx.component_dts[comp]
        ops: list[ir_op] = []
        for rs in steps:
            step = rs.step
            sigs = getattr(rs, "sg", None) or self.step_sigs(step, dt)
            lanes = [None]
            if step.repeat is not None:
                lanes = list(range(self.gen.simd_size // adt_size(dt)))
            for lane in lanes:
                elements = self.elements(tiling, comp, coord)
                if lane is not None:
                    vidx = self.vector_index(tiling, comp)
                    elements[vidx] = elements.get(vidx, sym()) + lane
                if "load" == step.op:
                    dest = self.ref_reg(step.dest, step.dest_rtype, reg)
                    ops.append(ir_mem("load", dest,
                                      self.address(sto, comp, direction, coord, elements),
                                      tag, step, sigs, lane))
                elif "store" == step.op:
                    src = self.ref_reg(step.src[0], step.src_rtypes[0], reg)
                    ops.append(ir_mem("store", src,
                                      self.address(sto, comp, direction, coord, elements),
                                      tag, step, sigs, lane))
                else:
                    src = self.ref_reg(step.src[0], step.src_rtypes[0], reg)
                    dest = self.ref_reg(step.dest, step.dest_rtype, reg)
                    ops.append(ir_move(src, dest, tag, step, sigs, lane))
        return ops

    # --- STOs ----------------------------------------------------------------

    def emit_compute(self, sto: str, tiling, op, impl=None) -> list:
        """
        One STO operation: each step of the chosen implementation, with the
        data its operands need loaded first unless a register holds it
        """
        impl = impl or self.part[sto].impl
        items: list = []
        temps: dict[str, vreg] = {}
        for res, step in zip(impl.resolved_chain, impl.math_chain):
            sig = res.compute_sg.representative
            regs, lanes, reads, writes = {}, {}, [], []
            written = []
            for hw, math in step.name_mapping.items():
                is_read, is_written = get_operand_io(step.hw_ast, hw)
                rtype = sig.operands[hw].rtype
                if math not in self.components:
                    reg = temps.setdefault(math, vreg(math, rtype, 0))
                    self._use(reg)
                else:
                    coord = op.coord(math)
                    reg = self.reg_of(math, rtype, coord)
                    strat = res.operand_strategies.get((hw, dmd.IN))
                    if is_read and strat is not None and strat.rsln.steps:
                        if self.holder.get(reg) != (math, coord):
                            access = read_access.STREAM == self.flow[(sto, math)].read
                            items.append(access_group(
                                math, reg,
                                self.move_data(sto, tiling, math, coord, reg,
                                               strat.resolved_steps, "load",
                                               strat.rsln.unique_tag),
                                access, coord))
                            self.holder[reg] = (math, coord)
                    elif is_read and self.holder.get(reg) != (math, coord):
                        raise model_error(
                            f"{sto} reads {math}{list(coord)}, which is no longer in "
                            f"{reg}: give {math} more data registers")
                    lane = [l for l in op.lane(math) if l is not None]
                    if lane and omod.ILANE in sig.operands[hw].modifiers:
                        lanes[hw] = lane[0]
                    if is_written:
                        written.append((reg, math, coord))
                regs[hw] = reg
                if is_read:
                    reads.append(hw)
                if is_written:
                    writes.append(hw)
            opname = self.ctx.osb.ast_op_map[step.hw_ast]
            items.append(compute_item(ir_compute(sto, opname, res, regs, lanes,
                                                 tuple(reads), tuple(writes))))
            for reg, math, coord in written:
                self.holder[reg] = (math, coord)
        return items

    def emit_store(self, sto: str, tiling, op) -> list:
        choice = self.part[sto].impl
        items = []
        for cand in choice.stores:
            comp = cand.component
            coord = op.coord(comp)
            reg = self.reg_of(comp, cand.rtype, coord)
            if self.holder.get(reg) != (comp, coord):
                raise model_error(f"{sto} stores {comp}{list(coord)}, which is no longer "
                                  f"in {reg}: give {comp} more data registers")
            steps = [_step(s) for s in cand.rsln.steps]
            items.append(access_group(comp, reg,
                                      self.move_data(sto, tiling, comp, coord, reg, steps,
                                                     "store", cand.rsln.unique_tag), False))
        return items

    def emit_sto(self, sto: str, ops, tiling=None, impl=None) -> list:
        tiling = tiling or self.stos[sto]
        kind = self.comp.get_sto(sto).kind
        items = []
        for op in ops:
            items += self.emit_compute(sto, tiling, op, impl) if sto_kind.COMPUTE == kind \
                else self.emit_store(sto, tiling, op)
        return items

    def forget(self, components):
        """
        Registers of these components hold nothing usable any more: what a loop
        streamed through them belongs to another iteration
        """
        for reg in [r for r, (c, _) in self.holder.items() if c in components]:
            del self.holder[reg]

    # --- blocks ----------------------------------------------------------------

    def zero_accumulators(self, block: block_description) -> list[ir_op]:
        from ..flow.stages.solve import produced_rtype
        ops = []
        for sto in block.stos:
            for acc in sorted(self.comp.accumulators(sto)):
                if read_access.ZERO != self.flow[(sto, acc)].read:
                    continue
                rtype = produced_rtype(self.part[sto].impl, acc)
                for coord in self.coords[acc]:
                    reg = self.reg_of(acc, rtype, coord)
                    if self.holder.get(reg) != (acc, coord):
                        ops.append(ir_zero(reg))
                        self.holder[reg] = (acc, coord)
        if any(self.data_regs.get(a, len(self.coords[a])) < len(self.coords[a])
               for sto in block.stos for a in self.comp.accumulators(sto)):
            raise model_error("an accumulator needs a register for every tile it "
                              "accumulates: it has fewer data registers than tiles")
        return ops

    def build_loop(self, block: block_description) -> ir_block:
        k = block.loop_index
        # The size given for the loop index (--k for gemm) counts operations
        # along it per iteration: the unroll. An iteration covers that many
        # times one operation's extent along the loop index.
        extent = sym.extent(self.stos[block.stos[0]].extents[k])
        iteration = extent * self.ctx.dims[k]
        out = ir_block(name="+".join(block.stos), loop_index=k, step=iteration,
                       unroll=self.ctx.dims[k])
        out.prologue = self.zero_accumulators(block)

        streamed = {c for sto in block.stos for c in self.comp.get_sto(sto).operands
                    if read_access.STREAM == self.flow[(sto, c)].read}
        items = []
        for sto in block.stos:
            items += self.emit_sto(sto, self.stos[sto].ops)

        for comp in sorted(streamed):
            out.advance[comp] = self.db.add(comp, {k: iteration})

        if not (self.preload and block.preload):
            out.body = _flatten(items)
        else:
            # The prologue loads the first iteration's streamed data. The body
            # then loads the next iteration's into each register as soon as
            # this iteration has last read it; the epilogue is the last
            # iteration, loading nothing ahead.
            last_read: dict[vreg, int] = {}
            for pos, item in enumerate(items):
                if isinstance(item, compute_item):
                    for hw in item.op.reads:
                        last_read[item.op.regs[hw]] = pos
            #
            # That needs each register to hold one tile per iteration. A
            # component given fewer data registers than tiles reuses them
            # within the iteration, so its loads stay where they are.
            tiles: dict[str, set] = {}
            for item in items:
                if isinstance(item, access_group) and item.streamed:
                    tiles.setdefault(item.component, set()).add(item.coord)
            hoisted = {c for c, t in tiles.items()
                       if self.data_regs.get(c, len(self.coords[c])) >= len(t)}

            def preloaded(item):
                return isinstance(item, access_group) and item.streamed \
                    and item.component in hoisted

            ahead: dict[int, list[access_group]] = {}
            for item in items:
                if preloaded(item):
                    out.prologue += item.ops
                    ahead.setdefault(last_read.get(item.reg, len(items) - 1), []).append(item)
            for pos, item in enumerate(items):
                if preloaded(item):
                    continue
                ops = _flatten([item])
                out.body += ops
                out.epilogue += ops
                for group in ahead.get(pos, []):
                    out.body += [self.shifted(op, k, iteration) for op in group.ops]

        # The tail runs the main implementation one operation at a time along
        # the loop index, for what the unrolled loop leaves over. With an
        # unroll of 1 the loop itself steps by one operation.
        if block.tail and out.unroll > 1:
            self.forget(streamed)
            items = []
            for sto in block.stos:
                items += self.emit_sto(sto, self.stos[sto].regenerate(counts={k: 1}))
            out.tail = _flatten(items)
            out.tail_step = extent

        # What is shorter than one operation needs the subtail: another
        # implementation covering one element along the loop index. Without
        # one, the loop count must be a multiple of an operation's extent.
        if extent != sym.const(1):
            if all(sto in self.subtails for sto in block.stos):
                self.forget(streamed)
                items = []
                for sto in block.stos:
                    items += self.emit_sto(sto, self.subtails[sto].ops,
                                           tiling=self.subtails[sto],
                                           impl=self.subtail_impls.get(sto, None)
                                           and self.subtail_impls[sto].impl)
                out.subtail = _flatten(items)
                out.subtail_step = sym.const(1)
            else:
                out.requires_multiple = extent
        return out

    def shifted(self, op: ir_op, index: str, amount: sym) -> ir_op:
        """
        The same access one loop iteration later
        """
        if not isinstance(op, ir_mem):
            return op
        addr = addr_ref(op.addr.component, op.addr.reg,
                        self.db.shifted(op.addr.offset, index, amount))
        return ir_mem(op.kind, op.reg, addr, op.resolution, op.step, op.sigs, op.lane)

    def build(self) -> ir_program:
        blocks = []
        for block in self.comp.get_blocks():
            if block.is_loop:
                blocks.append(self.build_loop(block))
            else:
                items = []
                for sto in block.stos:
                    items += self.emit_sto(sto, self.stos[sto].ops)
                blocks.append(ir_block(name="+".join(block.stos), body=_flatten(items)))
        return ir_program(blocks=blocks, offsets=self.db, strides=self.strides,
                          addr_setup=self.addr_setup, registers=dict(self.used))


@dataclass
class _step:
    """
    A store resolution's step; its signatures are looked up when it is emitted
    """
    step : object
    sg : object = None


def _flatten(items: list) -> list[ir_op]:
    ops = []
    for item in items:
        ops += item.ops if isinstance(item, access_group) else [item.op]
    return ops
