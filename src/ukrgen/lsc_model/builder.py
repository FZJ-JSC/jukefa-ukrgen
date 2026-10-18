"""
Building LSC IR from tiled STOs and their chosen implementations.

Each STO operation becomes the data movement its implementation's resolutions
describe - loads on demand, skipped when the register already holds the data -
followed by the computation. A loop block emits one iteration once, as access
groups and computations; preloading is a rearrangement of those items, not a
second run with saved and restored state.
"""

from __future__ import annotations

import copy

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
from ..components.tile import scalar_tile
from ..models.load_store_operations import (
    lsc_operation, lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, ldst_modifier)
from ..models.lsc.index import lsc_reg_index
from .ir import vreg, addr_ref, ir_block, ir_case, ir_program


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
    ops : list[lsc_operation]
    streamed : bool
    coord : tuple = ()


@dataclass
class compute_item:
    op : lsc_transformation
    reads : list = field(default_factory=list)


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
    :param resolve_order: components in the order an operation loads them
    """

    def __init__(self, ctx, part: int = 0,
                 addressing: dict[str, addressing_plan] | None = None,
                 data_regs: dict[str, int] | None = None,
                 preload: bool = True,
                 resolve_order: list[str] | None = None):
        self.vidx: dict[str, str] = {}
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

        self.subtails = ctx.subtail_stos[part] if len(ctx.subtail_stos) > part else {}
        self.subtail_impls = ctx.subtail_parts[part] if len(ctx.subtail_parts) > part else {}

        # Register coordinates of each component in the order the STOs first
        # use them: the rank names the register and picks the address
        # register. A component cycling through fewer registers than tiles
        # then spreads consecutive tiles over all of them, rather than
        # crowding the tiles of one loop step into a few - sorted coordinates
        # would interleave the loop index.
        coords: dict[str, list] = {}
        order = [n for n in self.comp.sto_order() if n in self.stos]
        for tiling in [self.stos[n] for n in order] + list(self.subtails.values()):
            for op in tiling.ops:
                for name in op.tile_strs:
                    if name in self.components:
                        seen = coords.setdefault(name, [])
                        if op.coord(name) not in seen:
                            seen.append(op.coord(name))
        self.coords = coords

        # the order an operation's components get their data in: which
        # component's memory is touched first
        self.resolve_order = resolve_order or [c.name for c in self.comp.get_components()]

        self.holder: dict[vreg, tuple] = {}
        # for registers loaded lane by lane: (register, lane) -> what it holds
        self.lane_holder: dict[tuple, tuple] = {}
        self.future: list[dict] = []
        self.pos = 0
        self.clock = 0
        self.last_access: dict[vreg, int] = {}
        self.used: dict[str, tuple] = {}
        self.phases: dict[str, list] = {}
        self.addr_setup: dict[tuple[str, int], int] = {}

    # --- registers ---------------------------------------------------------

    def reg_of(self, comp: str, rtype, coord: tuple) -> vreg:
        """
        The register for a component's tile. A tile still held keeps its
        register. With a register per tile, each tile has its own, in order of
        first use. With fewer, new data goes to a free register, else to one
        holding data not needed again in this section - the one accessed
        longest ago, so a reload lands far from its last reads - else to the
        one holding data needed furthest ahead. That loads as rarely as the
        registers allow.
        """
        for reg, held in self.holder.items():
            if reg.owner == comp and reg.rtype == rtype and held == (comp, coord):
                return self._touch(reg)
        ring = self.data_regs.get(comp, len(self.coords[comp]))
        if ring >= len(self.coords[comp]):
            return self._touch(vreg(comp, rtype, self.coords[comp].index(coord)))

        regs = [vreg(comp, rtype, i) for i in range(ring)]
        free = [r for r in regs if r not in self.holder]
        if free:
            return self._touch(free[0])
        upcoming = {r: self.next_use(*self.holder[r]) for r in regs}
        dead = [r for r in regs if upcoming[r] is None]
        if dead:
            return self._touch(min(dead, key=lambda r: self.last_access.get(r, -1)))
        return self._touch(max(regs, key=lambda r: upcoming[r]))

    def _touch(self, reg: vreg) -> vreg:
        self.clock += 1
        self.last_access[reg] = self.clock
        self._use(reg)
        return reg

    def next_use(self, comp: str, coord: tuple) -> int | None:
        """
        How many operations ahead of the current one a tile is needed again in
        this section; None if it is not
        """
        for ahead, needs in enumerate(self.future[self.pos + 1:], start=1):
            if needs.get(comp) == coord:
                return ahead
        return None

    def begin_section(self, stos_ops: list[tuple[str, list]]):
        """
        Start emitting a run of operations - a loop iteration, a tail, a block -
        whose tile accesses decide which registers to reuse
        """
        self.future = [{c: op.coord(c) for c in op.tile_strs if c in self.components}
                       for _, ops in stos_ops for op in ops]
        self.pos = 0

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

    def reg_tile(self, tiling, reg: vreg):
        """
        Tile a register holds: its component's register tile, a scalar for
        scratch space
        """
        return tiling.registers.get(reg.owner, scalar_tile)

    def move_data(self, sto: str, tiling, comp: str, coord: tuple, reg: vreg,
                  steps, direction: str, tag: str,
                  memory: str | None = None, lane: int | None = None) -> list[lsc_operation]:
        """
        The operations of one data movement: its steps in order, a repeated
        step once per lane, each load or store at the tile's address - in
        comp's own memory, or the memory a store writes it into
        """
        memory = memory or comp
        dt = self.ctx.component_dts[memory]
        self.vidx.setdefault(memory, self.vector_index(tiling, comp))
        repeats = [getattr(rs.step, "repeat", None) for rs in steps]
        if any(r is not None and (r.per_block or r.block_operand) for r in repeats):
            return self.move_blocks(sto, tiling, comp, coord, reg, steps, direction, tag,
                                    memory, dt)
        ops: list[lsc_operation] = []
        for rs in steps:
            step = rs.step
            sigs = getattr(rs, "sg", None) or self.step_sigs(step, dt)
            lanes = [lane]
            if step.repeat is not None:
                lanes = list(range(self.gen.simd_size // adt_size(dt)))
            for lane in lanes:
                elements = self.elements(tiling, comp, coord)
                if lane is not None:
                    vidx = self.vector_index(tiling, comp)
                    elements[vidx] = elements.get(vidx, sym()) + lane
                if step.op in ("load", "store"):
                    data = self.ref_reg(step.dest, step.dest_rtype, reg) if "load" == step.op \
                        else self.ref_reg(step.src[0], step.src_rtypes[0], reg)
                    addr = self.address(sto, memory, direction, coord, elements)
                    mods = set()
                    if lane is not None:
                        mods.add(ldst_modifier.lane)
                    if "bc_load" == tag:
                        mods.add(ldst_modifier.bcast1)
                    cls = lsc_load if "load" == step.op else lsc_store
                    op = cls(memory, data.index, addr.reg, None, None,
                             self.reg_tile(tiling, data), mods,
                             data=_index(data, lane), rsln=tag, step=step, sigs=sigs,
                             offset=addr.offset, rtypes=[None, data.rtype])
                    if lane is None and any("ILANE" == m.name
                                            for mods in (step.opd_mod_reqs or {}).values()
                                            for m in mods):
                        # one element into one lane (bc_lane): lane 0
                        lane = 0
                    if lane is not None:
                        op.add_property("lane", lane)
                        op.add_property("stride_index", self.vector_index(tiling, comp))
                    if {"GSTRIDE", "VINDEX"} & {m.name for m in (step.op_mod_reqs or set())}:
                        # a strided access or a gather: its stride is the
                        # component's along the register's index
                        op.add_property("stride_index", self.vector_index(tiling, comp))
                    ops.append(op)
                else:
                    src = self.ref_reg(step.src[0], step.src_rtypes[0], reg)
                    dest = self.ref_reg(step.dest, step.dest_rtype, reg)
                    op = lsc_move(_index(src), _index(dest),
                                  [self.reg_tile(tiling, src), self.reg_tile(tiling, dest)],
                                  rsln=tag, step=step, sigs=sigs,
                                  rtypes=[src.rtype, dest.rtype])
                    if any("ILANE" == m.name for mods in (step.opd_mod_reqs or {}).values()
                           for m in mods):
                        # a move from or into one lane: the lane the element is in
                        op.add_property("lane", 0 if lane is None else lane)
                    ops.append(op)
        return ops

    def move_blocks(self, sto, tiling, comp, coord, reg, steps, direction, tag, memory, dt):
        """
        A vector moved block by block. Per 128-bit block: its lanes loaded into
        a scratch in increasing order, or stored from one, and the moves of
        128-bit blocks; per chunk of the largest block size (256 bits on
        AVX-512), the moves of those chunks
        """
        ops: list[lsc_operation] = []
        block_lanes = 16 // adt_size(dt)
        vidx = self.vector_index(tiling, comp)
        sizes = {rs.step.repeat.block_bytes for rs in steps
                 if rs.step.repeat is not None and rs.step.repeat.block_operand}
        top = max(sizes | {16})
        per_chunk = top // 16
        inner = [rs for rs in steps if rs.step.repeat is None or rs.step.repeat.per_block
                 or 16 == rs.step.repeat.block_bytes]
        outer = [rs for rs in steps if not any(rs is r for r in inner)]

        def move(rs, index):
            step = rs.step
            sigs = getattr(rs, "sg", None) or self.step_sigs(step, dt)
            src = self.ref_reg(step.src[0], step.src_rtypes[0], reg)
            dest = self.ref_reg(step.dest, step.dest_rtype, reg)
            op = lsc_move(_index(src), _index(dest),
                          [self.reg_tile(tiling, src), self.reg_tile(tiling, dest)],
                          rsln=tag, step=step, sigs=sigs, rtypes=[src.rtype, dest.rtype])
            op.add_property("block", index)
            ops.append(op)

        for chunk in range(self.gen.simd_size // top):
            for sub in range(per_chunk):
                block = chunk * per_chunk + sub
                for rs in inner:
                    step = rs.step
                    if step.repeat is None or not step.repeat.per_block:
                        # a 128-bit block: within its chunk where chunks are larger
                        move(rs, sub if top > 16 else block)
                        continue
                    sigs = getattr(rs, "sg", None) or self.step_sigs(step, dt)
                    for lane in range(block_lanes):
                        elements = self.elements(tiling, comp, coord)
                        elements[vidx] = elements.get(vidx, sym()) + block * block_lanes + lane
                        addr = self.address(sto, memory, direction, coord, elements)
                        if "load" == step.op:
                            data = self.ref_reg(step.dest, step.dest_rtype, reg)
                            cls = lsc_load
                        else:
                            data = self.ref_reg(step.src[0], step.src_rtypes[0], reg)
                            cls = lsc_store
                        op = cls(memory, data.index, addr.reg, None, None,
                                 self.reg_tile(tiling, data), {ldst_modifier.lane},
                                 data=_index(data, lane), rsln=tag, step=step, sigs=sigs,
                                 offset=addr.offset, rtypes=[None, data.rtype])
                        op.add_property("lane", lane)
                        op.add_property("stride_index", vidx)
                        ops.append(op)
            for rs in outer:
                move(rs, chunk)
        return ops

    # --- STOs ----------------------------------------------------------------

    def emit_compute(self, sto: str, tiling, op, impl=None) -> list:
        """
        One STO operation: each step of the chosen implementation, with the
        data its operands need loaded first unless a register holds it
        """
        impl = impl or self.part[sto].impl
        last = impl.math_chain[-1]
        result = last.name_mapping.get(last.hw_ast.left.name)
        result_tile = tiling.registers.get(result, scalar_tile)

        items: list = []
        temps: dict[str, vreg] = {}
        for res, step in zip(impl.resolved_chain, impl.math_chain):
            sig = res.compute_sg.representative
            loads: list[access_group] = []
            hws, indices, tiles, reads, writes, read_regs = [], [], [], [], [], []
            written = []
            for pos, (hw, math) in enumerate(step.name_mapping.items()):
                is_read, is_written = get_operand_io(step.hw_ast, hw)
                rtype = sig.operands[hw].rtype
                lane = None
                if math not in self.components:
                    reg = temps.setdefault(math, vreg(math, rtype, 0))
                    self._use(reg)
                    tile = result_tile
                else:
                    coord = op.coord(math)
                    reg = self.reg_of(math, rtype, coord)
                    tile = tiling.registers[math]
                    strat = res.operand_strategies.get((hw, dmd.IN))
                    by_lane = [l for l in op.lane(math) if l is not None]
                    if is_read and strat is not None and strat.rsln.steps and by_lane \
                            and _lane_steps(strat.rsln.steps):
                        # loaded lane by lane: each element into the lane the
                        # operation uses it from
                        if self.lane_holder.get((reg, by_lane[0])) != (math, coord):
                            access = read_access.STREAM == self.flow[(sto, math)].read
                            loads.append(access_group(
                                math, reg,
                                self.move_data(sto, tiling, math, coord, reg,
                                               strat.resolved_steps, "load",
                                               strat.rsln.unique_tag, lane=by_lane[0]),
                                access, coord))
                            self.lane_holder[(reg, by_lane[0])] = (math, coord)
                        self.holder[reg] = (math, coord)
                    elif is_read and strat is not None and strat.rsln.steps:
                        if self.holder.get(reg) != (math, coord):
                            access = read_access.STREAM == self.flow[(sto, math)].read
                            loads.append(access_group(
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
                    lanes = [l for l in op.lane(math) if l is not None]
                    if lanes and {omod.ILANE, omod.BLOCKLANE} & sig.operands[hw].modifiers:
                        lane = lanes[0]
                    if is_written:
                        written.append((reg, math, coord))
                hws.append(hw)
                indices.append(_index(reg, lane))
                tiles.append(tile)
                if is_read:
                    reads.append(pos)
                    read_regs.append(reg)
                if is_written:
                    writes.append(pos)
            rank = {c: i for i, c in enumerate(self.resolve_order)}
            items += sorted(loads, key=lambda g: rank.get(g.component, len(rank)))
            opname = self.ctx.osb.ast_op_map[step.hw_ast]
            items.append(compute_item(
                lsc_transformation(opname, indices, tiles, reads, writes,
                                   resolution=res, hw_operands=hws,
                                   rtypes=[sig.operands[hw].rtype for hw in hws]),
                read_regs))
            for reg, math, coord in written:
                self.holder[reg] = (math, coord)
                for key in [k for k in self.lane_holder if k[0] == reg]:
                    del self.lane_holder[key]
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
            memory = self.comp.get_sto(sto).memory_of(comp)
            items.append(access_group(comp, reg,
                                      self.move_data(sto, tiling, comp, coord, reg, steps,
                                                     "store", cand.rsln.unique_tag, memory),
                                      False))
        return items

    def emit_sto(self, sto: str, ops, tiling=None, impl=None) -> list:
        tiling = tiling or self.stos[sto]
        kind = self.comp.get_sto(sto).kind
        items = []
        for op in ops:
            items += self.emit_compute(sto, tiling, op, impl) if sto_kind.COMPUTE == kind \
                else self.emit_store(sto, tiling, op)
            self.pos += 1
        return items

    def emit_section(self, parts: list[tuple]) -> list:
        """
        Emit STOs' operations as one section: (sto, ops, tiling, impl) each
        """
        self.begin_section([(sto, ops) for sto, ops, _, _ in parts])
        items = []
        for sto, ops, tiling, impl in parts:
            items += self.emit_sto(sto, ops, tiling, impl)
        return items

    def forget(self, components):
        """
        Registers of these components hold nothing usable any more: what a loop
        streamed through them belongs to another iteration
        """
        for reg in [r for r, (c, _) in self.holder.items() if c in components]:
            del self.holder[reg]
        for key in [k for k, (c, _) in self.lane_holder.items() if c in components]:
            del self.lane_holder[key]

    # --- blocks ----------------------------------------------------------------

    def zero_accumulators(self, block: block_description) -> list[lsc_operation]:
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
                        ops.append(lsc_zero(reg.owner, reg.index,
                                            self.stos[sto].registers[acc],
                                            rtypes=[reg.rtype]))
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
        items = self.emit_section([(sto, self.stos[sto].ops, None, None) for sto in block.stos])

        # what the loop stores along its index moves with it too (a packing
        # kernel's buffer); only what it reads did
        stored = {c for sto in block.stos
                  for c in (getattr(self.comp.get_sto(sto), "store_components", None) or ())
                  if k in self.strides.get(c, {})}
        for comp in sorted(streamed | stored):
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
                    for reg in item.reads:
                        last_read[reg] = pos
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
                # its own copies: the schedulers rename registers in place
                out.epilogue += [_clone(o) for o in ops]
                for group in ahead.get(pos, []):
                    out.body += [self.shifted(op, k, iteration) for op in group.ops]

        # The tail runs the main implementation one operation at a time along
        # the loop index, for what the unrolled loop leaves over. With an
        # unroll of 1 the loop itself steps by one operation.
        if block.tail and out.unroll > 1:
            self.forget(streamed)
            items = self.emit_section([(sto, self.stos[sto].regenerate(counts={k: 1}), None, None)
                                       for sto in block.stos])
            out.tail = _flatten(items)
            out.tail_step = extent

        # What is shorter than one operation needs the subtail: another
        # implementation covering one element along the loop index. Without
        # one, the loop count must be a multiple of an operation's extent.
        if extent != sym.const(1):
            if all(sto in self.subtails for sto in block.stos):
                self.forget(streamed)
                items = self.emit_section([
                    (sto, self.subtails[sto].ops, self.subtails[sto],
                     self.subtail_impls.get(sto, None) and self.subtail_impls[sto].impl)
                    for sto in block.stos])
                out.subtail = _flatten(items)
                out.subtail_step = sym.const(1)
            else:
                out.requires_multiple = extent
        return out

    def shifted(self, op: lsc_operation, index: str, amount: sym) -> lsc_operation:
        """
        The same operation one loop iteration later: a copy, with a load or
        store's address moved along the loop index
        """
        new = _clone(op)
        if isinstance(op, (lsc_load, lsc_store)):
            new.offset = self.db.shifted(op.offset, index, amount)
        return new

    def build_block(self, block: block_description) -> ir_block:
        if block.is_loop:
            return self.build_loop(block)
        items = self.emit_section([(sto, self.stos[sto].ops, None, None) for sto in block.stos])
        return ir_block(name="+".join(block.stos), body=_flatten(items))

    def build(self) -> ir_program:
        blocks = [self.build_block(b) for b in self.comp.get_blocks()
                  if isinstance(b, block_description)]

        # Every case starts from the registers the blocks before the branch
        # leave, and numbers its address phases afresh: C's loads take the same
        # address register in every case, and so do its stores.
        cases = []
        branch = self.comp.get_branch()
        if branch is not None:
            holder, phases = dict(self.holder), {c: list(p) for c, p in self.phases.items()}
            for case in branch.cases:
                self.holder = dict(holder)
                self.phases = {c: list(p) for c, p in phases.items()}
                cases.append(ir_case(label=case.label, when=dict(case.when),
                                     blocks=[self.build_block(b) for b in case.blocks]))

        return ir_program(blocks=blocks, offsets=self.db, strides=self.strides,
                          addr_setup=self.addr_setup, registers=dict(self.used),
                          cases=cases, vector_indices=dict(self.vidx))

@dataclass
class _step:
    """
    A store resolution's step; its signatures are looked up when it is emitted
    """
    step : object
    sg : object = None


def _lane_steps(steps) -> bool:
    """
    Whether a data movement loads into a single lane of its register
    """
    return any(omod.ILANE in mods for step in steps
               for mods in (getattr(step, "opd_mod_reqs", None) or {}).values())


def _index(reg: vreg, lane: int | None = None) -> lsc_reg_index:
    """
    The LSC register index of a virtual register; a lane is a second index
    """
    return lsc_reg_index(reg.owner, [reg.index] + ([lane] if lane is not None else []))


def _clone(op: lsc_operation) -> lsc_operation:
    """
    A copy owning its register indices and lists: the MRU renames registers by
    rewriting op.indices in place, and widening rewrites the indices
    themselves, so operations must not share them
    """
    new = copy.copy(op)
    new.indices = [lsc_reg_index(i.component, list(i.indices)) for i in op.indices]
    new.tiles = list(op.tiles)
    new.reads = list(op.reads)
    new.writes = list(op.writes)
    new.reg_types = list(op.reg_types)
    new.properties = dict(op.properties)
    if hasattr(op, "mods"):
        new.mods = copy.copy(op.mods)
    return new


def _flatten(items: list) -> list[lsc_operation]:
    ops = []
    for item in items:
        ops += item.ops if isinstance(item, access_group) else [item.op]
    return ops
