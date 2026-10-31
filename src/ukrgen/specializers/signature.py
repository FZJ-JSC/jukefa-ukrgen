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

from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.asmblocks.op.constraint import ArgumentDependencyError
from asmgen.callconv.fngen import fngen
from ..support.sig_group import sig_group
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
    if isinstance(groups, sig_group):
        return list(groups.sigs)
    # a signature itself
    return [groups]


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
    setup = ctx.gen.isa_setup()
    if "EXPLICIT" != setup.predication().name:
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
    clobbered = set(sig.clobber_list or [])
    # re-set before each where the generator sets a mask all-true at all
    return set(masks) <= clobbered and bool(ctx.gen.set.forms(modifiers={opset_modifier.CONSTMASK}))


def _vl_form(sig) -> bool:
    """
    A load or store signature taking an offset in vector lengths: [x, #n, MUL VL]
    """
    return {m.name for m in sig.modifiers} - {"MASK"} == {"VOFFSET"} and "voffset" in sig.operands


def _takes(sig, immediate: int, limit: int | None = None) -> bool:
    """
    Whether a load or store signature takes an access at this immediate offset
    - within limit bytes, either sign, where one is given (--max-imm-offset)
    """
    form = _offset_forms(sig)
    if "plain" == form:
        return 0 == immediate
    if "ioffset" == form:
        if limit is not None and abs(immediate) > limit:
            return False
        return _accepts(sig, "ioffset", immediate)
    return False


