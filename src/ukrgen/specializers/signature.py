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

    def instructions(self) -> list[str]:
        """
        Every instruction, in program order, ignoring loop structure
        """
        out = list(self.setup)
        for block in self.blocks + [b for _, _, bs in self.cases for b in bs]:
            for lines in block.sections.values():
                out += lines
            out += block.advance + block.tail_advance
        return out

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
    if not mods:
        return "plain"
    if {"IOFFSET"} == mods and "ioffset" in sig.operands:
        return "ioffset"
    return None


def _takes(sig, immediate: int) -> bool:
    """
    Whether a load or store signature takes an access at this immediate offset
    """
    form = _offset_forms(sig)
    if "plain" == form:
        return 0 == immediate
    if "ioffset" == form:
        for cons in sig.operands["ioffset"].value_constraints:
            lo, hi = getattr(cons, "minval", None), getattr(cons, "maxval", None)
            if lo is not None and not lo <= immediate <= hi:
                return False
            valset = getattr(cons, "valset", None)
            if valset is not None and immediate not in valset:
                return False
        return True
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
        if sigs and all(_masked(s) for s in sigs):
            raise specialization_error(
                f"every {op.step.op} signature for {db[op.offset]} needs a governing "
                f"predicate: masked signatures (SVE, RVV) are not specialized yet")
        rel = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
        inserted = []

        strided = {f: c for f, c in rel.items() if f}
        if strided:
            for factors, count in strided.items():
                if len(factors) != 1 or not factors[0].startswith("stride(") or count < 0:
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
        usable = [s for s in sigs if not _masked(s)]
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
            if sigs and all(_masked(s) for s in sigs):
                raise specialization_error(
                    f"every {op.op} signature needs a governing predicate: masked "
                    f"signatures (SVE, RVV) are not specialized yet")
        if isinstance(op, lsc_move):
            raise specialization_error("moves between registers are not specialized yet")
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
        self.rt = reg_tracker([("greg", self.gen.max_gregs), ("vreg", self.gen.max_vregs)])
        self.phys: dict[tuple, object] = {}
        self.dts: dict[tuple, object] = self._register_types()
        self.fp_next = self.gen.max_vregs - 1
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
                self.phys[key] = self.gen.vreg(self.rt.reserve_any_reg("vreg"))
            elif rgt.FP == rtype:
                while self.fp_next in self.rt.get_used_regs("vreg"):
                    self.fp_next -= 1
                self.rt.reserve_specific_reg("vreg", self.fp_next)
                self.phys[key] = self.gen.freg(self.fp_next, dt)
                self.fp_next -= 1
            else:
                raise specialization_error(f"{rtype.name} registers are not specialized yet")
        return self.phys[key]

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
        esize = adt_size(self.ctx.component_dts[comp])
        lines = []
        for factors, coeff in amount.terms:
            if not factors:
                lines.append(self.gen.add_greg_imm(reg=areg, imm=coeff))
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
        if set(rel) - {()}:
            raise specialization_error(
                f"{op.rsln} access to {self.program.offsets[op.offset]} is not a constant "
                f"offset from its address register: specialize the IR first")
        immediate = rel.get((), 0) * adt_size(self.ctx.component_dts[comp])
        line = self._mem(op, self.reg(op.indices[1], op.rtypes[1]), areg, immediate)
        if line is None:
            raise specialization_error(
                f"no signature of {op.step.op} takes {self.program.offsets[op.offset]} at "
                f"offset {immediate}: specialize the IR first")
        return [line]

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

    def _mem(self, op, data, areg, immediate: int) -> str | None:
        """
        The access through the first signature taking it with this immediate
        offset (0: one without an offset)
        """
        dt = self.ctx.component_dts[op.indices[0].component]
        lane = op.properties.get("lane")
        for sig in sorted(_sigs(op.sigs), key=lambda s: len(s.modifiers)):
            mods = {m.name for m in sig.modifiers} - {"MASK"}
            kwargs = {}
            if {"IOFFSET"} == mods:
                kwargs["ioffset"] = immediate
            elif mods or immediate:
                continue
            if any(orl.MASK == o.orole for o in sig.operands.values()):
                continue
            for name, shape in sig.operands.items():
                if ot.IMMEDIATE == shape.otype and name.endswith("_lane"):
                    kwargs[name] = lane
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
        for sig in _sigs(op.resolution.compute_sg):
            if any(orl.MASK == o.orole for o in sig.operands.values()):
                continue
            dts = {f"{hw[0]}_dt": sig.operands[hw].dt for hw in op.hw_operands}
            try:
                return getattr(self.gen, op.op)(
                    **regs, **dts, **lanes, modifiers=set(sig.modifiers),
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
            raise specialization_error("moves between registers are not specialized yet")
        raise specialization_error(f"cannot emit {type(op).__name__}")

    def block(self, block: ir_block) -> emitted_block:
        out = emitted_block(name=block.name, loop_index=block.loop_index)
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            out.sections[section] = [line for op in getattr(block, section)
                                     for line in self.emit_op(op)]
        db, strides = self.program.offsets, self.program.strides
        for comp, oid in block.advance.items():
            step = self.bytes_of(comp, db.elements_offset(oid, strides.get(comp, {})))
            for (c, reg), areg in sorted(self.aregs.items(), key=lambda x: x[0]):
                if c == comp:
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
        setup = self.setup_addresses()
        blocks = [self.block(b) for b in self.program.blocks]
        # every case starts with the address registers where the blocks before
        # the branch leave them
        start = dict(self.positions)
        cases = []
        for c in self.program.cases:
            self.positions = dict(start)
            cases.append((c.label, c.when, [self.block(b) for b in c.blocks]))
        bases = {c: str(r) for c, r in self.bases.items()}
        bases.update({f"{f} in bytes": str(r) for f, r in self.strides_in.items()})
        return emitted_program(
            setup=setup, blocks=blocks, cases=cases,
            bases=bases,
            registers={k: str(v) for k, v in self.phys.items()})
