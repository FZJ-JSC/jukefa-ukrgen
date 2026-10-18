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


@dataclass
class emitted_block:
    """
    A block's sections as assembly. A loop block's body is one iteration;
    advance moves the address registers on to the next, tail_advance does the
    same for one tail iteration.
    """
    name : str
    loop_index : str | None
    sections : dict[str, list[str]] = field(default_factory=dict)
    advance : list[str] = field(default_factory=list)
    #: what the region needs set up at its start: address registers from the
    #: parameters, loop counts
    loads : list[str] = field(default_factory=list)
    #: a loop's counters: iterations, then the tail's
    counters : tuple | None = None
    tail_advance : list[str] = field(default_factory=list)


@dataclass
class emitted_program:
    """
    :param setup: address register initialization
    :param bases: memory component -> register holding its base address, to be
                  bound to the kernel's arguments
    :param registers: virtual register -> physical register
    """
    setup : list[str]
    blocks : list[emitted_block]
    cases : list[tuple[str, dict, list[emitted_block]]]
    bases : dict[str, str]
    registers : dict[tuple, str]
    teardown : list[str] = field(default_factory=list)
    data : list[str] = field(default_factory=list)
    #: the program with its control flow - loops, the dispatch on cases -
    #: between setup and teardown
    code : list[str] = field(default_factory=list)
    #: the function's parameters in order, each in the register named - k per
    #: loop, base(X) per component's start address, stride(X,i) in bytes - as
    #: the calling convention passes them (asmgen's callconv)
    params : dict[str, str] = field(default_factory=dict)
    #: the function's boilerplate: saving the callee-saved registers the code
    #: clobbers and loading parameters passed on the stack; restoring, return
    entry : list[str] = field(default_factory=list)
    exit : list[str] = field(default_factory=list)

    def instructions(self) -> list[str]:
        """
        Every instruction, in program order, ignoring loop structure
        """
        out = list(self.setup)
        if self.code:
            return list(self.entry) + out + list(self.code) + list(self.teardown) \
                + list(self.exit) + list(self.data)
        for block in self.blocks + [b for _, _, bs in self.cases for b in bs]:
            for lines in block.sections.values():
                out += lines
            out += block.advance + block.tail_advance
        return out + list(self.teardown) + list(self.data)

    def function(self, name: str) -> list[str]:
        """
        The program as an assembly function: the symbol, then every
        instruction
        """
        # no executable stack: GNU linkers assume one without this note
        return [".text", f".global {name}", f"{name}:"] + self.instructions() \
            + ['.section .note.GNU-stack,"",%progbits']

    def render(self) -> str:
        lines = ["// bases: " + ", ".join(f"{c} in {r}" for c, r in self.bases.items())]
        lines += self.setup

        def block_lines(block: emitted_block, indent: str):
            lines.append(f"{indent}// block {block.name}"
                         + (f", loop over {block.loop_index}" if block.loop_index else ""))
            for section, ops in block.sections.items():
                if ops:
                    lines.append(f"{indent}// {section}")
                    lines.extend(indent + op for op in ops)
            if block.advance:
                lines.append(f"{indent}// next iteration")
                lines.extend(indent + op for op in block.advance)

        for block in self.blocks:
            block_lines(block, "")
        for label, _, blocks in self.cases:
            lines.append(f"// case {label}")
            for block in blocks:
                block_lines(block, "  ")
        return "\n".join(lines)


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
            delta = sym.const(const) + sym.factor("VL", vl)
            inserted.append(lsc_addr_compute(comp, reg, scratch, delta, scalar_tile))
            self.positions[(comp, scratch)] = self.positions[(comp, reg)] + delta
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

    def adapt(self, op) -> list:
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
            # column pointers are computed per section, in the same registers
            self.pointers = set()
            self.walking = {}

    def specialize(self) -> ir_program:
        for block in self.program.blocks:
            self.adapt_block(block)
        start = dict(self.positions)
        for case in self.program.cases:
            self.positions = dict(start)
            for block in case.blocks:
                self.adapt_block(block)
        return self.program


