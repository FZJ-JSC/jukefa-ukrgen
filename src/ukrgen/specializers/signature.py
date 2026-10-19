"""
Specializing LSC IR for the ISA, and emitting it, through operation signatures.

Every operation the model emits carries the signatures its instruction can
come from. Specializing (IR to IR) makes each operation fit one of them: an
access at an offset no addressing form takes, or offset by run-time strides,
gets an explicit address computation inserted before it. The result is still
LSC IR, for the irmod, MRU and scheduling stages.

Emitting (IR to assembly, codegen's part) picks for each operation the
signature that fits and calls asmgen with its modifiers and operands; asmgen
checks the call against its signatures again.

Neither knows which microkernel it works on: registers, data types, strides
and offsets all come from the program and the composition metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from asmgen.asmblocks.op.constraint import ArgumentDependencyError
from asmgen.callconv.fngen import fngen
from ..support.domains import operand_values
from ..support.data_move import operand_side
from ..support.tiles import widening_ways
from asmgen.asmblocks.noarch import comparison
from asmgen.asmblocks.op import (
    register_type as rgt,
    operand_role as orl,
    operand_type as ot,
    opmem_modifier as memmod,
)
from asmgen.registers import reg_tracker, adt_size
from asmgen.asmblocks.op.constraint import ConstraintDoesNotApplyError

from ..lsc_model.addressing import sym
from ..lsc_model.ir import ir_program, ir_block
from ..components.tile import scalar_tile
from ..models.load_store_operations import (
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute, lsc_loop)
from ..models.lsc.index import lsc_reg_index


class specialization_error(Exception):
    """
    An operation fits none of its signatures as specialized
    """


def _sigs(groups) -> list:
    """
    The signatures in a signature group, or in a list of groups
    """
    if groups is None:
        return []
    if isinstance(groups, list):
        return [s for g in groups for s in _sigs(g)]
    for attr in ("sigs", "members", "signatures"):
        if hasattr(groups, attr):
            return list(getattr(groups, attr))
    # a signature group's representative, or a signature itself
    return [getattr(groups, "representative", groups)]


def _masked(sig) -> bool:
    return any(orl.MASK == o.orole for o in sig.operands.values())


def _offset_forms(sig) -> str | None:
    """
    "plain" for a signature without an offset, "ioffset" for one taking an
    immediate offset, None for other addressing forms
    """
    # a structure load or store is addressed like a plain one
    mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
    if not mods or ({"GSTRIDE"} == mods and "streg" in sig.operands) \
            or ({"VINDEX"} == mods and "vidxreg" in sig.operands):
        # a strided access or a gather is addressed plainly; its stride or
        # index vector is bound when emitted
        return "plain"
    if {"IOFFSET"} == mods and "ioffset" in sig.operands:
        return "ioffset"
    return None


def _accepts(sig, name: str, value) -> bool:
    """
    Whether a signature's operand takes a value: each of its constraints is
    asked, a ValueError meaning no; constraints that don't apply are skipped
    """
    shape = sig.operands.get(name)
    if shape is None:
        return False
    for constraint in shape.value_constraints:
        try:
            constraint(name, set(sig.modifiers), value, {})
        except (ConstraintDoesNotApplyError, ArgumentDependencyError):
            # doesn't apply, or depends on another operand: for when every
            # operand is known
            continue
        except ValueError:
            return False
    return True


def _all_true(ctx, rt=None):
    """
    The ISA's all-true governing predicate for masked signatures, set up by
    its isa_setup() - and reserved and aliased in the register tracker, when
    one is given. Only where predication is explicit (SVE, SME): with RVV's
    implicit vector length a mask is something else, v0. None where there is
    none.
    """
    factory = getattr(ctx.gen, "isa_setup", None)
    if factory is None:
        return None
    setup = factory()
    kind = getattr(setup, "predication", None)
    if kind is not None and "EXPLICIT" != kind().name:
        return None
    return setup.all_true_predicate(rt=rt, dt=None)


def _usable(ctx, sig) -> bool:
    """
    Unmasked signatures always; masked ones where the ISA sets up an all-true
    predicate to govern them, or where the mask is one the instruction clears
    (its signature's clobber_list) and the generator can set it all-true again
    before each use - AVX gathers and scatters
    """
    if not _masked(sig) or _all_true(ctx) is not None:
        return True
    masks = [n for n, o in sig.operands.items() if orl.MASK == o.orole]
    clobbered = set(getattr(sig, "clobber_list", None) or [])
    return set(masks) <= clobbered and hasattr(ctx.gen, "mask_all_true")


def _vl_form(sig) -> bool:
    """
    A load or store signature taking an offset in vector lengths: [x, #n, MUL VL]
    """
    return {m.name for m in sig.modifiers} - {"MASK"} == {"VOFFSET"} and "voffset" in sig.operands


def _takes(sig, immediate: int) -> bool:
    """
    Whether a load or store signature takes an access at this immediate offset
    """
    form = _offset_forms(sig)
    if "plain" == form:
        return 0 == immediate
    if "ioffset" == form:
        return _accepts(sig, "ioffset", immediate)
    return False


#: column pointers kept per component and base; columns beyond them share
#: one walking pointer
MAX_COLUMN_POINTERS = 4


class signature_specializer:
    """
    Adapts one part's IR program to the ISA, in place: after it, every
    operation fits one of its signatures as it stands.

    - an access offset by run-time strides goes through a column pointer: an
      address register computed once per section from the access's address
      register and the strides
    - an access at a constant offset no signature takes (NEON's ld1r has no
      immediate form) goes through a scratch address register set right before
      it - which an irmod can fuse into a post-increment form

    :raises specialization_error: for what is not specialized yet, e.g. the
                                  governing predicates of SVE and RVV
    """

    def __init__(self, ctx, program: ir_program):
        self.ctx = ctx
        self.program = program
        self.positions: dict[tuple[str, int], sym] = {
            (comp, reg): program.offsets.elements_offset(oid, program.strides.get(comp, {}))
            for (comp, reg), oid in program.addr_setup.items()}
        self.next_reg: dict[str, int] = {}
        for comp, reg in self.positions:
            self.next_reg[comp] = max(self.next_reg.get(comp, 0), reg + 1)
        self.pointer_regs: dict[tuple, int] = {}
        self.pointers: set[tuple] = set()
        # walking pointers for lane-by-lane strided accesses: register, and
        # the stride multiple it is at in this section
        self.walk_regs: dict[tuple, int] = {}
        self.walking: dict[tuple, int] = {}
        self.scratch: dict[str, int] = {}

    def new_reg(self, comp: str) -> int:
        reg = self.next_reg.get(comp, 0)
        self.next_reg[comp] = reg + 1
        return reg

    def adapt_access(self, op) -> list:
        comp, reg = op.indices[0].component, op.indices[0].indices[0]
        db, strides = self.program.offsets, self.program.strides.get(comp, {})
        sigs = _sigs(op.sigs)
        usable = [s for s in sigs if _usable(self.ctx, s)]
        if sigs and not usable:
            raise specialization_error(
                f"every {op.step.op} signature for {db[op.offset]} needs a governing "
                f"predicate the ISA doesn't set up")
        rel = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
        vl = rel.pop(("VL",), 0)
        inserted = []

        strided = {f: c for f, c in rel.items() if f}
        if strided:
            for factors, count in strided.items():
                vl_times_stride = 2 == len(factors) and "VL" == factors[0] \
                    and factors[1].startswith("stride(")
                if not (vl_times_stride or (1 == len(factors) and factors[0].startswith("stride("))) \
                        or count < 0:
                    raise specialization_error(
                        f"{op.rsln} access to {db[op.offset]} is {sym._make(rel)} elements from "
                        f"its address register, which is not specialized yet")
            # lane by lane along a stride: the lane's own stride walks one
            # pointer per base and stride, stepping by the stride and
            # restarting from its base when the base changes or an access
            # goes back; the other factors (a column) give that base, as a
            # column pointer. A pointer per lane would take a register each
            lane_factor = None
            if "lane" in op.properties:
                singles = [k[0] for k in strided if 1 == len(k)]
                index = op.properties.get("stride_index")
                named = f"stride({comp},{index})" if index is not None else None
                if named in singles:
                    lane_factor = named
                elif 1 == len(strided) and 1 == len(singles):
                    lane_factor = singles[0]
            lane_count = strided.pop((lane_factor,)) if lane_factor is not None else None
            key = (comp, reg, tuple(sorted(strided.items())))
            columns = [k for k in self.pointer_regs if k[:2] == (comp, reg) and "walk" != k[2]]
            if strided and key not in self.pointer_regs and len(columns) >= MAX_COLUMN_POINTERS:
                # more columns than pointers kept for them (general registers
                # are few - RISC-V's C of 14 columns): one pointer walks
                # between the rest, moved by the difference, computed from
                # the base where this section hasn't placed it
                key = (comp, reg, "walk")
                if key not in self.pointer_regs:
                    self.pointer_regs[key] = self.new_reg(comp)
                ptr = self.pointer_regs[key]
                target = self.positions[(comp, reg)] + sym._make(strided)
                if key in self.pointers:
                    move = target - self.positions[(comp, ptr)]
                    if dict(move.terms):
                        inserted.append(lsc_addr_compute(comp, ptr, ptr, move, scalar_tile))
                else:
                    inserted.append(lsc_addr_compute(comp, reg, ptr, sym._make(strided), scalar_tile))
                    self.pointers.add(key)
                self.positions[(comp, ptr)] = target
            else:
                if strided and key not in self.pointer_regs:
                    self.pointer_regs[key] = self.new_reg(comp)
                ptr = self.pointer_regs[key] if strided else reg
            if strided and key not in self.pointers:
                delta = sym._make(strided)
                inserted.append(lsc_addr_compute(comp, reg, ptr, delta, scalar_tile))
                self.positions[(comp, ptr)] = self.positions[(comp, reg)] + delta
                self.pointers.add(key)
            base = reg
            reg = ptr
            if lane_factor is not None:
                wkey = (comp, base, lane_factor)
                if wkey not in self.walk_regs:
                    self.walk_regs[wkey] = self.new_reg(comp)
                walker = self.walk_regs[wkey]
                state = self.walking.get(wkey)
                if state is None or state[0] != ptr or lane_count < state[1]:
                    step = sym.factor(lane_factor, lane_count)
                    inserted.append(lsc_addr_compute(comp, ptr, walker, step, scalar_tile))
                    self.positions[(comp, walker)] = self.positions[(comp, ptr)] + step
                elif lane_count > state[1]:
                    step = sym.factor(lane_factor, lane_count - state[1])
                    inserted.append(lsc_addr_compute(comp, walker, walker, step, scalar_tile))
                    self.positions[(comp, walker)] = self.positions[(comp, walker)] + step
                self.walking[wkey] = (ptr, lane_count)
                reg = walker

        const = rel.get((), 0)
        immediate = const * adt_size(self.ctx.component_dts[comp])

        # Offsets in vector lengths: [x, #n, MUL VL] where a signature takes n
        # and nothing else is added; otherwise the address register moves by
        # them first, along with any constant
        if vl:
            if any(_vl_form(s) and _accepts(s, "voffset", vl) for s in usable) and not const:
                op.indices[0] = lsc_reg_index(comp, [reg])
                return inserted + [op]
            if comp not in self.scratch:
                self.scratch[comp] = self.new_reg(comp)
            scratch = self.scratch[comp]
            target = self.positions[(comp, reg)] + sym.const(const) + sym.factor("VL", vl)
            vl_taken = lambda n: any(_vl_form(s) and _accepts(s, "voffset", n) for s in usable)
            # the scratch where this section placed it: what is left, if a
            # signature takes it - vector lengths, or a constant
            if (comp, scratch) in getattr(self, "placed", set()):
                rest = dict((target - self.positions[(comp, scratch)]).terms)
                rvl, rconst = rest.pop(("VL",), 0), rest.pop((), 0)
                if not rest and ((not rconst and (not rvl or vl_taken(rvl))) or
                                 (not rvl and any(_takes(s, rconst * adt_size(
                                     self.ctx.component_dts[comp])) for s in usable))):
                    op.indices[0] = lsc_reg_index(comp, [scratch])
                    return inserted + [op]
            # placed at the constant only where a signature takes the vector
            # lengths: the next vectors past it need nothing more
            delta = sym.const(const) if vl_taken(vl) else sym.const(const) + sym.factor("VL", vl)
            here = self.positions[(comp, reg)] + delta
            if (comp, scratch) in getattr(self, "placed", set()) and \
                    not [f for f in dict((here - self.positions[(comp, scratch)]).terms) if f and ("VL",) != f]:
                # already placed this section: moved by the difference alone
                move = here - self.positions[(comp, scratch)]
                inserted.append(lsc_addr_compute(comp, scratch, scratch, move, scalar_tile))
            else:
                inserted.append(lsc_addr_compute(comp, reg, scratch, delta, scalar_tile))
            self.positions[(comp, scratch)] = here
            self.placed = getattr(self, "placed", set()) | {(comp, scratch)}
            op.indices[0] = lsc_reg_index(comp, [scratch])
            return inserted + [op]

        if not any(_takes(s, immediate) for s in usable):
            if not any(_takes(s, 0) for s in usable):
                raise specialization_error(
                    f"no {op.step.op} signature for {db[op.offset]} takes a plain address")
            if comp not in self.scratch:
                self.scratch[comp] = self.new_reg(comp)
            scratch = self.scratch[comp]
            inserted.append(lsc_addr_compute(comp, reg, scratch, sym.const(const), scalar_tile))
            self.positions[(comp, scratch)] = self.positions[(comp, reg)] + sym.const(const)
            reg = scratch
        op.indices[0] = lsc_reg_index(comp, [reg])
        return inserted + [op]

    def adapt_slices(self, op) -> list:
        """
        A loop over a tile's slices walks the address registers the model's
        plan gave its accesses - C's loads one, its stores another - not
        pointers of its own: each register starts at the first slice of the
        first walk on it in the block (its home), every walk on it an offset
        from there - another tile's first slice - and the loop leaves it a
        vector length of steps further. The plan is the emitter's too
        """
        db = self.program.offsets
        order = []
        for b in op.block:
            if isinstance(b, (lsc_load, lsc_store)):
                w = b.properties.get("walk", 0)
                if w not in order:
                    order.append(w)
        order += [w for w in range(len(op.walks)) if w not in order]
        plan = {}
        for w in order:
            walk = op.walks[w]
            comp, reg = walk.anchor.indices[0].component, walk.anchor.indices[0].indices[0]
            start = db.elements_offset(walk.anchor.offset, self.program.strides.get(comp, {}))
            key = (comp, reg)
            if key not in plan:
                plan[key] = {"step": walk.step, "home": start, "walks": {}}
            elif str(plan[key]["step"]) != str(walk.step):
                raise specialization_error(
                    f"a loop over slices walks {comp}'s address register by {plan[key]['step']} "
                    f"and by {walk.step}")
            plan[key]["walks"][w] = start - plan[key]["home"]
        inserted = []
        for (comp, reg), p in plan.items():
            to_home = p["home"] - self.positions[(comp, reg)]
            if dict(to_home.terms):
                inserted.append(lsc_addr_compute(comp, reg, reg, to_home, scalar_tile))
            # every slice walked: a vector length of steps on
            self.positions[(comp, reg)] = p["home"] + sym._make(
                {tuple(sorted(("VL",) + f)): c for f, c in dict(p["step"].terms).items()})
        op.walk_plan = plan
        # it moves them: the scheduler keeps what addresses through them after
        # it, after it
        op.refresh()
        return inserted + [op]

    def adapt(self, op) -> list:
        if isinstance(op, lsc_loop) and "slices" == op.info.get("kind"):
            return self.adapt_slices(op)
        if isinstance(op, lsc_loop):
            # each walk's anchor addressed like any access, its address
            # computations before the loop
            inserted = []
            for walk in op.walks:
                done = self.adapt_access(walk.anchor)
                walk.anchor = done[-1]
                inserted += done[:-1]
            op.refresh()
            return inserted + [op]
        if isinstance(op, (lsc_load, lsc_store)):
            return self.adapt_access(op)
        if isinstance(op, lsc_transformation):
            sigs = _sigs(op.resolution.compute_sg)
            if sigs and not any(_usable(self.ctx, s) for s in sigs):
                raise specialization_error(
                    f"every {op.op} signature needs a governing predicate the ISA "
                    f"doesn't set up")
        if isinstance(op, lsc_move):
            sigs = _sigs(op.sigs)
            if sigs and not any(_usable(self.ctx, s) for s in sigs):
                raise specialization_error(
                    "every move signature needs a governing predicate the ISA doesn't "
                    "set up")
            if not sigs:
                raise specialization_error(f"the ISA has no move for {op.rsln}")
        return [op]

    def adapt_block(self, block: ir_block):
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            ops = []
            for op in getattr(block, section):
                ops += self.adapt(op)
            setattr(block, section, ops)
            # column pointers are computed per section, in the same registers;
            # a scratch address placed in one section isn't relied on in the next
            self.pointers = set()
            self.walking = {}
            self.placed = set()

    def specialize(self) -> ir_program:
        for block in self.program.blocks:
            self.adapt_block(block)
        start = dict(self.positions)
        for case in self.program.cases:
            self.positions = dict(start)
            for block in case.blocks:
                self.adapt_block(block)
        return self.program
