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
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute)
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

    def instructions(self) -> list[str]:
        """
        Every instruction, in program order, ignoring loop structure
        """
        out = list(self.setup)
        for block in self.blocks + [b for _, _, bs in self.cases for b in bs]:
            for lines in block.sections.values():
                out += lines
            out += block.advance + block.tail_advance
        return out + list(self.teardown) + list(self.data)

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
    return [groups.representative]


def _masked(sig) -> bool:
    return any(orl.MASK == o.orole for o in sig.operands.values())


def _offset_forms(sig) -> str | None:
    """
    "plain" for a signature without an offset, "ioffset" for one taking an
    immediate offset, None for other addressing forms
    """
    mods = {m.name for m in sig.modifiers} - {"MASK"}
    if not mods or ({"GSTRIDE"} == mods and "streg" in sig.operands):
        # a strided access is addressed plainly; its stride register is bound
        # when emitted
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
        except ConstraintDoesNotApplyError:
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
    predicate to govern them
    """
    return not _masked(sig) or _all_true(ctx) is not None


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
            key = (comp, reg, tuple(sorted(strided.items())))
            if key not in self.pointer_regs:
                self.pointer_regs[key] = self.new_reg(comp)
            ptr = self.pointer_regs[key]
            if key not in self.pointers:
                delta = sym._make(strided)
                inserted.append(lsc_addr_compute(comp, reg, ptr, delta, scalar_tile))
                self.positions[(comp, ptr)] = self.positions[(comp, reg)] + delta
                self.pointers.add(key)
            reg = ptr

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

    def __init__(self, ctx, program: ir_program):
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
        # setup instructions found while emitting: vector length in bytes,
        # constant strides
        self.late_setup: list[str] = []
        self.vlb: dict[int, object] = {}
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
        if key not in self.phys:
            dt = self.dts.get((idx.component, idx.indices[0]))
            if rgt.VEC == rtype:
                bound = self.bounds.get(key)
                if bound is None:
                    number = self.rt.reserve_any_reg("vreg")
                else:
                    used = self.rt.get_used_regs("vreg")
                    free = [i for i in range(bound + 1) if i not in used]
                    if not free:
                        raise specialization_error(
                            f"no vector register up to {bound} left for {key[0]}{key[1]}")
                    number = free[0]
                    self.rt.reserve_specific_reg("vreg", number)
                self.phys[key] = self.gen.vreg(number)
            elif rgt.FP == rtype:
                used = self.rt.get_used_regs("vreg")
                number = max(i for i in range(self.gen.max_vregs()) if i not in used)
                self.rt.reserve_specific_reg("vreg", number)
                self.phys[key] = self.gen.freg(number, dt)
            else:
                raise specialization_error(f"{rtype.name} registers are not specialized yet")
            self.numbers[key] = number
        return self.phys[key]

    def _register_bounds(self) -> dict[tuple, int]:
        """
        The highest vector register each virtual register may use, where an
        operation's signature limits it - SVE's indexed fmla encodes its
        indexed register in 4 bits for doubles. Found by asking the
        signature's constraints, so whatever asmgen declares counts.
        """
        bounds: dict[tuple, int] = {}
        top = self.gen.max_vregs() - 1
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
                highest = next((i for i in range(top, -1, -1)
                                if _accepts(sig, hw, self.gen.vreg(i))), -1)
                if highest < top:
                    key = (idx.component, idx.indices[0], rtype)
                    bounds[key] = min(bounds.get(key, highest), highest)
        return bounds

    def release(self, key):
        """
        A virtual register's value is dead: its physical register is free again
        """
        if key in self.phys:
            self.rt.unuse_reg("vreg", self.numbers.pop(key))
            del self.phys[key]

    def greg(self):
        return self.gen.greg(self.rt.reserve_any_reg("greg"))

    # --- addresses ---------------------------------------------------------

    def bytes_of(self, component: str, elements: sym) -> sym:
        return elements * adt_size(self.ctx.component_dts[component])

    def setup_addresses(self) -> list[str]:
        """
        A base register per memory component, to be bound to the kernel's
        arguments, and each address register started at its first access
        """
        lines = []
        self.bases: dict[str, object] = {}
        self.aregs: dict[tuple[str, int], object] = {}
        self.positions: dict[tuple[str, int], sym] = {}
        db, strides = self.program.offsets, self.program.strides
        for (comp, reg), oid in sorted(self.program.addr_setup.items()):
            lines = [l.strip() for l in lines]
            if comp not in self.bases:
                self.bases[comp] = self.greg()
            areg = self.greg()
            self.aregs[(comp, reg)] = areg
            start = db.elements_offset(oid, strides.get(comp, {}))
            self.positions[(comp, reg)] = start
            lines.append(self.gen.mov_greg(src=self.bases[comp], dst=areg))
            lines += self.add_bytes(areg, self.bytes_of(comp, start), comp)
        return [l.strip() for l in lines]

    def stride_reg(self, factor: str):
        """
        The register holding a run-time stride, in bytes: bound to a kernel
        argument like the base addresses
        """
        if factor not in self.strides_in:
            self.strides_in[factor] = self.greg()
        return self.strides_in[factor]

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
                    and coeff > 0 and 0 == coeff % esize and self.vector_length_kept:
                # a vector length of strided elements: vl times the stride in
                # bytes, multiplied once
                key = f"VL*{factors[1]}"
                if key not in self.strides_in:
                    vlreg = self.gen.isa_setup().vector_length_register(rt=self.rt)
                    reg = self.greg()
                    self.strides_in[key] = reg
                    self.late_setup.append(self.gen.mul_greg_greg(
                        dst=reg, reg1=vlreg, reg2=self.stride_reg(factors[1])))
                lines += [self.gen.add_greg_greg(dst=areg, reg1=areg,
                                                 reg2=self.strides_in[key])] * (coeff // esize)
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

    def _predicate(self, sig, kwargs: dict) -> bool:
        """
        Bind a signature's mask operands to the all-true predicate; False if it
        has some and the ISA sets up none
        """
        masks = [n for n, o in sig.operands.items() if orl.MASK == o.orole]
        if not masks:
            return True
        predicate = _all_true(self.ctx, self.rt)
        if predicate is None:
            return False
        for name in masks:
            kwargs[name] = predicate
        return True

    def stride_of(self, op):
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
            return self.stride_reg(list(terms)[0][0])
        if set(terms) <= {()}:
            nbytes = terms.get((), 0) * adt_size(self.ctx.component_dts[comp])
            key = f"constant stride {nbytes}"
            if key not in self.strides_in:
                reg = self.greg()
                self.strides_in[key] = reg
                self.late_setup.append(self.gen.mov_greg_imm(reg=reg, imm=nbytes))
            return self.strides_in[key]
        return None

    def vl_bytes(self, dt):
        """
        A register holding the vector length in bytes, for ISAs keeping the
        vector length in a register (RVV): computed once per element size,
        right after the ISA's setup
        """
        esize = adt_size(dt)
        if esize not in self.vlb:
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
        lines = [self.gen.mov_greg(src=self.aregs[src_key], dst=dest)]
        lines += self.add_bytes(dest, self.bytes_of(comp, op.delta), comp)
        self.positions[dest_key] = self.positions[src_key] + op.delta
        return lines

    def _mem(self, op, data, areg, immediate: int, increment: int | None = None,
             voffset: int | None = None) -> str | None:
        """
        The access through the first signature taking it with this immediate
        offset (0: one without an offset)
        """
        dt = self.ctx.component_dts[op.indices[0].component]
        lane = op.properties.get("lane")
        for sig in sorted(_sigs(op.sigs), key=lambda s: len(s.modifiers)):
            mods = {m.name for m in sig.modifiers} - {"MASK"}
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
            elif {"GSTRIDE"} == mods and not immediate:
                stride = self.stride_of(op)
                if stride is None:
                    continue
                kwargs["streg"] = stride
            elif mods or immediate:
                continue
            if not self._predicate(sig, kwargs):
                continue
            for name, shape in sig.operands.items():
                if ot.IMMEDIATE == shape.otype and name.endswith("_lane"):
                    kwargs[name] = lane
            kwargs.update(sig.structural_params)
            try:
                return getattr(self.gen, op.step.op)(
                    dregs=[data], areg=areg, dt=dt, modifiers=set(sig.modifiers),
                    operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                       if s.modifiers},
                    **kwargs)
            except Exception:       # asmgen refuses: try the next signature
                continue
        return None

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
            try:
                return getattr(self.gen, op.op)(
                    **regs, **dts, **lanes, **masks, **sig.structural_params,
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
        return [line.strip() for line in self._emit_op(op)]

    def _emit_op(self, op) -> list[str]:
        if isinstance(op, (lsc_load, lsc_store)):
            return self.memory(op)
        if isinstance(op, lsc_transformation):
            return [self.compute(op)]
        if isinstance(op, lsc_zero):
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [self.gen.zero_vreg(vreg=reg, dt=self.dts[(op.indices[0].component,
                                                               op.indices[0].indices[0])])]
        if isinstance(op, lsc_addr_compute):
            return self.address(op)
        if isinstance(op, lsc_move):
            return [self.move(op)]
        raise specialization_error(f"cannot emit {type(op).__name__}")

    def move(self, op: lsc_move) -> str:
        """
        A move between registers through the first unmasked signature taking it
        """
        src = self.reg(op.indices[0], op.rtypes[0])
        dst = self.reg(op.indices[1], op.rtypes[1])
        dt = self.dts[(op.indices[1].component, op.indices[1].indices[0])]
        for sig in sorted(_sigs(op.sigs), key=_masked):
            masks = {}
            if not self._predicate(sig, masks):
                continue
            try:
                return self.gen.move(
                    dregs=[src, dst], dts=[dt, dt], modifiers=set(sig.modifiers),
                    **masks, **sig.structural_params,
                    operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                       if s.modifiers})
            except Exception:       # asmgen refuses: try the next signature
                continue
        raise specialization_error(f"no move signature takes {src} into {dst}")

    def block(self, block: ir_block, later: list[ir_block] = ()) -> emitted_block:
        out = emitted_block(name=block.name, loop_index=block.loop_index)
        if block.loop_index is not None:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
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
        # registers an operation limits go first, from the bottom
        for key in sorted(self.bounds, key=self.bounds.get):
            self.reg(lsc_reg_index(key[0], [key[1]]), key[2])
        setup = lines(isa.setup(rt=self.rt, dt=dt))
        self.isa_setup_lines = len(setup)
        setup += self.setup_addresses()
        prefix = self.program.blocks
        case_blocks = [b for c in self.program.cases for b in c.blocks]
        blocks = [self.block(b, prefix[i + 1:] + case_blocks) for i, b in enumerate(prefix)]
        # every case starts with the address and data registers where the blocks
        # before the branch leave them
        start = (dict(self.positions), dict(self.phys), dict(self.numbers), copy.deepcopy(self.rt))
        cases = []
        for c in self.program.cases:
            self.positions, self.phys, self.numbers = dict(start[0]), dict(start[1]), dict(start[2])
            self.rt = copy.deepcopy(start[3])
            cases.append((c.label, c.when,
                          [self.block(b, list(c.blocks[i + 1:])) for i, b in enumerate(c.blocks)]))
        bases = {c: str(r) for c, r in self.bases.items()}
        bases.update({f"{f} in bytes": str(r) for f, r in self.strides_in.items()})
        # what emission found it needs: right after the ISA's setup
        setup = setup[:self.isa_setup_lines] + [l.strip() for l in self.late_setup] \
            + setup[self.isa_setup_lines:]
        return emitted_program(
            setup=setup, blocks=blocks, cases=cases,
            teardown=lines(isa.teardown(rt=self.rt, dt=dt)), data=lines(isa.data()),
            bases=bases,
            registers={k: str(v) for k, v in self.phys.items()})