class signature_emitter:
    """
    Turns one part's specialized IR program into assembly

    :param ctx: context after the model stage
    :param program: the program to specialize
    """

    def __init__(self, ctx, program: ir_program, preallocate=()):
        self.ctx = ctx
        self.gen = ctx.gen
        self.program = program
        # the generator's tracker keeps the stack pointer and the like out of
        # reach; older generators don't provide one
        make = getattr(self.gen, "get_reg_tracker", None)
        self.rt = make() if make else \
            reg_tracker([("greg", self.gen.max_gregs()), ("vreg", self.gen.max_vregs())])
        self.phys: dict[tuple, object] = {}
        self.dts: dict[tuple, object] = self._register_types()
        self.numbers: dict[tuple, int] = {}
        self.bounds = self._register_bounds()
        if hasattr(self.rt, "set_priority"):
            self._required_priorities()
        # setup instructions found while emitting: vector length in bytes,
        # constant strides
        self.late_setup: list[str] = []
        self.vlb: dict[int, object] = {}
        self.masks: dict = {}
        self.indexes: dict = {}
        # setup-time values a previous emission found it needed: allocated
        # before any region, in the tracker every region inherits
        self.preallocate = list(preallocate)
        self.recipes: list[tuple[str, tuple, bool]] = []
        self.regions_started = False
        self.region_loads: list[str] = []
        self.labels = iter(range(10**6))
        isa = self.gen.isa_setup()
        self.vector_length_kept = isa.predication().name == "IMPLICIT" \
            if hasattr(isa, "predication") else False
        self.strides_in: dict[str, object] = {}

    # --- registers ---------------------------------------------------------

    def _register_types(self) -> dict[tuple, object]:
        """
        Data type of every virtual data register: the memory component it is
        loaded from or stored to, or the component it holds
        """
        comps = self.ctx.component_dts
        dts: dict[tuple, object] = {}

        def note(idx, dt):
            dts.setdefault((idx.component, idx.indices[0]), dt)

        for op in self._all_ops():
            if isinstance(op, (lsc_load, lsc_store)):
                note(op.indices[1], comps[op.indices[0].component])
        for op in self._all_ops():
            for idx in op.indices:
                if idx.component in comps:
                    note(idx, comps[idx.component])
        default = next(iter(comps.values()))
        for op in self._all_ops():
            for idx in op.indices:
                note(idx, default)
        return dts

    def _all_ops(self):
        for block in self.program.blocks + [b for c in self.program.cases for b in c.blocks]:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                yield from getattr(block, section)

    def reg(self, idx, rtype):
        """
        The physical register for a virtual one. Vectors fill the vector file
        from the bottom, scalars from the top: on ISAs where scalar FP registers
        are the low parts of vector registers the two must not meet.
        """
        key = (idx.component, idx.indices[0], rtype)
        group = self.program.groups.get(idx.component)
        if key not in self.phys and group is not None and rgt.VEC == rtype:
            # a group of registers: all of them at once, consecutive and
            # starting at a multiple of their number (RVV's groups need that,
            # SVE's structure loads and stores take consecutive ones)
            ways = group[0]
            first = idx.indices[0] - idx.indices[0] % ways
            used = self.rt.get_used_regs("vreg")
            start = next((s for s in range(0, self.gen.max_vregs() - ways + 1, ways)
                          if not any(s + p in used for p in range(ways))), None)
            if start is None:
                raise specialization_error(f"no {ways} consecutive vector registers left for "
                                           f"{idx.component}{first}")
            for p in range(ways):
                self.rt.reserve_specific_reg("vreg", start + p)
                member = (idx.component, first + p, rtype)
                self.phys[member] = self.gen.vreg(start + p)
                self.numbers[member] = ("vreg", start + p)
        if key not in self.phys:
            dt = self.dts.get((idx.component, idx.indices[0]))
            tag = "vreg"
            if rgt.VEC == rtype:
                bound = self.bounds.get(key)
                if bound is None:
                    number = self.rt.reserve_any_reg("vreg")
                else:
                    used = self.rt.get_used_regs("vreg")
                    free = [i for i in bound if i not in used]
                    if not free:
                        raise specialization_error(
                            f"none of the vector registers {bound} left for {key[0]}{key[1]}")
                    number = free[0]
                    self.rt.reserve_specific_reg("vreg", number)
                self.phys[key] = self.gen.vreg(number)
            elif rgt.FP == rtype and "freg" in getattr(self.rt, "shared", {}):
                # the tracker knows which vector registers FP registers are
                number = self.rt.reserve_any_reg("freg")
                tag = "freg"
                self.phys[key] = self.gen.freg(number, dt)
            elif rgt.FP == rtype and "freg" in getattr(self.rt, "registered_types", ()):
                # a file of its own (RVV)
                number = self.rt.reserve_any_reg("freg")
                tag = "freg"
                self.phys[key] = self.gen.freg(number, dt)
            elif rgt.FP == rtype:
                # older trackers: from the top of the vector file, clear of vectors
                used = self.rt.get_used_regs("vreg")
                number = max(i for i in range(self.gen.max_vregs()) if i not in used)
                self.rt.reserve_specific_reg("vreg", number)
                tag = "vreg"
                self.phys[key] = self.gen.freg(number, dt)
            elif rgt.TILE == rtype:
                # a tile (SME ZA): from its own file
                if "treg" not in getattr(self.rt, "registered_types", ()):
                    self.rt.add_type("treg", self.gen.max_tregs(dt))
                number = self.rt.reserve_any_reg("treg")
                tag = "treg"
                self.phys[key] = self.gen.treg(number, dt)
            else:
                raise specialization_error(f"{rtype.name} registers are not specialized yet")
            self.numbers[key] = (tag, number)
        return self.phys[key]

    def _register_bounds(self) -> dict[tuple, list[int]]:
        """
        The vector registers each virtual register may use, where an
        operation's signature limits them - SVE's indexed fmla encodes its
        indexed register in 4 bits for doubles: the domain of the operand's
        constraints over the register file, whatever asmgen declares
        """
        bounds: dict[tuple, list[int]] = {}
        file = range(self.gen.max_vregs())
        for op in self._all_ops():
            if not isinstance(op, lsc_transformation):
                continue
            sigs = sorted((s for s in _sigs(op.resolution.compute_sg) if _usable(self.ctx, s)),
                          key=_masked)
            if not sigs:
                continue
            sig = sigs[0]
            for hw, idx, rtype in zip(op.hw_operands, op.indices, op.rtypes or []):
                shape = sig.operands.get(hw)
                if rgt.VEC != rtype or shape is None or not shape.value_constraints:
                    continue
                try:
                    allowed = operand_values(sig, hw, universe=file).values
                except ArgumentDependencyError:
                    continue
                if len(allowed) < len(file):
                    key = (idx.component, idx.indices[0], rtype)
                    bounds[key] = sorted(set(bounds.get(key, allowed)) & set(allowed))
        return bounds

    def _required_priorities(self):
        """
        Registers some instruction restricts an operand to - SME's slice index
        registers, SVE's indexed registers - kept for it: their allocation
        priority lowered, so general allocation takes others first
        """
        files = {rgt.GP: ("greg", self.gen.max_gregs()), rgt.VEC: ("vreg", self.gen.max_vregs()),
                 rgt.MASK: ("mreg", self.gen.max_mregs())}
        ops = list(self._all_ops())
        while ops:
            op = ops.pop()
            if isinstance(op, lsc_loop):
                ops += list(op.block) + [w.anchor for w in op.walks]
                continue
            groups = [getattr(getattr(op, "resolution", None), "compute_sg", None), getattr(op, "sigs", None)]
            for sig in (s for g in groups if g for s in _sigs(g)):
                for name, shape in sig.operands.items():
                    if ot.REGISTER != shape.otype or shape.rtype not in files or \
                            not shape.value_constraints:
                        continue
                    tag, count = files[shape.rtype]
                    if tag not in getattr(self.rt, "registered_types", ()):
                        continue
                    try:
                        allowed = operand_values(sig, name, universe=range(count)).values
                    except ArgumentDependencyError:
                        continue
                    if len(allowed) < count:
                        # below callee-saved registers' -1
                        for n in allowed:
                            self.rt.set_priority(tag, n, min(-2, self.rt.priority(tag, n)))

    def release(self, key):
        """
        A virtual register's value is dead: its physical register is free again
        (a group's registers stay: a lone member must not be handed out)
        """
        if key[0] in self.program.groups:
            return
        if key in self.phys:
            tag, number = self.numbers.pop(key)
            self.rt.unuse_reg(tag, number)
            del self.phys[key]

    def greg(self):
        return self.gen.greg(self.rt.reserve_any_reg("greg"))

    # --- addresses ---------------------------------------------------------

    def bytes_of(self, component: str, elements: sym) -> sym:
        return elements * adt_size(self.ctx.component_dts[component])

    def stride_reg(self, factor: str, setup: bool = False):
        """
        The register holding a run-time stride in bytes: its parameter's
        """
        return self.params[factor]

    def add_bytes(self, areg, amount: sym, comp: str) -> list[str]:
        """
        Move an address register on by a number of bytes: constants as an
        immediate, multiples of run-time strides as adds of the stride
        registers, which hold strides in bytes
        """
        dt = self.ctx.component_dts[comp]
        esize = adt_size(dt)
        lines = []
        for factors, coeff in amount.terms:
            if not factors:
                lines.append(self.gen.add_greg_imm(reg=areg, imm=coeff))
            elif 2 == len(factors) and "VL" == factors[0] and factors[1].startswith("stride(") \
                    and coeff > 0 and 0 == coeff % esize:
                # a vector length of strided elements: the vector length in
                # elements times the stride in bytes, multiplied once
                lines += [self.gen.add_greg_greg(dst=areg, reg1=areg,
                                                 reg2=self.vl_stride(factors[1], dt))] * (coeff // esize)
            elif ("VL",) == factors and coeff > 0 and 0 == coeff % esize \
                    and self.vector_length_kept:
                # RVV: the vector length is in a register - add it in bytes
                vlb = self.vl_bytes(dt)
                lines += [self.gen.add_greg_greg(dst=areg, reg1=areg, reg2=vlb)] * (coeff // esize)
            elif ("VL",) == factors and coeff > 0 and 0 == coeff % esize:
                # whole vectors: incb x, ALL, MUL #n, n at most 16 a time
                vectors = coeff // esize
                while vectors:
                    step = min(vectors, 16)
                    lines.append(self.gen.add_greg_voff(reg=areg, offset=step, dt=dt))
                    vectors -= step
            elif 1 == len(factors) and factors[0].startswith("stride(") \
                    and coeff > 0 and 0 == coeff % esize:
                sreg = self.stride_reg(factors[0])
                lines += [self.gen.add_greg_greg(dst=areg, reg1=areg, reg2=sreg)] * (coeff // esize)
            else:
                raise specialization_error(
                    f"moving {comp}'s address by {amount} bytes needs run-time arithmetic "
                    f"(vector length), which is not specialized yet")
        return lines

    # --- operations ----------------------------------------------------------

    def slices(self, op) -> list[str]:
        """
        A loop over a tile's slices, as many as it has rows or columns at run
        time: a walking pointer from the first slice, the slice index in one of
        w12-w15 counting up - an unrolled iteration's slices at its immediates
        """
        anchor = op.walks[0].anchor
        comp, reg = anchor.indices[0].component, anchor.indices[0].indices[0]
        dt = self.ctx.component_dts[comp]
        elements = self.program.offsets.elements_offset(anchor.offset, self.program.strides.get(comp, {}))
        start = elements - self.positions[(comp, reg)]
        # the slice index register: one every signature's slice operand takes
        # (SME: w12-w15)
        access = op.block[0]
        allowed = set(range(self.gen.max_gregs()))
        for sig in _sigs(access.sigs):
            for name in sig.operands:
                if name.endswith(("_rowreg", "_colreg")):
                    allowed &= set(operand_values(sig, name, universe=sorted(allowed)).values)
        used = self.rt.get_used_regs("greg")
        number = next((n for n in sorted(allowed) if n not in used), None)
        if number is None:
            raise specialization_error(f"{comp}: the slice index registers, {sorted(allowed)}, "
                                       f"are all taken")
        self.rt.reserve_specific_reg("greg", number)
        index = self.gen.greg(number)
        walker, counter, delta = self.greg(), self.greg(), self.greg()
        lines = [self.gen.mov_greg(src=self.aregs[(comp, reg)], dst=walker)]
        lines += self.add_bytes(walker, self.bytes_of(comp, start), comp)
        lines.append(self.gen.mov_greg(src=self.vl_elements(dt), dst=counter))
        lines.append(self.gen.mov_greg_imm(reg=index, imm=0))
        terms = dict(op.walks[0].step.terms)
        if set(terms) == {()}:
            lines.append(self.gen.mov_greg_imm(reg=delta, imm=terms[()] * adt_size(dt)))
        else:
            lines.append(self.gen.mov_greg(src=self.stride_reg(next(iter(terms))[0]), dst=delta))
        loop = f"ukr{next(self.labels)}_slices"
        lines.append(self.gen.label(label=loop))
        access, unroll = op.block[0], op.subtiling.unroll
        for u in range(unroll):
            access.properties.update(slice_reg=index, slice_imm=u)
            line = self._mem(access, self.reg(access.indices[1], access.rtypes[1]), walker, 0)
            if line is None:
                raise specialization_error(f"{op.walks[0].anchor.rsln}: no {access.step.op} of a "
                                           f"{comp} slice takes slice immediate {u}")
            lines.append(line)
            lines.append(self.gen.add_greg_greg(dst=walker, reg1=walker, reg2=delta))
        lines.append(self.gen.add_greg_imm(reg=index, imm=unroll))
        lines.append(self.gen.add_greg_imm(reg=counter, imm=-unroll))
        lines.append(self.gen.cb(reg1=counter, reg2=None, cmp=comparison.NZ, label=loop))
        for r in (walker, counter, delta, index):
            self.rt.unuse_reg("greg", r.idx)
        return [l.strip() for chunk in lines for l in (chunk.splitlines() if isinstance(chunk, str) else chunk)
                if l.strip()]

    def loop(self, op) -> list[str]:
        """
        A loop over a vector's elements, as many as it has of its type at run
        time: a walking pointer from the first element, one element's steps,
        the pointer moved by the element stride
        """
        if "slices" == op.info.get("kind"):
            return self.slices(op)
        anchor = op.walks[0].anchor
        comp, reg = anchor.indices[0].component, anchor.indices[0].indices[0]
        dt = self.ctx.component_dts[comp]
        if not op.subtiling.count.runtime or 1 != op.subtiling.count.size:
            raise specialization_error(f"{op.info.get('component')}: a loop of "
                                       f"{op.subtiling.count} iterations is not emitted yet")
        elements = self.program.offsets.elements_offset(anchor.offset, self.program.strides.get(comp, {}))
        start = elements - self.positions[(comp, reg)]
        # the scratch scalars in the body hold the component's elements
        for s in op.block:
            for idx in s.indices:
                self.dts.setdefault((idx.component, idx.indices[0]), dt)
        walker, counter, delta = self.greg(), self.greg(), self.greg()
        lines = [self.gen.mov_greg(src=self.aregs[(comp, reg)], dst=walker)]
        lines += self.add_bytes(walker, self.bytes_of(comp, start), comp)
        lines.append(self.gen.mov_greg(src=self.vl_elements(dt), dst=counter))
        # the walk's step, the element stride in bytes - negative where a fill
        # shifts up (SVE insr, into lane 0): from the last element backwards
        stride = op.walks[0].step
        terms = dict(stride.terms)
        up = op.subtiling.order < 0
        if set(terms) == {()}:
            nbytes = terms[()] * adt_size(dt)
            lines.append(self.gen.mov_greg_imm(reg=delta, imm=-nbytes if up else nbytes))
        elif 1 == len(terms) and 1 == len(next(iter(terms))) and 1 == next(iter(terms.values())):
            source = self.stride_reg(next(iter(terms))[0])
            lines.append(self.gen.mul_greg_imm(src=source, dst=delta, factor=-1) if up
                         else self.gen.mov_greg(src=source, dst=delta))
        else:
            raise specialization_error(f"{op.rsln}: walking {comp} by {stride} elements")
        if up:
            # the last element: a vector length of strides on, one back
            lines += self.add_bytes(walker, self.bytes_of(comp, sym._make(
                {tuple(sorted(("VL",) + f)): c for f, c in terms.items()})), comp)
            lines.append(self.gen.add_greg_greg(dst=walker, reg1=walker, reg2=delta))
        loop = f"ukr{next(self.labels)}_elements"
        lines.append(self.gen.label(label=loop))
        # the body as often as an iteration takes elements, the pointer moved
        # after each; its scalar rotating through as many registers as asked,
        # so the elements' scalar loads and stores need not wait for each other
        unroll = op.subtiling.unroll
        count = max(1, min(op.subtiling.registers, unroll))
        first = op.block[0]
        scalars, extra = [self.reg(first.indices[1], first.rtypes[1])], []
        for _ in range(count - 1):
            tag = "freg" if rgt.FP == first.rtypes[1] else "greg"
            number = self.rt.reserve_any_reg(tag)
            extra.append((tag, number))
            scalars.append(self.gen.freg(number, dt) if "freg" == tag else self.gen.greg(number))

        def access(step, data):
            line = self._mem(step, data, walker, 0)
            if line is None:
                raise specialization_error(f"{op.rsln}: no {step.step.op} of one {comp} "
                                           "element takes a plain address")
            return line

        if "load" == op.info["direction"]:
            # a batch of loads into different registers, then their fills in
            # order: the loads don't wait for the fills
            load, fill = op.block
            for start in range(0, unroll, count):
                batch = range(start, min(unroll, start + count))
                for e in batch:
                    lines.append(access(load, scalars[e - start]))
                    lines.append(self.gen.add_greg_greg(dst=walker, reg1=walker, reg2=delta))
                for e in batch:
                    lines.append(self.move(fill, src=scalars[e - start]))
        else:
            # the extract and shift a chain on the vector; each extract into the
            # next register, so it needn't wait for the store before
            extract, store, shift = op.block
            for e in range(unroll):
                scalar = scalars[e % count]
                lines.append(self.move(extract, dst=scalar))
                lines.append(self.move(shift))
                lines.append(access(store, scalar))
                lines.append(self.gen.add_greg_greg(dst=walker, reg1=walker, reg2=delta))
        lines.append(self.gen.add_greg_imm(reg=counter, imm=-unroll))
        lines.append(self.gen.cb(reg1=counter, reg2=None, cmp=comparison.NZ, label=loop))
        for r in (walker, counter, delta):
            self.rt.unuse_reg("greg", r.idx)
        for tag, number in extra:
            self.rt.unuse_reg(tag, number)
        return [l.strip() for chunk in lines for l in (chunk.splitlines() if isinstance(chunk, str) else chunk)
                if l.strip()]

    def shift_of(self, op) -> int:
        """
        How far a move shifts its vector: recorded, or fixed by its signature
        """
        if "irot" in op.properties:
            return op.properties["irot"]
        for sig in _sigs(op.sigs):
            for name in sig.operands:
                if name.endswith("_irot"):
                    single = operand_values(sig, name).single()
                    if single is not None:
                        return single
        return 0

    def memory(self, op) -> list[str]:
        """
        A load or store through the signature taking its offset from its address
        register, which specializing has made a constant some signature takes
        """
        comp, reg = op.indices[0].component, op.indices[0].indices[0]
        areg = self.aregs[(comp, reg)]
        elements = self.program.offsets.elements_offset(op.offset, self.program.strides.get(comp, {}))
        rel = dict((elements - self.positions[(comp, reg)]).terms)
        vl = rel.pop(("VL",), 0)
        if vl:
            line = self._mem(op, self.reg(op.indices[1], op.rtypes[1]), areg, 0, voffset=vl)
            if line is None:
                raise specialization_error(
                    f"no signature of {op.step.op} takes {self.program.offsets[op.offset]} "
                    f"at {vl} vector lengths: specialize the IR first")
            return [line]
        if set(rel) - {()}:
            raise specialization_error(
                f"{op.rsln} access to {self.program.offsets[op.offset]} is not a constant "
                f"offset from its address register: specialize the IR first")
        immediate = rel.get((), 0) * adt_size(self.ctx.component_dts[comp])
        increment = getattr(op, "increment", None)
        if increment is not None:
            # a post-increment: the access at the register, then the register on
            line = self._mem(op, self.reg(op.indices[1], op.rtypes[1]), areg, immediate,
                             increment=dict(increment.terms).get((), 0)
                             * adt_size(self.ctx.component_dts[comp]))
            if line is None:
                raise specialization_error(
                    f"no signature of {op.step.op} post-increments by {increment} elements")
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + increment
            return [line]
        line = self._mem(op, self.reg(op.indices[1], op.rtypes[1]), areg, immediate)
        if line is None:
            raise specialization_error(
                f"no signature of {op.step.op} takes {self.program.offsets[op.offset]} at "
                f"offset {immediate}: specialize the IR first")
        return [line]

    def _predicate(self, sig, kwargs: dict, prefix: list | None = None, dt=None) -> bool:
        """
        Bind a signature's mask operands: to the all-true predicate under
        explicit predication; to a mask register set all-true right before
        the instruction where the instruction clears it (prefix gets the
        setting). False if neither applies
        """
        masks = [n for n, o in sig.operands.items() if orl.MASK == o.orole]
        if not masks:
            return True
        predicate = _all_true(self.ctx, self.rt)
        clobbered = set(getattr(sig, "clobber_list", None) or [])
        if predicate is None and (prefix is None or not set(masks) <= clobbered
                                  or not hasattr(self.gen, "mask_all_true")):
            return False
        for name in masks:
            if predicate is not None:
                kwargs[name] = predicate
                continue
            reg = self.clobbered_mask(sig.operands[name].rtype)
            kwargs[name] = reg
            prefix.append(self.gen.mask_all_true(reg=reg, dt=dt))
        return True

    def clobbered_mask(self, rtype):
        """
        The register for masks instructions clear: a mask register, or a
        vector register where masks are vectors (AVX2) - allocated once
        """
        if rtype not in self.masks:
            if rgt.VEC == rtype:
                self.masks[rtype] = self.gen.vreg(self.rt.reserve_any_reg("vreg"))
            else:
                self.masks[rtype] = self.gen.mreg(self.rt.reserve_any_reg("mreg"))
        return self.masks[rtype]

    def index_vector(self, op):
        """
        The index vector of a gather or scatter: the stride along its index
        times 0, 1, 2... in bytes, built once after the ISA's setup
        (greg_to_voffs)
        """
        comp = op.indices[0].component
        key = (comp, op.properties.get("stride_index"))
        if key not in self.indexes:
            stride = self.stride_of(op)
            if stride is None:
                return None
            vreg = self.gen.vreg(self.rt.reserve_any_reg("vreg"))
            try:
                text = self.gen.greg_to_voffs(streg=stride, vreg=vreg,
                                              dt=self.ctx.component_dts[comp])
            except NotImplementedError as err:
                raise specialization_error(f"index vector for {comp}: {err}") from err
            # built where the region using it starts
            self.region_loads += [l.strip() for l in text.splitlines() if l.strip()]
            self.indexes[key] = vreg
        return self.indexes[key]

    def stride_of(self, op, setup: bool = False):
        """
        The register holding a strided access's stride in bytes: the run-time
        stride register, or a constant stride loaded once
        """
        comp = op.indices[0].component
        index = op.properties.get("stride_index")
        stride = self.program.strides.get(comp, {}).get(index)
        if stride is None:
            return None
        terms = dict(stride.terms)
        if 1 == len(terms) and 1 == list(terms.values())[0] and list(terms)[0] \
                and list(terms)[0][0].startswith("stride("):
            return self.stride_reg(list(terms)[0][0], setup=setup)
        if set(terms) <= {()}:
            nbytes = terms.get((), 0) * adt_size(self.ctx.component_dts[comp])
            return self.constant_stride(nbytes)
        return None

    def vl_elements(self, dt):
        """
        A register holding the vector length in elements: RVV's vl, or read
        once after the ISA's setup where the ISA doesn't keep it (SVE: cntd)
        """
        if self.vector_length_kept:
            return self.gen.isa_setup().vector_length_register(rt=self.rt)
        key = f"VL in {adt_size(dt)}-byte elements"
        if key not in self.strides_in:
            self.recipes.append(("vl_elements", (dt,), self.regions_started))
            reg = self.greg()
            try:
                self.late_setup.append(self.gen.vlen_to_greg(reg=reg, dt=dt))
            except (NotImplementedError, AttributeError) as err:
                raise specialization_error(f"reading the vector length: {err}") from err
            self.strides_in[key] = reg
        return self.strides_in[key]

    def vl_stride(self, factor: str, dt):
        """
        A register holding the vector length in elements times a stride in
        bytes: a vector length of strided elements, multiplied once in setup
        """
        key = f"VL*{factor}"
        if key not in self.strides_in:
            self.recipes.append(("vl_stride", (factor, dt), self.regions_started))
            vlreg = self.vl_elements(dt)
            reg = self.greg()
            self.strides_in[key] = reg
            self.late_setup.append(self.gen.mul_greg_greg(
                dst=reg, reg1=vlreg, reg2=self.stride_reg(factor, setup=True)))
        return self.strides_in[key]

    def constant_stride(self, nbytes: int):
        """
        A register holding a constant stride, loaded once in setup
        """
        key = f"constant stride {nbytes}"
        if key not in self.strides_in:
            self.recipes.append(("constant_stride", (nbytes,), self.regions_started))
            reg = self.greg()
            self.strides_in[key] = reg
            self.late_setup.append(self.gen.mov_greg_imm(reg=reg, imm=nbytes))
        return self.strides_in[key]

    def vl_bytes(self, dt):
        """
        A register holding the vector length in bytes, for ISAs keeping the
        vector length in a register (RVV): computed once per element size,
        right after the ISA's setup
        """
        esize = adt_size(dt)
        if esize not in self.vlb:
            self.recipes.append(("vl_bytes", (dt,), self.regions_started))
            vlreg = self.gen.isa_setup().vector_length_register(rt=self.rt)
            reg = self.greg()
            self.vlb[esize] = reg
            self.late_setup += [self.gen.mov_greg(src=vlreg, dst=reg),
                                self.gen.shift_greg_left(reg=reg, bit_count=esize.bit_length() - 1)]
        return self.vlb[esize]

    def address(self, op: lsc_addr_compute) -> list[str]:
        """
        An address register set from another plus an offset
        """
        comp = op.indices[0].component
        src_key = (comp, op.indices[0].indices[0])
        dest_key = (comp, op.indices[1].indices[0])
        if dest_key not in self.aregs:
            self.aregs[dest_key] = self.greg()
        dest = self.aregs[dest_key]
        lines = [] if src_key == dest_key else [self.gen.mov_greg(src=self.aregs[src_key], dst=dest)]
        lines += self.add_bytes(dest, self.bytes_of(comp, op.delta), comp)
        self.positions[dest_key] = self.positions[src_key] + op.delta
        return lines

    def members(self, op, data, sig) -> list:
        """
        The registers a load or store moves: for a structure signature on a
        group, every member - interleaved in memory - else the one
        """
        ways = op.properties.get("group")
        if not ways or "STRUCT" not in {m.name for m in sig.modifiers}:
            return [data]
        j = next(j for j, r in enumerate(op.rtypes) if rgt.VEC == r)
        base = op.indices[j]
        return [self.reg(lsc_reg_index(base.component, [base.indices[0] + p]), rgt.VEC)
                for p in range(ways)]

    def _mem(self, op, data, areg, immediate: int, increment: int | None = None,
             voffset: int | None = None) -> str | None:
        """
        The access through the first signature taking it with this immediate
        offset (0: one without an offset)
        """
        dt = self.ctx.component_dts[op.indices[0].component]
        lane = op.properties.get("lane")
        for sig in sorted(_sigs(op.sigs), key=lambda s: len(s.modifiers)):
            mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
            kwargs = {}
            if voffset is not None:
                if {"VOFFSET"} != mods:
                    continue
                kwargs["voffset"] = voffset
            elif increment is not None:
                if {"POSTINC"} != mods or immediate:
                    continue
                kwargs["iinc"] = increment
            elif {"IOFFSET"} == mods:
                kwargs["ioffset"] = immediate
            elif {"VINDEX"} == mods and not immediate:
                index = self.index_vector(op)
                if index is None:
                    continue
                kwargs["vidxreg"] = index
            elif {"GSTRIDE"} == mods and not immediate:
                stride = self.stride_of(op)
                if stride is None:
                    continue
                kwargs["streg"] = stride
            elif mods or immediate:
                continue
            prefix = []
            if not self._predicate(sig, kwargs, prefix, dt):
                continue
            # a tile slice's index: the loop's register and immediate
            for name in sig.operands:
                if name.endswith(("_rowreg", "_colreg")) and "slice_reg" in op.properties:
                    kwargs[name] = op.properties["slice_reg"]
                elif name.endswith(("_immrow", "_immcol")) and "slice_imm" in op.properties:
                    kwargs[name] = op.properties["slice_imm"]
            side = op.properties.get("side")
            for name, shape in sig.operands.items():
                if ot.IMMEDIATE == shape.otype and name.endswith("_lane") and \
                        (side is None or side == operand_side(sig, name[:-5], op.step.op)):
                    kwargs[name] = lane
            kwargs.update(sig.structural_params)
            try:
                return "".join(prefix) + getattr(self.gen, op.step.op)(
                    dregs=self.members(op, data, sig), areg=areg, dt=dt,
                    modifiers=set(sig.modifiers),
                    operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                       if s.modifiers},
                    **kwargs)
            except Exception:       # asmgen refuses: try the next signature
                continue
        return None

    def vtype_for(self, op, sig) -> str:
        """
        Where the element type travels in a register (RVV's vtype): switched,
        keeping the vector length, only before an operation needing another -
        a widening one the narrow type, arithmetic on a group the group's type
        and grouping. Empty where nothing changes
        """
        if self.vtype is None or not hasattr(self.gen, "vsetvli_keep_vl"):
            return ""
        sizes = [adt_size(o.dt) for o in sig.operands.values()
                 if rgt.VEC == o.rtype and getattr(o, "dt", None) is not None]
        if not sizes:
            return ""
        ways = op.properties.get("group", 1)
        if widening_ways(sig) > 1:
            want = (min(sizes), self.lmul)
        else:
            want = (max(sizes), self.lmul * ways)
        if want == self.vtype:
            return ""
        self.vtype = want
        dt = next(o.dt for o in sig.operands.values()
                  if rgt.VEC == o.rtype and adt_size(o.dt) == want[0])
        return self.gen.vsetvli_keep_vl(dt=dt, lmul=want[1])

    def compute(self, op: lsc_transformation) -> str:
        """
        An arithmetic operation through a signature of its group, with its
        registers in the operand slots and lanes in the lane immediates
        """
        regs = {hw: self.reg(idx, rtype)
                for hw, idx, rtype in zip(op.hw_operands, op.indices, op.rtypes)}
        lanes = {f"{hw}_lane": idx.indices[1]
                 for hw, idx in zip(op.hw_operands, op.indices) if len(idx.indices) > 1}
        failures = []
        for sig in sorted(_sigs(op.resolution.compute_sg), key=_masked):
            masks = {}
            if not self._predicate(sig, masks):
                continue
            dts = {f"{hw[0]}_dt": sig.operands[hw].dt for hw in op.hw_operands}
            # the part of a wide result a widening instruction computes
            parts = {"part": op.properties["part"]} \
                if "part" in sig.operands and "part" in op.properties else {}
            try:
                return self.vtype_for(op, sig) + getattr(self.gen, op.op)(
                    **regs, **dts, **lanes, **masks, **parts, **sig.structural_params,
                    modifiers=set(sig.modifiers),
                    operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                       if s.modifiers})
            except Exception as err:
                failures.append(str(err))
        if all(any(orl.MASK == o.orole for o in sig.operands.values())
               for sig in _sigs(op.resolution.compute_sg)):
            raise specialization_error(
                f"every {op.op} signature needs a governing predicate: masked signatures "
                f"(SVE, RVV) are not specialized yet")
        raise specialization_error(f"no signature of {op.op} takes {regs}: {failures[:2]}")

    def emit_op(self, op) -> list[str]:
        return [l.strip() for chunk in self._emit_op(op) for l in chunk.splitlines() if l.strip()]

    def _emit_op(self, op) -> list[str]:
        if isinstance(op, lsc_loop):
            return self.loop(op)
        if isinstance(op, (lsc_load, lsc_store)):
            return self.memory(op)
        if isinstance(op, lsc_transformation):
            return [self.compute(op)]
        if isinstance(op, lsc_zero) and rgt.TILE == op.rtypes[0]:
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [self.gen.zero_treg(treg=reg, dt=self.dts[(op.indices[0].component,
                                                              op.indices[0].indices[0])])]
        if isinstance(op, lsc_zero):
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [self.gen.zero_vreg(vreg=reg, dt=self.dts[(op.indices[0].component,
                                                               op.indices[0].indices[0])])]
        if isinstance(op, lsc_addr_compute):
            return self.address(op)
        if isinstance(op, lsc_move):
            return [self.move(op)]
        raise specialization_error(f"cannot emit {type(op).__name__}")

    def move(self, op: lsc_move, src=None, dst=None) -> str:
        """
        A move between registers through the first unmasked signature taking it
        (src, dst: other physical registers than the operation's, an unrolled
        loop's rotation)
        """
        src = self.reg(op.indices[0], op.rtypes[0]) if src is None else src
        dst = self.reg(op.indices[1], op.rtypes[1]) if dst is None else dst
        # the destination's type, or the source's where the destination is a
        # scratch (a drain loop's extract into a scalar)
        dt = self.dts.get((op.indices[1].component, op.indices[1].indices[0])) or \
            self.dts[(op.indices[0].component, op.indices[0].indices[0])]
        for sig in sorted(_sigs(op.sigs), key=_masked):
            masks = {}
            if not self._predicate(sig, masks):
                continue
            # the lane or block index for the operand on the step's side
            side = op.properties.get("side")
            on_side = lambda base: side is None or side == operand_side(sig, base, "move")
            blocks = {n: op.properties.get("block") for n in sig.operands
                      if n.endswith("_block") and "block" in op.properties and on_side(n[:-6])}
            blocks.update({n: op.properties["lane"] for n in sig.operands
                           if n.endswith("_lane") and "lane" in op.properties and on_side(n[:-5])})
            # a shift by a fixed amount (a fill loop's): the one the signature
            # takes, or the one recorded (a drain loop's)
            for n, shape in sig.operands.items():
                if n.endswith("_irot") and "irot" in op.properties:
                    blocks[n] = op.properties["irot"]
                elif n.endswith("_irot") and shape.value_constraints:
                    single = operand_values(sig, n).single()
                    if single is not None:
                        blocks[n] = single
            try:
                return self.gen.move(
                    dregs=[src, dst], dts=[dt, dt], modifiers=set(sig.modifiers),
                    **masks, **sig.structural_params, **blocks,
                    operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                       if s.modifiers})
            except Exception:       # asmgen refuses: try the next signature
                continue
        raise specialization_error(f"no move signature takes {src} into {dst}")

    def block(self, block: ir_block, later: list[ir_block] = ()) -> emitted_block:
        out = emitted_block(name=block.name, loop_index=block.loop_index)
        if block.loop_index is not None:
            # zeroing the accumulators goes before anything a loop may skip:
            # with no full iterations only the tail runs
            prologue = list(block.prologue)
            # (and loads the hoist irmod moved out of the loop)
            first = lambda op: isinstance(op, lsc_zero) or op.properties.get("hoisted")
            out.sections["init"] = [line for op in prologue if first(op)
                                    for line in self.emit_op(op)]
            out.sections["prologue"] = [line for op in prologue if not first(op)
                                        for line in self.emit_op(op)]
            for section in ("body", "epilogue", "tail", "subtail"):
                out.sections[section] = [line for op in getattr(block, section)
                                         for line in self.emit_op(op)]
        else:
            out.sections["body"] = self.straight(block.body, later)
        return self._advances(block, out)

    def straight(self, ops: list, later: list[ir_block]) -> list[str]:
        """
        A straight-line block, its registers renamed: a register is free again
        after its value's last use, so values reuse the registers of values that
        died - C those of AB in gemm's epilogue. Registers no later block reads
        are released when the block starts.
        """
        def keys(op):
            return [(i.component, i.indices[0], r) for i, r in
                    zip(op.indices, getattr(op, "rtypes", None) or [])
                    if r in (rgt.VEC, rgt.FP)]

        needed_later = {k for b in later
                        for section in ("prologue", "body", "epilogue", "tail", "subtail")
                        for op in getattr(b, section) for k in keys(op)}
        used_here = {k for op in ops for k in keys(op)}
        for key in list(self.phys):
            if key not in used_here and key not in needed_later:
                self.release(key)
        last = {}
        for pos, op in enumerate(ops):
            for k in keys(op):
                last[k] = pos
        lines = []
        for pos, op in enumerate(ops):
            lines += self.emit_op(op)
            for k in keys(op):
                if last[k] == pos and k not in needed_later:
                    self.release(k)
        return lines

    def _advances(self, block: ir_block, out: emitted_block) -> emitted_block:
        db, strides = self.program.offsets, self.program.strides
        for comp, oid in block.advance.items():
            step = self.bytes_of(comp, db.elements_offset(oid, strides.get(comp, {})))
            # the address registers the model set up: pointers and scratch
            # addresses are recomputed from them each iteration
            for (c, reg), areg in sorted(self.aregs.items(), key=lambda x: x[0]):
                if c == comp and (c, reg) in self.program.addr_setup:
                    out.advance += [l.strip() for l in self.add_bytes(areg, step, comp)]
                    if block.tail_step is not None:
                        one = db.add(comp, {block.loop_index: block.tail_step})
                        out.tail_advance += self._strip(self.add_bytes(
                            areg, self.bytes_of(comp, db.elements_offset(one, strides.get(comp, {}))),
                            comp))
        return out

    @staticmethod
    def _strip(lines: list[str]) -> list[str]:
        return [l.strip() for l in lines]

    def emit(self) -> emitted_program:
        import copy
        # what the ISA needs set up: SVE's all-true predicate, SME's smstart,
        # RVV's vsetvli - for the narrowest element type, so a predicate covers
        # every lane of every operation
        dt = min(self.ctx.component_dts.values(), key=adt_size)
        isa = self.gen.isa_setup()
        lines = lambda text: [l.strip() for l in text.splitlines() if l.strip()]
        # the function's parameters where the calling convention puts them
        self.parameters()
        # registers an operation limits go first, from the bottom
        for key in sorted(self.bounds, key=lambda k: len(self.bounds[k])):
            self.reg(lsc_reg_index(key[0], [key[1]]), key[2])
        setup = lines(isa.setup(rt=self.rt, dt=dt))
        self.isa_setup_lines = len(setup)
        # the element type the ISA's setup leaves in place, where it travels
        # in a register: the narrowest, with the chosen grouping
        self.lmul = getattr(self.gen, "lmul", 1)
        self.vtype = (adt_size(dt), self.lmul) if hasattr(self.gen, "vsetvli_keep_vl") else None
        # setup-time values found needed by a previous emission: allocated
        # here, before any region, so every region knows their registers
        for name, args in self.preallocate:
            getattr(self, name)(*args)
        self.regions_started = True
        # regions - each block, the dispatch, each case - set up what they
        # need at their start and release, at their end, what no later region
        # needs: parameters live only as long as they are used
        self.bases, self.aregs, self.positions = {}, {}, {}
        prefix = self.program.blocks
        case_blocks = [b for c in self.program.cases for b in c.blocks]
        regions = [self.memory_comps([b]) for b in prefix]
        case_comps = [self.memory_comps(c.blocks) for c in self.program.cases]
        conditions = {v for c in self.program.cases for v in c.when}
        loops = [b.loop_index for b in prefix + case_blocks]
        blocks = []
        for i, b in enumerate(prefix):
            later = set().union(*regions[i + 1:], *case_comps, conditions)
            new_before = set(self.aregs)
            self.region_loads = self.start_addresses(regions[i], later)
            self.start_indexes([b])
            counters = None
            if b.loop_index is not None:
                counters, count_lines = self.loop_counts(b, b.loop_index in loops[i + 1:])
                self.region_loads += count_lines
            out = self.block(b, prefix[i + 1:] + case_blocks)
            out.loads, out.counters = self.region_loads, counters
            blocks.append(out)
            # pointers the block computed, and what no later region uses
            new = set(self.aregs) - new_before
            self.release_aregs({k for k in self.aregs
                                if k[0] not in later or (k in new and k not in self.program.addr_setup)})
            for reg in counters or ():
                if reg is not None:
                    self.rt.unuse_reg("greg", reg.idx)
            self.release_params(later, set(loops[i + 1:]))
            self.release_indexes(set().union(*[self.index_keys([x]) for x in prefix[i + 1:]],
                                             *[self.index_keys(c.blocks) for c in self.program.cases]))
        self.dispatch_code = self.dispatch() if self.program.cases else []
        # every case starts with the registers where the dispatch leaves them;
        # the cases exclude each other, so they share the registers left, and
        # a parameter's register can become an address register in each
        start = (dict(self.positions), dict(self.phys), dict(self.numbers),
                 copy.deepcopy(self.rt), dict(self.aregs), set(self.live_params), self.vtype,
                 dict(self.indexes))
        main_rt = self.rt
        cases = []
        for j, c in enumerate(self.program.cases):
            self.positions, self.phys, self.numbers = dict(start[0]), dict(start[1]), dict(start[2])
            self.rt, self.aregs, self.live_params = copy.deepcopy(start[3]), dict(start[4]), set(start[5])
            self.vtype = start[6]
            self.indexes = dict(start[7])
            self.region_loads = self.start_addresses(case_comps[j], set())
            self.start_indexes(c.blocks)
            out = [self.block(b, list(c.blocks[i + 1:])) for i, b in enumerate(c.blocks)]
            if out:
                out[0].loads = self.region_loads + out[0].loads
            cases.append((c.label, c.when, out))
            for tag, regs in self.rt.clobbered_regs.items():
                main_rt.clobbered_regs.setdefault(tag, set()).update(regs)
        if self.program.cases:
            self.rt = main_rt
        bases = {n[5:-1]: str(r) for n, r in self.params.items() if n.startswith("base(")}
        # what the code clobbers is known now: the function's boilerplate,
        # loading stack parameters at entry into the registers they had then
        self.fn.rt.aliased_regs.setdefault("greg", {}).update(self.param_aliases)
        # what the ISA's setup and teardown clobber beyond the allocation (SME:
        # changing streaming mode zeroes the vector registers) - the calling
        # convention keeps what its callee must
        for tag, regs in getattr(isa, "clobbers", dict)().items():
            self.cc.add_clobber(tag, regs)
        save, load, restore = self.fn.get_boilerplate(cc=self.cc)
        # what emission found it needs: right after the ISA's setup
        late = [l.strip() for chunk in self.late_setup for l in chunk.splitlines() if l.strip()]
        setup = setup[:self.isa_setup_lines] + late + setup[self.isa_setup_lines:]
        entry, leave = lines(save) + lines(load), lines(restore) + lines(self.gen.ret())
        return emitted_program(
            setup=setup, blocks=blocks, cases=cases,
            teardown=lines(isa.teardown(rt=self.rt, dt=dt)), data=lines(isa.data()),
            bases=bases,
            registers={k: str(v) for k, v in self.phys.items()},
            code=self.control(blocks, cases),
            params={n: str(r) for n, r in self.params.items()},
            entry=entry, exit=leave)

    # --- control flow ---------------------------------------------------------

    def parameters(self):
        """
        The function's parameters, declared to the calling convention and
        aliased in the register tracker where it passes them (fngen): k per
        loop, each component's start address, each run-time stride in bytes
        """
        names = []
        for b in self.program.blocks + [b for c in self.program.cases for b in c.blocks]:
            if b.loop_index is not None and b.loop_index not in names:
                names.append(b.loop_index)
        for comp in dict.fromkeys(c for c, _ in sorted(self.program.addr_setup)):
            names.append(f"base({comp})")
        factors = set()
        for idxs in self.program.strides.values():
            for stride in idxs.values():
                for term in dict(stride.terms):
                    factors.update(f for f in term if f.startswith("stride("))
        names += sorted(factors)
        self.cc = self.gen.create_callconv()
        # the callee's registers last: no save and restore unless needed
        if hasattr(self.cc, "deprioritize_callee_saved"):
            self.cc.deprioritize_callee_saved(self.rt)
        for name in names:
            self.cc.add_param("greg", name)
        self.fn = fngen(gen=self.gen, rt=self.rt)
        self.fn.init_cc(cc=self.cc)
        self.params = {n: self.gen.greg(self.rt.aliased_regs["greg"][n]) for n in names}
        self.live_params = set(names)
        # the boilerplate finds where parameters passed on the stack are
        # loaded through these aliases, which releasing a register drops
        self.param_aliases = {n: self.rt.aliased_regs["greg"][n] for n in names}

    def param_comp(self, name: str):
        return name[name.index("(") + 1:].split(",")[0].rstrip(")") if "(" in name else None

    def release_params(self, later: set, later_loops: set):
        """
        Parameters no later region uses: their registers are free
        """
        for name in sorted(self.live_params):
            comp = self.param_comp(name)
            needed = comp in later if comp is not None else name in later_loops
            if not needed:
                self.live_params.discard(name)
                reg = self.params[name]
                if reg.idx in self.rt.get_used_regs("greg"):
                    self.rt.unuse_reg("greg", reg.idx)

    def loop_counts(self, block, shared: bool):
        """
        A loop's counters from its k parameter (kiterkleft): the iterations,
        each taking the elements of one, and what is left for the tail
        """
        k = self.params[block.loop_index]
        terms = dict(block.step.terms)
        if set(terms) != {()}:
            raise specialization_error(f"{block.name}: a step of {block.step} elements is not "
                                       "counted yet")
        if 1 == int(terms[()]):
            # one element an iteration: k counts them, nothing is left over
            return (None, None), []
        lines = []
        if shared:
            # a later loop counts the same k: count a copy
            copy_reg = self.greg()
            lines.append(self.gen.mov_greg(src=k, dst=copy_reg))
            k = copy_reg
        left, tmp = self.greg(), self.greg()
        lines.append(self.gen.kiterkleft(kreg=k, kleftreg=left, tmpreg=tmp, unroll=int(terms[()])))
        self.rt.unuse_reg("greg", tmp.idx)
        return (k if shared else None, left), [l.strip() for chunk in lines for l in chunk.splitlines()
                                               if l.strip()]

    def dispatch(self) -> list[str]:
        """
        Find the first case whose conditions hold: alpha and beta loaded at
        their own size and compared as floating point (cb) to the values the
        conditions name - so -0.0 counts as 0, and NaN as no value named
        """
        import struct
        gen = self.gen
        lines = []
        self.dispatch_tag = next(self.labels)

        def freg(dt):
            return gen.freg(self.rt.reserve_any_reg("freg"), dt)

        for i, c in enumerate(self.program.cases):
            following = f"ukr{self.dispatch_tag}_try{i + 1}"
            for var, value in c.when.items():
                dt = self.ctx.component_dts[var]
                size = adt_size(dt)
                v, k, t = freg(dt), freg(dt), self.greg()
                lines.append(gen.load_freg(areg=self.params[f"base({var})"], offset=0, dst=v, dt=dt))
                if 0 == float(value):
                    lines.append(gen.zero_freg(freg=k, dt=dt))
                else:
                    bits = struct.unpack("<Q" if 8 == size else "<I",
                                         struct.pack("<d" if 8 == size else "<f", float(value)))[0]
                    lines.append(gen.mov_greg_imm(reg=t, imm=bits))
                    lines.append(gen.mov_greg_to_freg(src=t, dst=k, dt=dt))
                lines.append(gen.cb(reg1=v, reg2=k, cmp=comparison.NE, label=following, dt=dt, greg=t))
                for r in (v, k):
                    self.rt.unuse_reg("freg", r.idx)
                self.rt.unuse_reg("greg", t.idx)
            lines.append(gen.jump(label=f"ukr{self.dispatch_tag}_case{i}"))
            lines.append(gen.label(label=following))
        return [l.strip() for chunk in lines for l in chunk.splitlines() if l.strip()]

    def memory_comps(self, blocks) -> set:
        """
        The components a region's loads, stores and address computations access
        """
        comps = set()
        for b in blocks:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                for op in getattr(b, section, None) or []:
                    if isinstance(op, (lsc_load, lsc_store, lsc_addr_compute)):
                        comps.add(op.indices[0].component)
                    elif isinstance(op, lsc_loop):
                        comps |= {w.anchor.indices[0].component for w in op.walks}
        return comps

    def gathers(self, blocks) -> list:
        """
        A region's gathers and scatters: loads and stores through an index
        vector, which the region builds at its start
        """
        found = []
        for b in blocks:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                for op in getattr(b, section, None) or []:
                    if isinstance(op, (lsc_load, lsc_store)) and "VINDEX" in \
                            {m.name for m in (getattr(op.step, "op_mod_reqs", None) or set())}:
                        found.append(op)
        return found

    def index_keys(self, blocks) -> set:
        return {(op.indices[0].component, op.properties.get("stride_index"))
                for op in self.gathers(blocks)}

    def start_indexes(self, blocks):
        """
        The index vectors a region's gathers and scatters need, allocated and
        built at its start - before anything the region allocates itself
        """
        for op in self.gathers(blocks):
            self.index_vector(op)

    def release_indexes(self, later: set):
        for key in [k for k in self.indexes if k not in later]:
            self.rt.unuse_reg("vreg", self.indexes.pop(key).idx)

    def start_addresses(self, comps, later) -> list[str]:
        """
        Each address register of these components, not yet held: a copy of
        the component's start address parameter moved to its first access.
        Where no later region needs the start address, the parameter's own
        register becomes the last of them, the others copied before it moves
        """
        lines = []
        db, strides = self.program.offsets, self.program.strides
        for comp in sorted(comps):
            name = f"base({comp})"
            keys = [k for k in sorted(self.program.addr_setup) if k[0] == comp and k not in self.aregs]
            if not keys or name not in self.params:
                continue
            param = self.params[name]
            reuse = comp not in later and name in self.live_params
            for n, key in enumerate(keys):
                if reuse and n == len(keys) - 1:
                    areg = param
                    self.live_params.discard(name)
                else:
                    areg = self.greg()
                    lines += [l.strip() for l in self.gen.mov_greg(src=param, dst=areg).splitlines()
                              if l.strip()]
                self.aregs[key] = areg
                start = db.elements_offset(self.program.addr_setup[key], strides.get(comp, {}))
                self.positions[key] = start
                lines += [l.strip() for l in self.add_bytes(areg, self.bytes_of(comp, start), comp)]
        return lines

    def release_aregs(self, keys):
        for key in keys:
            reg = self.aregs.pop(key)
            self.rt.unuse_reg("greg", reg.idx)

    def control(self, blocks, cases) -> list[str]:
        """
        The program's control flow around the blocks' sections, branching with
        cb. A loop with N iterations, software-pipelined:

            cb N == 0 -> done; prologue; N -= 1; cb N == 0 -> last
          loop: body, advance; N -= 1; cb N != 0 -> loop
          last: epilogue, advance
          done: the tail likewise, R times

        then the dispatch to the first case whose conditions hold, each case
        ending at the end of the cases
        """
        lines = lambda text: [l.strip() for l in text.splitlines() if l.strip()]
        gen = self.gen
        code: list[str] = []
        ez, nz = comparison.EZ, comparison.NZ

        def counted(reg, label, part, done):
            code.extend(lines(gen.cb(reg1=reg, reg2=None, cmp=ez, label=done)))
            code.extend(lines(gen.label(label=label)))
            code.extend(part)
            code.extend(lines(gen.add_greg_imm(reg=reg, imm=-1)))
            code.extend(lines(gen.cb(reg1=reg, reg2=None, cmp=nz, label=label)))
            code.extend(lines(gen.label(label=done)))

        def block_code(block):
            code.extend(block.loads)
            sec = block.sections
            if block.loop_index is None:
                for part in sec.values():
                    code.extend(part)
                code.extend(block.advance + block.tail_advance)
                return
            n, left = block.counters
            n = n or self.params[block.loop_index]
            tag = next(self.labels)
            done = f"ukr{tag}_done"
            code.extend(sec.get("init", []))
            code.extend(lines(gen.cb(reg1=n, reg2=None, cmp=ez, label=done)))
            code.extend(sec.get("prologue", []))
            code.extend(lines(gen.add_greg_imm(reg=n, imm=-1)))
            counted(n, f"ukr{tag}_loop", sec.get("body", []) + block.advance, f"ukr{tag}_last")
            code.extend(sec.get("epilogue", []) + block.advance)
            code.extend(lines(gen.label(label=done)))
            if sec.get("tail") and left is not None:
                counted(left, f"ukr{tag}_tail", sec["tail"] + block.tail_advance,
                        f"ukr{tag}_taildone")
            if sec.get("subtail"):
                raise specialization_error(
                    f"{block.name}: a tail below one operation's extent is not emitted yet")

        for block in blocks:
            block_code(block)
        if cases:
            tag = self.dispatch_tag
            end = f"ukr{tag}_cases_end"
            code.extend(self.dispatch_code)
            code.extend(lines(gen.jump(label=end)))
            for i, (_, _, case_blocks) in enumerate(cases):
                code.extend(lines(gen.label(label=f"ukr{tag}_case{i}")))
                for block in case_blocks:
                    block_code(block)
                if i + 1 < len(cases):
                    code.extend(lines(gen.jump(label=end)))
            code.extend(lines(gen.label(label=end)))
        return code



def emit_program(ctx, program: ir_program) -> emitted_program:
    """
    Emit a program. Values setup computes once (the vector length in bytes,
    times a stride, constant strides) are allocated where first needed - in a
    case, only that case's register tracker knew their registers, which other
    regions could hand out while setup's values must live in them. Where an
    emission first needed one inside a region, emit again with every such
    value allocated before the regions
    """
    emitter = signature_emitter(ctx, program)
    out = emitter.emit()
    for _ in range(3):
        if not any(late for _, _, late in emitter.recipes):
            return out
        emitter = signature_emitter(ctx, program,
                                    preallocate=[(n, a) for n, a, _ in emitter.recipes])
        out = emitter.emit()
    raise specialization_error("setup's registers kept changing between emissions")