#: column pointers kept per component and base where general registers are
#: many (AArch64, RISC-V: 31); columns beyond them share one walking pointer
MAX_COLUMN_POINTERS = 4
#: ... and where they are few (x86: 16)
FEW_COLUMN_POINTERS = 2


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

    def column_pointers(self) -> int:
        """
        Column pointers kept per component and base: fewer where the ISA has
        few general registers - x86's 16 hold A's and B's pointers, the
        loop's counter and the parameters too
        """
        if self._column_pointers is None:
            # the general registers the tracker allocates, reserved ones included
            gregs = self.ctx.gen.get_reg_tracker().available_reg_count("greg")
            self._column_pointers = MAX_COLUMN_POINTERS if gregs > 16 else FEW_COLUMN_POINTERS
        return self._column_pointers

    def __init__(self, ctx, program: ir_program):
        # what's been placed and walked, the column pointers made on first use
        self.placed = set()
        self.walked_by = {}
        #: the state the caller guarantees (--assume-state)
        self.assumed = {}
        self._column_pointers = None
        #: the loop index of the block being adapted (None: straight-line)
        self.loop_index = None
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
        assigned = reg
        db, strides = self.program.offsets, self.program.strides.get(comp, {})
        sigs = _sigs(op.sigs)
        # a last vector's access (tailmask) under the mask the emitter sets
        # up from tail(<index>): its masked forms usable without an all-true
        # predicate (RVV's v0.t)
        tail = op.properties.get("tail") is not None
        usable = [s for s in sigs if tail or _usable(self.ctx, s)]
        if sigs and not usable:
            raise specialization_error(
                f"every {op.step.op} signature for {db[op.offset]} needs a governing "
                f"predicate the ISA doesn't set up")
        rel = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
        vl = rel.pop(("VL",), 0)
        inserted = []

        strided = {f: c for f, c in rel.items() if f}
        # a component strided along the loop's own index (k:s - a gemmsup's
        # unpacked A, B): its registers walk - every strided offset of it (a
        # general stride's columns too), the access's register moved there from
        # whichever of the component's registers is the fewest strides away:
        # forward a stride (registers taken in turn leapfrog: one add of its
        # register), or a row on (a general stride: rs - (n - R) cs) - not a
        # column pointer per offset and register, which the walking bases
        # would leave behind
        def single(f):
            return 1 == len(f) and f[0].startswith(f"stride({comp},")
        walking = self.loop_index is not None and self.loop_index in strides \
            and strided and all(single(f) for f in strided) and "lane" not in op.properties
        if walking:
            target = self.positions[(comp, reg)] + sym._make(strided)
            def strides_away(r):
                d = dict((target - self.positions[(comp, r)]).terms)
                if not all(single(f) for f in d if f):
                    return float("inf")
                return sum(abs(c) for f, c in d.items() if f)
            bases = [r for (c, r) in self.program.addr_setup if c == comp and (c, r) in self.positions]
            source = min(bases or [reg], key=strides_away)
            move = target - self.positions[(comp, source)]
            if dict(move.terms) or source != reg:
                # (source first, then the register set: dest = src + delta)
                inserted.append(lsc_addr_compute(comp, source, reg, move, scalar_tile))
                walked = self.walked_by
                walked[(comp, reg)] = walked.get((comp, reg), sym.const(0)) + \
                    (target - self.positions[(comp, reg)])
                self.walked_by = walked
                self.positions[(comp, reg)] = target
            rel = {f: c for f, c in rel.items() if not f}
            strided = {}
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
            # a stride times a count the ISA scales an index register by (x86:
            # 1, 2, 4, 8): the base pointer and the stride's register as
            # index - no pointer of its own (docs/REG_USE_OPTIMIZATION.md, 2c)
            if lane_factor is None and not vl and 1 == len(strided):
                (factors, count), = strided.items()
                # the ISA's own forms - the operation's signatures, chosen for
                # its resolution, hold none with a register offset
                dt = self.ctx.component_dts[comp]
                operation = getattr(self.ctx.gen, op.step.op, None)      # IR pseudo-operations have none
                full = operation.get_signatures() if operation is not None else []
                scales = {s.structural_params.get("scale_factor") for s in full
                          if "SCALEOFFSET" in {m.name for m in s.modifiers}
                          and ("adreg" not in s.operands or s.operands["adreg"].dt == dt)}
                # the access's own plain or immediate form, which the index
                # extends (a gather or scatter has none)
                plain = any(not ({m.name for m in s.modifiers} - {"IOFFSET", "MASK", "STRUCT"})
                            for s in usable)
                if 1 == len(factors) and count in scales and plain:
                    op.properties["scaled_index"] = (factors[0], count)
                    strided = {}
            key = (comp, reg, tuple(sorted(strided.items())))
            columns = [k for k in self.pointer_regs if k[:2] == (comp, reg) and "walk" != k[2]]
            if strided and key not in self.pointer_regs and len(columns) >= self.column_pointers():
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

        if reg != assigned:
            # the access goes through a column or walking pointer: what is
            # left is from where that pointer stands - its walks included
            now = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
            if not [f for f in now if f and ("VL",) != f]:
                vl = now.pop(("VL",), 0)
                rel = now
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
            if (comp, scratch) in self.placed:
                rest = dict((target - self.positions[(comp, scratch)]).terms)
                rvl, rconst = rest.pop(("VL",), 0), rest.pop((), 0)
                if not rest and ((not rconst and (not rvl or vl_taken(rvl))) or
                                 (not rvl and any(_takes(s, rconst * adt_size(
                                     self.ctx.component_dts[comp]),
                                     self.max_imm_offset) for s in usable))):
                    op.indices[0] = lsc_reg_index(comp, [scratch])
                    return inserted + [op]
            # placed at the constant only where a signature takes the vector
            # lengths: the next vectors past it need nothing more
            delta = sym.const(const) if vl_taken(vl) else sym.const(const) + sym.factor("VL", vl)
            here = self.positions[(comp, reg)] + delta
            if (comp, scratch) in self.placed and \
                    not [f for f in dict((here - self.positions[(comp, scratch)]).terms) if f and ("VL",) != f]:
                # already placed this section: moved by the difference alone
                move = here - self.positions[(comp, scratch)]
                inserted.append(lsc_addr_compute(comp, scratch, scratch, move, scalar_tile))
            else:
                inserted.append(lsc_addr_compute(comp, reg, scratch, delta, scalar_tile))
            self.positions[(comp, scratch)] = here
            self.placed = self.placed | {(comp, scratch)}
            op.indices[0] = lsc_reg_index(comp, [scratch])
            return inserted + [op]

        if not any(_takes(s, immediate, self.max_imm_offset) for s in usable):
            if not any(_takes(s, 0) for s in usable):
                raise specialization_error(
                    f"no {op.step.op} signature for {db[op.offset]} takes a plain address")
            # the access's own register walks to it: later accesses resolved
            # from there (offsets until the limit, then a bump, as v1 did); the
            # section moves it back at its end
            inserted.append(lsc_addr_compute(comp, reg, reg, sym.const(const), scalar_tile))
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + sym.const(const)
            walked = self.walked_by
            walked[(comp, reg)] = walked.get((comp, reg), sym.const(0)) + sym.const(const)
            self.walked_by = walked
        op.indices[0] = lsc_reg_index(comp, [reg])
        return inserted + [op]

    def adapt_slices(self, op) -> list:
        """
        A loop over a tile's slices walks the address registers the model's
        plan gave its accesses - C's loads one, its stores another - not
        pointers of its own: each register starts at the first slice of the
        first walk on it in the block (its home), every walk on it an offset
        from there - another tile's first slice - and after the loop an
        address computation steps it back by its walk, home: code around the
        loop - an enclosing loop's advance, its last iteration's - finds it
        there whatever iteration it is. The plan is the emitter's too
        """
        if op.info.get("count"):
            # a run-time count (a masked tile's rows): its walks copied into
            # registers of their own (the emitter's), its addresses not moving
            return [op]
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
        inserted, back = [], []
        for (comp, reg), p in plan.items():
            to_home = p["home"] - self.positions[(comp, reg)]
            if dict(to_home.terms):
                inserted.append(lsc_addr_compute(comp, reg, reg, to_home, scalar_tile))
                # a move like an access's: the section moves it back at its
                # end - a loop's next iteration, its tail, start where it did
                # (a streamed tile's: ZA's kappa 1 loads X's rows into tiles)
                walked = self.walked_by
                walked[(comp, reg)] = walked.get((comp, reg), sym.const(0)) + to_home
                self.walked_by = walked
            # every slice walked - a vector length of steps on - then its walk
            # stepped back: home
            walk = sym._make({tuple(sorted(("VL",) + f)): c for f, c in dict(p["step"].terms).items()})
            if dict(walk.terms):
                back.append(lsc_addr_compute(comp, reg, reg, sym.const(0) - walk, scalar_tile))
            self.positions[(comp, reg)] = p["home"]
        op.walk_plan = plan
        # it moves them: the scheduler keeps what addresses through them after
        # it, after it
        op.refresh()
        return inserted + [op] + back

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
        if isinstance(op, lsc_store) and "shuffle" == op.rsln:
            raise specialization_error(
                f"{op.indices[1]}: a shuffle store is a row of a transpose in registers, "
                f"which shufflenet makes of blocks of as many rows as a vector has lanes - "
                f"these rows aren't; alone it would store the row contiguously")
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

    def rebase(self, block: ir_block, rebased: dict) -> list:
        """
        After a preloading prologue: each register of a preloaded component
        moved to its first access in the body, so the loop's offsets start
        at 0 - where none of its accesses there goes negative (x86 takes no
        negative offset) and the move is constant or in vector lengths
        """
        shift = block.preload_shift or {}
        if not any(shift.values()):
            return []
        db, firsts, lows = self.program.offsets, {}, {}
        for op in block.body:
            if not isinstance(op, (lsc_load, lsc_store)):
                continue
            comp, reg = op.indices[0].component, op.indices[0].indices[0]
            if not shift.get(comp) or (comp, reg) not in self.positions:
                continue
            rel = db.elements_offset(op.offset, self.program.strides.get(comp, {})) - self.positions[(comp, reg)]
            firsts.setdefault((comp, reg), rel)
            lows.setdefault((comp, reg), []).append(rel)
        out = []
        for (comp, reg), delta in firsts.items():
            terms = dict(delta.terms)
            if any(f and ("VL",) != f for f in terms) or not any(terms.values()):
                continue
            # none of the register's accesses below it after the move
            if any(dict((r - delta).terms).get((), 0) < 0 or dict((r - delta).terms).get(("VL",), 0) < 0
                   for r in lows[(comp, reg)]):
                continue
            out.append(lsc_addr_compute(comp, reg, reg, delta, scalar_tile))
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + delta
            rebased[(comp, reg)] = delta
        return out

    def loop_advances(self, block: ir_block) -> dict:
        """
        A loop's advance to its next iteration, per address register the model
        set up: what the emitter otherwise appends as text after the body
        """
        if block.loop_index is None or not block.advance:
            return {}
        db, out = self.program.offsets, {}
        for comp, oid in block.advance.items():
            step = db.elements_offset(oid, self.program.strides.get(comp, {}))
            for (c, reg) in list(self.positions):
                if c == comp and (c, reg) in self.program.addr_setup:
                    out[(c, reg)] = step
        return out

    def adapt_block(self, block: ir_block):
        self.loop_index = block.loop_index
        rebased = {}
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            ops = []
            for op in getattr(block, section):
                ops += self.adapt(op)
            # registers walked in this section back where it found them: the
            # next section (or iteration) starts from the same positions - and
            # in a loop's body and last iteration, merged with the advance to
            # the next iteration: one add a register, placed by the schedulers
            walked = self.walked_by
            advances = self.loop_advances(block) if section in ("body", "epilogue") else {}
            for key in list(walked) + [k for k in advances if k not in walked]:
                comp, reg = key
                moved = walked.get(key, sym.const(0))
                step = advances.get(key)
                # strides walked (k:s - a gemmsup's A, B): one move, the advance
                # less the walk - two would each add the stride's register as
                # often as it counts (8 strides back, 8 on: 16 adds for none);
                # addrmerge merges constants and vector lengths, not strides
                strided = any(f and f != ("VL",) for x in (moved, step) if x is not None
                              for f in dict(x.terms))
                if strided and step is not None:
                    net = step - moved
                    op = lsc_addr_compute(comp, reg, reg, net, scalar_tile)
                    op.properties = dict(op.properties or {}, advance=step)
                    ops.append(op)
                    self.positions[key] = self.positions[key] - moved
                    continue
                if any(dict(moved.terms).values()):
                    ops.append(lsc_addr_compute(comp, reg, reg, sym.const(0) - moved, scalar_tile))
                if step is not None and any(dict(step.terms).values()):
                    op = lsc_addr_compute(comp, reg, reg, step, scalar_tile)
                    op.properties = dict(op.properties or {}, advance=step)
                    ops.append(op)
                self.positions[key] = self.positions[key] - moved
            if advances:
                block.advance_in_ir = True
            self.walked_by = {}
            if "prologue" == section:
                # the loop's offsets from 0: registers moved past the preload
                ops += self.rebase(block, rebased)
            if "epilogue" == section:
                # and back after the last iteration: the tail starts where it
                # does when the loop (and its prologue) didn't run
                for (comp, reg), delta in rebased.items():
                    ops.append(lsc_addr_compute(comp, reg, reg, sym.const(0) - delta, scalar_tile))
                    self.positions[(comp, reg)] = self.positions[(comp, reg)] - delta
            setattr(block, section, ops)
            # column pointers are computed per section, in the same registers;
            # a scratch address placed in one section isn't relied on in the next
            self.pointers = set()
            self.walking = {}
            self.placed = set()

    def element_types(self, dt):
        """
        Where the element type is processor state (RVV's vtype): an lsc_state
        before each transformation needing another than the one before - a
        widening one the narrow type, arithmetic on a group the group's type
        and grouping - each section beginning and ending with the setup's
        (dt's, ungrouped), whatever order the sections run in. A
        transformation whose signatures need different ones left to the
        emitter (vtype_dynamic), as it was
        """
        from ..models.load_store_operations import lsc_state
        from ..irmod.lsc.base import blocks_and_sections
        setup = (adt_size(dt), 1)
        def need(op, sig):
            sizes = [adt_size(o.dt) for o in sig.operands.values() if rgt.VEC == o.rtype and o.dt is not None]
            if not sizes:
                return None
            ways = op.properties.get("group", 1)
            return (min(sizes), 1) if widening_ways(sig) > 1 else (max(sizes), ways)
        def switch(want, sig, dtype=None):
            wdt = dtype or next(o.dt for o in sig.operands.values()
                                if rgt.VEC == o.rtype and o.dt is not None and adt_size(o.dt) == want[0])
            # named as the setup's state names it (asmgen: e32), a group's
            # grouping after it (e64,m2)
            name = f"e{8 * want[0]}" + (f",m{want[1]}" if want[1] > 1 else "")
            return lsc_state({"vtype": name}, wdt)
        for block, section in blocks_and_sections(self.program):
            ops, out, current = list(getattr(block, section) or []), [], setup
            for op in ops:
                if isinstance(op, lsc_transformation):
                    sigs = _sigs(op.resolution.compute_sg) if op.resolution is not None else []
                    wants = {w for w in (need(op, s) for s in sigs) if w is not None}
                    if len(wants) > 1:
                        op.add_property("vtype_dynamic", True)
                        current = None              # the emitter's from here
                    elif wants:
                        want = next(iter(wants))
                        if want != current:
                            out.append(switch(want, next(s for s in sigs if need(op, s) == want)))
                            current = want
                out.append(op)
            if current is not None and current != setup:
                out.append(switch(setup, None, dt))
            setattr(block, section, out)

    def specialize(self) -> ir_program:
        for block in self.program.blocks:
            self.adapt_block(block)
        start = dict(self.positions)
        for case in self.program.cases:
            self.positions = dict(start)
            for block in case.blocks:
                self.adapt_block(block)
        # the state the ISA's setup leaves (for the narrowest element type, as
        # the emitter sets it up), lsc_states setting more: each access's
        # signatures those whose requirements hold where it is - decided here,
        # with the forms, before scheduling
        # (imported here: the state module reaches the irmods, tailmask this module)
        from ..lsc_model.state import check_state
        dt = min(self.ctx.component_dts.values(), key=adt_size)
        if self.ctx.gen.isa_setup().element_type_is_state():
            self.element_types(dt)
        isa = self.ctx.gen.isa_setup()
        state, engine = isa.state(dt), isa.engine()
        if engine is not None:
            # the engine on before every path and off after them, as state the
            # emitter writes through the ISA's signatures (set's ENGINE): the
            # state before it the setup's without its own switch
            from ..models.load_store_operations import lsc_state
            on, off = engine
            if all(self.assumed.get(k) == v for k, v in on.items()):
                # the caller's: the engine on around the kernel, no switch
                self.program.engine_assumed = True
            elif not any(isinstance(op, lsc_state) and op.values == on for op in self.program.entry):
                # first: smstart zeroes the predicates - a tail's mask after it
                self.program.entry = [lsc_state(dict(on), dt)] + list(self.program.entry)
                self.program.exit = list(self.program.exit) + [lsc_state(dict(off), dt)]
            state = {**state, **off}
        problems = check_state(self.program, {**state, **self.assumed})
        if problems:
            raise specialization_error("processor state: " + "; ".join(problems))
        return self.program
