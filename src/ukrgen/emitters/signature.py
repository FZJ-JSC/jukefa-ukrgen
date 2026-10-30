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

import functools

from dataclasses import dataclass, field

from asmgen.asmblocks.op.constraint import ArgumentDependencyError
from asmgen.callconv.fngen import fngen
from . import asmops
from ..support.domains import operand_values
from ..support.data_move import operand_side
from ..support.tiles import widening_ways
from asmgen.asmblocks.noarch import comparison
from asmgen.asmblocks.op import (
    register_type as rgt,
    operand_role as orl,
    operand_type as ot,
    opmem_modifier as memmod,
    operand_modifier as opd_mod,
)
from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.registers import adt_size, asm_data_type as adt
from asmgen.asmblocks.op.constraint import ConstraintDoesNotApplyError

from ..lsc_model.state import merge_switches
from ..lsc_model.addressing import sym
from ..lsc_model.ir import ir_program, ir_block
from ..components.tile import scalar_tile
from ..models.load_store_operations import (lsc_state, 
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute, lsc_loop, lsc_permute)
from ..models.lsc.index import lsc_reg_index


from ..specializers.signature import (
    specialization_error, _sigs, _masked, _offset_forms, _accepts, _all_true, _usable, _vl_form, _takes,
)

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
    #: the generator the program is for: it frames the function (fngen)
    gen : object = None

    def instructions(self, data : bool = True) -> list[str]:
        """
        Every instruction, in program order, ignoring loop structure; then
        the data the program keeps, unless data is False
        """
        kept = list(self.data) if data else []
        out = list(self.setup)
        if self.code:
            return list(self.entry) + out + list(self.code) + list(self.teardown) \
                + list(self.exit) + kept
        for block in self.blocks + [b for _, _, bs in self.cases for b in bs]:
            for lines in block.sections.values():
                out += lines
            out += block.advance + block.tail_advance
        return out + list(self.teardown) + kept

    def function(self, name: str, *, align: int | None = None, offset: int = 0) -> list[str]:
        """
        The program as an assembly function, as asmgen frames one (fngen:
        section, alignment, .global, .type, the label, the instructions,
        .size, the data) - then what the file says once, the GNU-stack note

        :param align: the function's alignment in bytes, if any
        :param offset: where it starts past that boundary, in bytes
        """
        from asmgen.callconv.fngen import fngen  # pylint: disable=import-outside-toplevel
        if self.gen is None:
            raise ValueError("the program has no generator to frame it")
        body = "".join(f"{l}\n" for l in self.instructions(data=False))
        data = "".join(f"{l}\n" for l in self.data)
        text = fngen(self.gen).function(name, body, align=align, offset=offset, data=data)
        return (text + self.gen.asmfile_annotations()).splitlines()

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


class offset_planner:
    """
    How an address offset is formed - every decision in one place: a
    register holding the vector length in bytes or k of them, VL squared,
    strides times the vector length or constants, computed once at the
    kernel's start; an address moved by an amount - shifted adds for stride
    multiples, one add of a register holding k vector lengths. The emitter
    asks; the planner keeps what it allocated (docs/REG_USE_OPTIMIZATION.md:
    step 2b - moved here as it was, to be extended)
    """

    def __init__(self, emitter):
        self.e = emitter

    def stride_reg(self, factor: str, setup: bool = False):
        """
        The register holding a run-time stride in bytes: its parameter's
        """
        return self.e.params[factor]

    def add_scaled(self, areg, source, n: int) -> list[str]:
        """
        areg moved by n times a register's amount, n negative backwards: an
        add or sub per set bit of n - shifted where the ISA shifts the operand
        (AArch64 add x, x, y, LSL #s; x86 lea): 2*VL*VL one instruction off a
        register holding VL*VL - plain adds or subs repeated where it doesn't
        """
        op = "sub" if n < 0 else "add"
        plain = functools.partial(asmops.arith, self.e.gen, op)
        shifted = functools.partial(asmops.shifted, self.e.gen, op)
        out, k, bit = [], abs(n), 0
        while k:
            if k & 1:
                if not bit:
                    out.append(plain(dst=areg, reg1=areg, reg2=source))
                elif self.e.shifted_available(op, bit):
                    out.append(shifted(dst=areg, reg1=areg, reg2=source, shift=bit))
                else:
                    out += [plain(dst=areg, reg1=areg, reg2=source)] * (1 << bit)
            k >>= 1
            bit += 1
        return out

    def add_bytes(self, areg, amount: sym, comp: str) -> list[str]:
        """
        Move an address register on by a number of bytes: constants as an
        immediate; whole vectors with incb/decb where the ISA counts them so;
        multiples of a register's amount - strides, the vector length (RVV),
        vector lengths of strides or of vectors, each held in bytes - as
        shifted or repeated adds and subs of it (add_scaled)
        """
        dt = self.e.ctx.component_dts[comp]
        esize = adt_size(dt)
        lines = []
        for factors, coeff in amount.terms:
            if not factors:
                lines.append(asmops.add_imm(self.e.gen, reg=areg, imm=coeff))
                continue
            if 0 != coeff % esize:
                raise specialization_error(
                    f"moving {comp}'s address by {amount} bytes: {coeff} isn't whole elements")
            n = coeff // esize
            if ("VL",) == factors and not self.e.vector_length_kept:
                # whole vectors, forward or back: incb or decb
                lines.append(asmops.add_vectors(self.e.gen, reg=areg, offset=n))
                continue
            if ("VL",) == factors and n > 1:
                # RVV: k vector lengths in a register of their own - one add
                lines.append(asmops.add(self.e.gen, dst=areg, reg1=areg, reg2=self.vl_multiple(dt, n)))
                continue
            if ("VL",) == factors:
                # RVV: the vector length in a register, in bytes
                source = self.vl_bytes(dt)
            elif 1 == len(factors) and factors[0].startswith("stride("):
                source = self.stride_reg(factors[0])
            elif 2 == len(factors) and "VL" == factors[0] and factors[1].startswith("stride("):
                # a vector length of strided elements, multiplied once
                source = self.vl_stride(factors[1], dt)
            elif ("VL", "VL") == factors:
                # vector lengths of vectors: a packed layout's next tile
                source = self.vl_squared(dt)
            else:
                raise specialization_error(
                    f"moving {comp}'s address by {amount} bytes needs run-time arithmetic "
                    f"(vector length), which is not specialized yet")
            lines += self.add_scaled(areg, source, n)
        return lines

    # --- operations ----------------------------------------------------------

    def vl_elements(self, dt):
        """
        A register holding the vector length in elements: RVV's vl, or read
        once after the ISA's setup where the ISA doesn't keep it (SVE: cntd)
        """
        if self.e.vector_length_kept:
            return self.e.gen.isa_setup().vector_length_register(rt=self.e.rt)
        key = f"VL in {adt_size(dt)}-byte elements"
        if key not in self.e.strides_in:
            self.e.recipes.append(("vl_elements", (dt,), self.e.regions_started))
            reg = self.e.greg()
            call = dict(dreg=reg, dt=dt, modifiers={opset_modifier.VLEN})
            why = self.e.gen.set.refusal(**call)
            if why:
                raise specialization_error(f"reading the vector length: {why}")
            self.e.late_setup.append(self.e.gen.set(**call))
            self.e.strides_in[key] = reg
        return self.e.strides_in[key]

    def vl_stride(self, factor: str, dt):
        """
        A register holding the vector length in elements times a stride in
        bytes: a vector length of strided elements, multiplied once in setup
        """
        key = f"VL*{factor}"
        if key not in self.e.strides_in:
            self.e.recipes.append(("vl_stride", (factor, dt), self.e.regions_started))
            vlreg = self.vl_elements(dt)
            reg = self.e.greg()
            self.e.strides_in[key] = reg
            self.e.late_setup.append(asmops.mul(self.e.gen, 
                dst=reg, reg1=vlreg, reg2=self.stride_reg(factor, setup=True)))
        return self.e.strides_in[key]

    def constant_stride(self, nbytes: int):
        """
        A register holding a constant stride, loaded once in setup
        """
        key = f"constant stride {nbytes}"
        if key not in self.e.strides_in:
            self.e.recipes.append(("constant_stride", (nbytes,), self.e.regions_started))
            reg = self.e.greg()
            self.e.strides_in[key] = reg
            self.e.late_setup.append(asmops.set_imm(self.e.gen, reg=reg, imm=nbytes))
        return self.e.strides_in[key]

    def vl_squared(self, dt):
        """
        A register holding the vector length squared, in elements, times the
        element size in bytes: a vector length of vectors - the next tile
        along a packed layout's outer index - multiplied once in setup
        """
        key = f"VL*VL:{adt_size(dt)}"
        if key not in self.e.strides_in:
            self.e.recipes.append(("vl_squared", (dt,), self.e.regions_started))
            vlreg = self.vl_elements(dt)
            reg = self.e.greg()
            self.e.strides_in[key] = reg
            self.e.late_setup += [asmops.mul(self.e.gen, dst=reg, reg1=vlreg, reg2=vlreg),
                                asmops.shift_left(self.e.gen, reg=reg,
                                                         bit_count=adt_size(dt).bit_length() - 1)]
        return self.e.strides_in[key]

    def vl_bytes(self, dt):
        """
        A register holding the vector length in bytes, for ISAs keeping the
        vector length in a register (RVV): computed once per element size,
        right after the ISA's setup
        """
        esize = adt_size(dt)
        if esize not in self.e.vlb:
            self.e.recipes.append(("vl_bytes", (dt,), self.e.regions_started))
            vlreg = self.e.gen.isa_setup().vector_length_register(rt=self.e.rt)
            reg = self.e.greg()
            self.e.vlb[esize] = reg
            self.e.late_setup += [asmops.mov(self.e.gen, src=vlreg, dst=reg),
                                asmops.shift_left(self.e.gen, reg=reg, bit_count=esize.bit_length() - 1)]
        return self.e.vlb[esize]

    def vl_multiple(self, dt, k: int):
        """
        A register holding k vector lengths in bytes (RVV): an address moves
        by k vectors in one add - computed once, right after the ISA's setup
        """
        if 1 == k:
            return self.vl_bytes(dt)
        key = (adt_size(dt), k)
        if key not in self.e.vlm:
            self.e.recipes.append(("vl_multiple", (dt, k), self.e.regions_started))
            base = self.vl_bytes(dt)
            reg = self.e.greg()
            self.e.vlm[key] = reg
            if 0 == k & (k - 1):
                self.e.late_setup += [asmops.mov(self.e.gen, src=base, dst=reg),
                                    asmops.shift_left(self.e.gen, reg=reg, bit_count=k.bit_length() - 1)]
            else:
                self.e.late_setup += [asmops.mov(self.e.gen, src=base, dst=reg)] + \
                    [asmops.add(self.e.gen, dst=reg, reg1=reg, reg2=base) for _ in range(k - 1)]
        return self.e.vlm[key]

    def vector_multiple(self, amount, comp: str) -> int | None:
        """
        k where an amount of bytes is k whole vector lengths (k > 0) and the
        ISA keeps the vector length in a register; else None
        """
        if not self.e.vector_length_kept:
            return None
        terms = list(amount.terms)
        if 1 != len(terms) or ("VL",) != tuple(terms[0][0]):
            return None
        esize = adt_size(self.e.ctx.component_dts[comp])
        coeff = terms[0][1]
        return coeff // esize if coeff > 0 and 0 == coeff % esize else None


class signature_emitter:
    """
    Turns one part's specialized IR program into assembly

    :param ctx: context after the model stage
    :param program: the program to specialize
    """

    #: shifted operands' forms asked of the operations, by (op, shift)
    shifted_known: dict | None = None

    def __init__(self, ctx, program: ir_program, preallocate=(), keep_params=()):
        self.ctx = ctx
        self.gen = ctx.gen
        self.program = program
        # the generator's tracker keeps the stack pointer and the like out of
        # reach; older generators don't provide one
        self.rt = self.gen.get_reg_tracker()
        self.phys: dict[tuple, object] = {}
        self.dts: dict[tuple, object] = self._register_types()
        self.numbers: dict[tuple, int] = {}
        self.bounds = self._register_bounds()
        self._required_priorities()
        # setup instructions found while emitting: vector length in bytes,
        # constant strides
        self.late_setup: list[str] = []
        self.vlb: dict[int, object] = {}
        #: (element size, k) -> a register holding k vector lengths in bytes
        self.vlm: dict[tuple, object] = {}
        #: how address offsets are formed
        self.offsets = offset_planner(self)
        self.masks: dict = {}
        self.indexes: dict = {}
        # setup-time values a previous emission found it needed: allocated
        # before any region, in the tracker every region inherits
        self.preallocate = list(preallocate)
        #: stack parameters needed before the dispatch (setup's values):
        #: loaded at entry, not deferred
        self.keep_params = set(keep_params)
        #: the last vectors' masks and, for the vl route, the full vector
        #: length's registers (tailmask): set up by the setup
        self.tails: dict = {}
        self.tail_vl: dict = {}
        self.recipes: list[tuple[str, tuple, bool]] = []
        self.regions_started = False
        self.region_loads: list[str] = []
        self.labels = iter(range(10**6))
        isa = self.gen.isa_setup()
        self.vector_length_kept = isa.predication().name == "IMPLICIT"
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
        parts = group[2] if group is not None and len(group) > 2 else None
        if key not in self.phys and parts is not None and rgt.VEC == rtype:
            # a group's parts each a group of its own (structfuse): a part's
            # registers consecutive wherever there's room, its rows wherever
            # its first is; a register in none ungrouped
            part = next(((s, n) for s, n in parts.items() if s <= idx.indices[0] < s + n), None)
            if part is not None:
                first, size = part
                used = self.rt.get_used_regs("vreg")
                start = next((s for s in range(0, self.gen.max_vregs() - size + 1)
                              if not any(s + p in used for p in range(size))), None)
                if start is None:
                    raise specialization_error(f"no {size} consecutive vector registers left for "
                                               f"{idx.component}{first}")
                for p in range(size):
                    self.rt.reserve_specific_reg("vreg", start + p)
                    member = (idx.component, first + p, rtype)
                    self.phys[member] = self.gen.vreg(start + p)
                    self.numbers[member] = ("vreg", start + p)
        elif key not in self.phys and group is not None and rgt.VEC == rtype:
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
                    if not self.rt.available("vreg"):
                        raise specialization_error(
                            f"{key[0]}: no vector register left - the accumulators, the data "
                            f"registers and a loop's unrolled copies (unroll_loops' factor and "
                            f"registers) take them all; scheduling (--mru) renames tiles "
                            f"streamed through straight-line code into the registers free, "
                            f"fewer register sets or data registers fit")
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
            elif rgt.FP == rtype and "freg" in self.rt.shared:
                # the tracker knows which vector registers FP registers are
                number = self.rt.reserve_any_reg("freg")
                tag = "freg"
                self.phys[key] = self.gen.freg(number, dt)
            elif rgt.FP == rtype and "freg" in self.rt.registered_types:
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
                # the element type's tiles, or fewer where max-tiles says so
                tiles = self.gen.max_tregs(dt)
                cap = self.ctx.params.get("max-tiles")
                cap = int(cap.value or 0) if cap is not None else 0
                tiles = min(tiles, cap) if cap > 0 else tiles
                if "treg" not in self.rt.registered_types:
                    self.rt.add_type("treg", tiles)
                if not self.rt.available("treg"):
                    raise specialization_error(
                        f"{key[0]}: no tile left - {dt.name} has {self.gen.max_tregs(dt)} tiles"
                        f"{f', max-tiles {cap}' if cap > 0 else ''}, "
                        f"all taken; fusing the loops over slices (fuse_slices, forward_slices) "
                        f"keeps tiles out of use, or a smaller microtile needs fewer")
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
            groups = [(op.resolution.compute_sg if op.resolution is not None else None), op.sigs]
            for sig in (s for g in groups if g for s in _sigs(g)):
                for name, shape in sig.operands.items():
                    if ot.REGISTER != shape.otype or shape.rtype not in files or \
                            not shape.value_constraints:
                        continue
                    tag, count = files[shape.rtype]
                    if tag not in self.rt.registered_types:
                        continue
                    try:
                        allowed = operand_values(sig, name, universe=range(count)).values
                    except ArgumentDependencyError:
                        continue
                    if len(allowed) < count:
                        # below callee-saved registers' -1
                        for n in allowed:
                            self.rt.set_priority(tag, n, min(-2, self.rt.priority(tag, n)))

    def operand_comps(self, blocks) -> set[str]:
        """
        The components the blocks' operations use as operands - a loop's
        block too
        """
        comps = set()
        def scan(ops):
            for op in ops:
                for idx in op.indices or ():
                    comp = idx.component
                    if comp is not None:
                        comps.add(comp)
                if op.block:
                    scan(op.block)
        for block in blocks:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                scan(getattr(block, section, None) or ())
        return comps

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

    def stride_reg(self, *args, **kwargs):
        return self.offsets.stride_reg(*args, **kwargs)

    def add_scaled(self, *args, **kwargs):
        return self.offsets.add_scaled(*args, **kwargs)

    def shifted_available(self, op: str, shift: int) -> bool:
        """
        Whether the ISA adds or subtracts a register shifted by shift in one
        instruction: asked once - a generator raises NotImplementedError where
        it doesn't - and remembered
        """
        if self.shifted_known is None:
            self.shifted_known = {}
        known = self.shifted_known
        if (op, shift) not in known:
            reg = self.gen.greg(0)
            known[(op, shift)] = getattr(self.gen, op).fits(
                adreg=reg, bdreg=reg, cdreg=reg, a_dt=adt.UINT64, b_dt=adt.UINT64, c_dt=adt.UINT64,
                operand_modifiers={"bdreg": {opd_mod.ISHIFT}}, bdreg_shift=shift) is not None
        return known[(op, shift)]

    def add_bytes(self, *args, **kwargs):
        return self.offsets.add_bytes(*args, **kwargs)

    def slices(self, op) -> list[str]:
        """
        A loop over a tile's slices, as many as it has rows or columns at run
        time: the slice index in a register every slice operand takes (SME:
        w12-w15), counting up - an unrolled iteration's slices at its
        immediates; a walking pointer per memory access, from its first
        slice's address, by its step; every operation of the block for each
        slice - tile slice accesses and moves at the slice index, memory
        accesses at their pointers, the rest as anywhere
        """
        comp = op.info.get("component") or op.walks[0].anchor.indices[0].component
        dt = self.ctx.component_dts[comp]
        sliced = [b for b in op.block if b.sigs is not None and
                  any(n.endswith(("_rowreg", "_colreg")) for s in _sigs(b.sigs) for n in s.operands)]
        allowed = set(range(self.gen.max_gregs()))
        for b in sliced:
            for sig in _sigs(b.sigs):
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
        counter = self.greg()
        lines = [asmops.mov(self.gen, src=self.slice_count(op, dt), dst=counter),
                 asmops.set_imm(self.gen, reg=index, imm=0)]
        # explicit copies in the block (unroll_loops): emitted once an
        # iteration, every pointer stepping by the unroll; a step register
        # shared by walks of the same step
        explicit = op.info.get("unrolled")
        scale = op.subtiling.unroll if explicit else 1
        plan = op.walk_plan

        # the plan's registers walk themselves: where each stands, as an offset
        # from its home at this iteration's first slice
        current = {key: sym.const(0) for key in plan} if plan else {}
        walk_of = {w: key for key, p in (plan or {}).items() for w in p["walks"]}
        # within the general registers allowed (--loop-gregs), a pointer per
        # access column - an offset's part beside vector lengths; tiles a
        # vector length apart share one, the rest an immediate - set before
        # the loop, stepped once an iteration: no moves between tiles. The
        # first column of a plan register is that register
        columns, pointers, column_of = {}, {}, {}
        if plan:
            accesses = {}
            for b in op.block:
                if isinstance(b, (lsc_load, lsc_store)):
                    accesses.setdefault(b.properties.get("walk", 0), []).append(b)
            for key, p in plan.items():
                for w, offset in p["walks"].items():
                    vectors = dict(offset.terms).get(("VL",))
                    # the vector lengths an immediate only where every access
                    # of the walk takes them
                    folds = vectors and all(any(_vl_form(sig) and _accepts(sig, "voffset", vectors)
                                                for sig in _sigs(b.sigs))
                                            for b in accesses.get(w, []))
                    column = sym._make({f: c for f, c in dict(offset.terms).items()
                                        if not (folds and ("VL",) == f)})
                    column_of[w] = (key, str(column), dict(offset.terms).get(("VL",)) if folds else None)
                    columns.setdefault((key, str(column)), (key, column))
            extra = len(columns) - len(plan)
            budget = self.ctx.loop_gregs
            if budget is None or 2 + extra <= budget:
                for (key, name), (_, column) in columns.items():
                    pointers[(key, name)] = None if not dict(column.terms) else column
        def place(b):
            # the access where the register stands, or vector lengths past it
            # where a signature takes them ([x, #n, MUL VL]): no move; else the
            # register moved there
            w = b.properties.get("walk", 0)
            key = walk_of[w]
            comp = key[0]
            target = plan[key]["walks"][w]
            if pointers:
                # its column's own pointer, the vector lengths an immediate
                _, name, vectors = column_of[w]
                return [], pointer_regs[(key, name)], vectors
            rest = dict((target - current[key]).terms)
            if not rest:
                return [], self.aregs[key], None
            vectors = rest.get(("VL",))
            if vectors and any(_vl_form(sig) and _accepts(sig, "voffset", vectors)
                               for sig in _sigs(b.sigs)):
                # the register moved by the rest alone (another column), the
                # vector lengths an immediate
                others = {f: c for f, c in rest.items() if ("VL",) != f}
                out = []
                if others:
                    move = sym._make(others)
                    out = self.add_bytes(self.aregs[key], self.bytes_of(comp, move), comp)
                    current[key] = current[key] + move
                return out, self.aregs[key], vectors
            out = self.add_bytes(self.aregs[key], self.bytes_of(comp, target - current[key]), comp)
            current[key] = target
            return out, self.aregs[key], None
        def step_on(slices):
            # every register to the next iteration's home, slices on
            out = []
            if pointers:
                for (key, name), ptr in pointer_regs.items():
                    step = sym._make({f: c * slices for f, c in dict(plan[key]["step"].terms).items()})
                    out += self.add_bytes(ptr, self.bytes_of(key[0], step), key[0])
                return out
            for key, p in (plan or {}).items():
                move = sym._make({f: c * slices for f, c in dict(p["step"].terms).items()}) - current[key]
                if dict(move.terms):
                    out += self.add_bytes(self.aregs[key], self.bytes_of(key[0], move), key[0])
                current[key] = sym.const(0)
            return out
        def release_pointers():
            for (key, name), ptr in pointer_regs.items():
                if ptr is not self.aregs[key]:
                    self.rt.unuse_reg("greg", ptr.idx)
        def settle() -> list[str]:
            # where the loop leaves them - a vector length of steps on; the
            # specializer's address computations after it step them back home
            for key, p in (plan or {}).items():
                self.positions[key] = p["home"] + sym._make(
                    {tuple(sorted(("VL",) + f)): c for f, c in dict(p["step"].terms).items()})
            return []
        walkers, deltas, steps, shared = [], [], {}, {}
        for walk in ([] if plan else op.walks):
            anchor = walk.anchor
            wcomp, wreg = anchor.indices[0].component, anchor.indices[0].indices[0]
            elements = self.program.offsets.elements_offset(
                anchor.offset, self.program.strides.get(wcomp, {}))
            terms = dict(walk.step.terms)
            wdt = self.ctx.component_dts[wcomp]
            key = (tuple(sorted(terms.items())), adt_size(wdt))
            # a pointer shared by walks of one component from the same element
            # by the same step: a tile's load and store of C
            start = (wcomp, str(elements), key)
            if start in shared:
                walkers.append(shared[start])
                deltas.append(steps[key])
                continue
            if not self.rt.available("greg"):
                raise specialization_error(
                    f"{op.info.get('component')}: a loop over slices needs a walking pointer for "
                    f"each of {len({(w.anchor.indices[0].component, str(w.anchor.offset)) for w in op.walks})} "
                    f"tile accesses and copies - more than the general registers left; a smaller "
                    f"unroll needs fewer")
            walker = self.greg()
            shared[start] = walker
            lines.append(asmops.mov(self.gen, src=self.aregs[(wcomp, wreg)], dst=walker))
            lines += self.add_bytes(walker, self.bytes_of(wcomp, elements - self.positions[(wcomp, wreg)]), wcomp)
            if key not in steps:
                delta = self.greg()
                if not terms or set(terms) == {()}:
                    lines.append(asmops.set_imm(self.gen, reg=delta, imm=terms.get((), 0) * adt_size(wdt) * scale))
                elif scale > 1:
                    lines.append(asmops.mul_imm(self.gen, src=self.stride_reg(next(iter(terms))[0]),
                                                       dst=delta, factor=scale))
                else:
                    lines.append(asmops.mov(self.gen, src=self.stride_reg(next(iter(terms))[0]), dst=delta))
                steps[key] = delta
            walkers.append(walker)
            deltas.append(steps[key])
        pointer_regs = {}
        for (key, name), column in pointers.items():
            if column is None:
                pointer_regs[(key, name)] = self.aregs[key]
                continue
            ptr = self.greg()
            lines.append(asmops.mov(self.gen, src=self.aregs[key], dst=ptr))
            lines += self.add_bytes(ptr, self.bytes_of(key[0], column), key[0])
            pointer_regs[(key, name)] = ptr
        loop = f"ukr{next(self.labels)}_slices"
        lines.append(self.gen.label(label=loop))
        unroll = op.subtiling.unroll
        # the block's own vector temporaries - written before read - rotate
        # through as many register sets as asked: an unrolled iteration's
        # slices don't wait on each other's registers
        rotate = 1 if explicit else max(1, min(op.subtiling.registers, unroll))
        def keys(b, positions):
            types = b.rtypes or []
            return [(b.indices[p].component, b.indices[p].indices[0], types[p] if p < len(types) else None)
                    for p in positions]
        local, read = [], set()
        for b in op.block:
            read |= set(keys(b, b.reads))
            for k in keys(b, b.writes):
                if rgt.VEC == k[2] and k not in read and k not in local:
                    local.append(k)
        sets = [{} for _ in range(rotate)]
        # software pipelined (preload): the first copy's loads - memory loads,
        # slices moved out of tiles - before the loop and, for the next
        # iteration, at the end of each; the last iteration without them
        preload = int(op.info.get("preload") or 0) if explicit else 0
        def early(b):
            return b.properties.get("copy", 0) < preload and (
                (isinstance(b, lsc_load) and b in op.block) or
                (isinstance(b, lsc_move) and "slice" in b.properties and rgt.TILE == b.rtypes[0]))
        def emit_ops(ops):
            out = []
            for b in ops:
                if b in sliced:
                    b.properties.update(slice_reg=index, slice_imm=b.properties.get("copy", 0))
                if isinstance(b, (lsc_load, lsc_store)):
                    vectors = None
                    if plan:
                        moves, walker, vectors = place(b)
                        out += moves
                    else:
                        walker = walkers[b.properties.get("walk", 0)]
                    line = self._mem(b, self.reg(b.indices[1], b.rtypes[1]), walker, 0,
                                     voffset=vectors)
                    if line is None:
                        raise specialization_error(f"{op.info.get('component')}: no {b.step.op} "
                                                   f"of a slice's {b.indices[0].component} takes "
                                                   f"a plain address")
                    out.append(line)
                elif isinstance(b, lsc_move):
                    out.append(self.move(b))
                else:
                    out += self._emit_op(b)
            return out
        def advance():
            if plan:
                out = step_on(unroll)
            else:
                out = [asmops.add(self.gen, dst=w, reg1=w, reg2=d)
                       for w, d in {w.idx: (w, d) for w, d in zip(walkers, deltas)}.values()]
            return out + [asmops.add_imm(self.gen, reg=index, imm=unroll)]
        if preload:
            first = [b for b in op.block if early(b)]
            rest = [b for b in op.block if not early(b)]
            last = f"{loop}_last"
            # the label emitted above starts the steady state; the first
            # loads go before it, the count is the slices after the last group
            label_line = lines.pop()
            lines += emit_ops(first)
            lines.append(asmops.add_imm(self.gen, reg=counter, imm=-unroll))
            lines.append(self.gen.cb(reg1=counter, reg2=None, cmp=comparison.EZ, label=last))
            lines.append(label_line)
            lines += emit_ops(rest) + advance() + emit_ops(first)
            lines.append(asmops.add_imm(self.gen, reg=counter, imm=-unroll))
            lines.append(self.gen.cb(reg1=counter, reg2=None, cmp=comparison.NZ, label=loop))
            lines.append(self.gen.label(label=last))
            lines += emit_ops(rest)
            for r in [counter, index] + list(shared.values()) + list(steps.values()):
                self.rt.unuse_reg("greg", r.idx)
            release_pointers()
            lines += settle()
            return [l.strip() for chunk in lines for l in (chunk.splitlines() if isinstance(chunk, str) else chunk)
                if l.strip()]
        for u in range(1 if explicit else unroll):
            group = u % rotate
            saved = {}
            if group:
                for k in local:
                    if k not in self.phys:
                        continue
                    if k not in sets[group]:
                        n = self.rt.reserve_any_reg("vreg")
                        sets[group][k] = (n, self.gen.vreg(n))
                    saved[k] = self.phys[k]
                    self.phys[k] = sets[group][k][1]
            for b in op.block:
                if b in sliced:
                    b.properties.update(slice_reg=index,
                                        slice_imm=b.properties.get("copy", 0) if explicit else u)
                if isinstance(b, (lsc_load, lsc_store)):
                    vectors = None
                    if plan:
                        moves, walker, vectors = place(b)
                        lines += moves
                    else:
                        walker = walkers[b.properties.get("walk", 0)]
                    line = self._mem(b, self.reg(b.indices[1], b.rtypes[1]), walker, 0,
                                     voffset=vectors)
                    if line is None:
                        raise specialization_error(f"{op.info.get('component')}: no {b.step.op} "
                                                   f"of a slice's {b.indices[0].component} takes "
                                                   f"a plain address at slice immediate {u}")
                    lines.append(line)
                elif isinstance(b, lsc_move):
                    lines.append(self.move(b))
                else:
                    lines += self._emit_op(b)
            if plan:
                # explicit copies are in the block: an iteration takes unroll
                # slices; otherwise each copy one
                lines += step_on(unroll if explicit else 1)
            else:
                for walker, delta in {w.idx: (w, d) for w, d in zip(walkers, deltas)}.values():
                    lines.append(asmops.add(self.gen, dst=walker, reg1=walker, reg2=delta))
            self.phys.update(saved)
        for group in sets:
            for n, _ in group.values():
                self.rt.unuse_reg("vreg", n)
        lines.append(asmops.add_imm(self.gen, reg=index, imm=unroll))
        lines.append(asmops.add_imm(self.gen, reg=counter, imm=-unroll))
        lines.append(self.gen.cb(reg1=counter, reg2=None, cmp=comparison.NZ, label=loop))
        for r in [counter, index] + list(shared.values()) + list(steps.values()):
            self.rt.unuse_reg("greg", r.idx)
        release_pointers()
        lines += settle()
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
        lines = [asmops.mov(self.gen, src=self.aregs[(comp, reg)], dst=walker)]
        lines += self.add_bytes(walker, self.bytes_of(comp, start), comp)
        lines.append(asmops.mov(self.gen, src=self.slice_count(op, dt), dst=counter))
        # the walk's step, the element stride in bytes - negative where a fill
        # shifts up (SVE insr, into lane 0): from the last element backwards
        stride = op.walks[0].step
        terms = dict(stride.terms)
        up = op.subtiling.order < 0
        if set(terms) == {()}:
            nbytes = terms[()] * adt_size(dt)
            lines.append(asmops.set_imm(self.gen, reg=delta, imm=-nbytes if up else nbytes))
        elif 1 == len(terms) and 1 == len(next(iter(terms))) and 1 == next(iter(terms.values())):
            source = self.stride_reg(next(iter(terms))[0])
            lines.append(asmops.mul_imm(self.gen, src=source, dst=delta, factor=-1) if up
                         else asmops.mov(self.gen, src=source, dst=delta))
        else:
            raise specialization_error(f"{op.rsln}: walking {comp} by {stride} elements")
        if up:
            # the last element: a vector length of strides on, one back
            lines += self.add_bytes(walker, self.bytes_of(comp, sym._make(
                {tuple(sorted(("VL",) + f)): c for f, c in terms.items()})), comp)
            lines.append(asmops.add(self.gen, dst=walker, reg1=walker, reg2=delta))
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
                    lines.append(asmops.add(self.gen, dst=walker, reg1=walker, reg2=delta))
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
                lines.append(asmops.add(self.gen, dst=walker, reg1=walker, reg2=delta))
        lines.append(asmops.add_imm(self.gen, reg=counter, imm=-unroll))
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
        return self._memory(op)

    def tail_mask(self, index: str, count: str, dt) -> list[str]:
        """
        A masked tail's mask (its lsc_state, first in the first prologue): the
        first count elements, where the ISA's MASKAVL form puts it - a mask
        register, or a vector: RVV's masked accesses take v0 - with a scratch
        register where the form takes one; reserved for the whole kernel
        """
        form = next(iter(self.gen.set.forms(modifiers={opset_modifier.MASKAVL}, dts={"dreg": dt})), None)
        if form is not None and rgt.VEC == form.operands["dreg"].rtype:
            self.rt.reserve_specific_reg("vreg", 0)
            mreg = self.gen.vreg(0)
        else:
            # the lowest free mask register: a mask governs accesses, and a
            # governing predicate is p0-p7 on SVE and SME (their slice stores
            # among them); the tracker hands out the highest first
            used = self.rt.get_used_regs("mreg")
            number = next(i for i in range(self.gen.max_mregs()) if i not in used)
            self.rt.reserve_specific_reg("mreg", number)
            mreg = self.gen.mreg(number)
        call = dict(dreg=mreg, dt=dt, modifiers={opset_modifier.MASKAVL}, avlreg=self.params[count])
        taken = self.scratch(form, call) if form is not None else []
        if taken is None:
            raise specialization_error(f"the mask of {count}: no free register for its scratch")
        why = self.gen.set.refusal(**call)
        if why:
            raise specialization_error(f"the mask of {count}: {why}")
        text = self.gen.set(**call)
        self.unscratch(taken)
        self.tails[index] = mreg
        return [l.strip() for l in text.splitlines() if l.strip()]

    def state(self, op) -> list[str]:
        """
        Processor state an lsc_state sets, through the generator's signature
        writing it (asmgen's state_writes): a value \"max\" the signature
        writing \"max\" (a scratch destination); a parameter's count the one
        writing its avl operand's (RVV's vsetvli zero, avl)
        """
        from asmgen.asmblocks.op.opset import opset_modifier as setmod
        # the engine's switches (SME's smstart, smstop): the form writing them
        engine = next((f for f in self.gen.set.forms()
                       if setmod.ENGINE in f.modifiers and f.state_writes == op.values), None)
        if engine is not None:
            call = dict(dt=op.dt, modifiers=set(engine.modifiers), **engine.structural_params)
            why = self.gen.set.refusal(**call)
            if why:
                raise specialization_error(f"{op}: {why}")
            return [l.strip() for l in self.gen.set(**call).splitlines() if l.strip()]
        lines = []
        for name, value in op.values.items():
            if name.startswith("mask(") and name.endswith(")"):
                lines += self.tail_mask(name[5:-1], value, op.dt)
                continue
            if "vtype" == name:
                # the element type and grouping, the vector length kept (RVV's
                # vsetvli zero, zero): the setup's switch
                bits, _, group = value.partition(",m")
                group = group or "1"
                lines += [l.strip() for l in self.gen.isa_setup().setup_dt(dt=op.dt, group=int(group)).splitlines()
                          if l.strip()]
                self.vtype = (int(bits[1:]) // 8, int(group))
                continue
            kind = "max" if "max" == value else "avl"
            form = next((f for f in self.gen.set.forms() if kind == f.state_writes.get(name)), None)
            if form is None:
                raise specialization_error(f"{op}: the ISA sets {name} to {value} with no signature")
            call = dict(dt=op.dt, modifiers=set(form.modifiers))
            taken = []
            if "avl" == kind:
                if value not in self.params:
                    raise specialization_error(f"{op}: no parameter {value}")
                zero = next((self.gen.greg(i) for i in range(64) if "zero" == str(self.gen.greg(i))), None)
                call.update(dreg=zero, avlreg=self.params[value])
            else:
                taken = [("greg", self.rt.reserve_any_reg("greg"))]
                call["dreg"] = self.gen.greg(taken[0][1])
            why = self.gen.set.refusal(**call)
            if why:
                raise specialization_error(f"{op}: {why}")
            lines += [l.strip() for l in self.gen.set(**call).splitlines() if l.strip()]
            self.unscratch(taken)
        return lines

    def _memory(self, op) -> list[str]:
        comp, reg = op.indices[0].component, op.indices[0].indices[0]
        areg = self.aregs[(comp, reg)]
        elements = self.program.offsets.elements_offset(op.offset, self.program.strides.get(comp, {}))
        rel = dict((elements - self.positions[(comp, reg)]).terms)
        scaled = op.properties.get("scaled_index")
        if scaled is not None:
            # the stride times its count through the index register
            rel.pop((scaled[0],), None)
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
        increment = op.increment
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

    def scratch(self, sig, call: dict) -> list | None:
        """
        The registers a signature's scratch operands take (asmgen's SCRATCH
        role: overwritten by the operation for its own use) - any free one
        of each's type, reserved for this instruction alone; None where one
        isn't free (the signature doesn't fit). Free them after the
        instruction (unscratch)
        """
        # the tracker's tag and the generator's register, by type - looked up
        # where a scratch operand needs it (RVV has no mask registers)
        kinds = {rgt.VEC: "vreg", rgt.GP: "greg", rgt.MASK: "mreg"}
        taken = []
        for name, shape in sig.operands.items():
            if orl.SCRATCH != shape.orole or name in call:
                continue
            tag = kinds.get(shape.rtype)
            make = getattr(self.gen, tag, None) if tag is not None else None
            if make is None:
                self.unscratch(taken)
                return None
            try:
                number = self.rt.reserve_any_reg(tag)
            except IndexError:              # all in use
                self.unscratch(taken)
                return None
            taken.append((tag, number))
            call[name] = make(number)
        return taken

    def unscratch(self, taken: list | None):
        for tag, number in taken or []:
            self.rt.unuse_reg(tag, number)

    def slice_count(self, op, dt):
        """
        How many slices a loop over them takes: the tile's (its vector
        length), or a run-time count (a masked tile's rows: tail(m)'s register)
        """
        count = op.info.get("count")
        return self.params[count] if count else self.vl_elements(dt)

    def _predicate(self, sig, kwargs: dict, prefix: list | None = None, dt=None, op=None) -> bool:
        """
        Bind a signature's mask operands: an access to a last vector masked
        to its run-time count (tailmask) to that mask; else to the all-true
        predicate under explicit predication; to a mask register set
        all-true right before the instruction where the instruction clears
        it (prefix gets the setting). False if none applies
        """
        masks = [n for n, o in sig.operands.items() if orl.MASK == o.orole]
        tail = op.properties.get("tail") if op is not None else None
        if tail is not None and tail not in self.tail_vl:
            if not masks or tail not in self.tails:
                return False                # a last vector only under its mask
            for name in masks:
                kwargs[name] = self.tails[tail]
            return True
        if not masks:
            return True
        predicate = _all_true(self.ctx, self.rt)
        clobbered = set(sig.clobber_list or [])
        if predicate is None and (prefix is None or not set(masks) <= clobbered
                                  or not self.gen.set.forms(modifiers={opset_modifier.CONSTMASK})):
            return False
        for name in masks:
            if predicate is not None:
                kwargs[name] = predicate
                continue
            reg = self.clobbered_mask(sig.operands[name].rtype)
            kwargs[name] = reg
            prefix.append(self.gen.set(dreg=reg, dt=dt, modifiers={opset_modifier.CONSTMASK},
                                       mask="alltrue"))
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
            call = dict(dreg=vreg, dt=self.ctx.component_dts[comp],
                        modifiers={opset_modifier.STINDEX}, streg=stride)
            why = self.gen.set.refusal(**call)
            if why:
                raise specialization_error(f"index vector for {comp}: {why}")
            text = self.gen.set(**call)
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

    def vl_elements(self, *args, **kwargs):
        return self.offsets.vl_elements(*args, **kwargs)

    def vl_stride(self, *args, **kwargs):
        return self.offsets.vl_stride(*args, **kwargs)

    def constant_stride(self, *args, **kwargs):
        return self.offsets.constant_stride(*args, **kwargs)

    def vl_squared(self, *args, **kwargs):
        return self.offsets.vl_squared(*args, **kwargs)

    def vl_bytes(self, *args, **kwargs):
        return self.offsets.vl_bytes(*args, **kwargs)

    def vl_multiple(self, *args, **kwargs):
        return self.offsets.vl_multiple(*args, **kwargs)

    def vector_multiple(self, *args, **kwargs):
        return self.offsets.vector_multiple(*args, **kwargs)

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
        amount = self.bytes_of(comp, op.delta)
        k = self.vector_multiple(amount, comp)
        if src_key != dest_key and k is not None:
            # k vectors on from another pointer: one add, as the scheduler counts it
            dt = self.ctx.component_dts[comp]
            lines = [asmops.add(self.gen, dst=dest, reg1=self.aregs[src_key],
                                            reg2=self.vl_multiple(dt, k))]
        else:
            lines = [] if src_key == dest_key else [asmops.mov(self.gen, src=self.aregs[src_key], dst=dest)]
            lines += self.add_bytes(dest, amount, comp)
        # a loop's advance moves to the next iteration: offsets are measured
        # within one, so that part isn't a move of the register
        advance = (op.properties or {}).get("advance")
        self.positions[dest_key] = self.positions[src_key] + op.delta - (advance or sym.const(0))
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
        scaled = op.properties.get("scaled_index")
        for sig in sorted(_sigs(op.sigs), key=lambda s: len(s.modifiers)):
            mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
            kwargs = {}
            call_mods = set(sig.modifiers)
            if scaled is not None:
                # base + the stride's register x its count (+ the immediate):
                # the access's plain or immediate form, the index added - the
                # ISA's own signatures checking it
                from asmgen.asmblocks.op import opmem_modifier as omod
                name, count = scaled
                if mods - {"IOFFSET"} or voffset is not None or increment is not None:
                    continue
                call_mods = (call_mods - {omod.IOFFSET}) | {omod.GOFFSET, omod.SCALEOFFSET}
                kwargs.update(offreg=self.params[name], scale_factor=count)
                if immediate:
                    call_mods.add(omod.IOFFSET)
                    kwargs["ioffset"] = immediate
            elif voffset is not None:
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
            if not self._predicate(sig, kwargs, prefix, dt, op):
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
            operation = getattr(self.gen, op.step.op)
            call = dict(dregs=self.members(op, data, sig), areg=areg, dt=dt, modifiers=call_mods,
                        operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                           if s.modifiers},
                        **kwargs)
            taken = self.scratch(sig, call)
            if taken is None:
                continue
            if operation.fits(**call):
                text = "".join(prefix) + operation(**call)
                self.unscratch(taken)
                return text
            self.unscratch(taken)
        return None

    def vtype_for(self, op, sig) -> str:
        """
        Where the element type travels in a register (RVV's vtype): switched,
        keeping the vector length, only before an operation needing another -
        a widening one the narrow type, arithmetic on a group the group's type
        and grouping. Empty where nothing changes
        """
        if self.vtype is None:
            return ""
        sizes = [adt_size(o.dt) for o in sig.operands.values()
                 if rgt.VEC == o.rtype and o.dt is not None]
        if not sizes:
            return ""
        # the registers this operation sees as one: a wide accumulator's group
        ways = op.properties.get("group", 1)
        want = (min(sizes), 1) if widening_ways(sig) > 1 else (max(sizes), ways)
        if want == self.vtype:
            return ""
        self.vtype = want
        dt = next(o.dt for o in sig.operands.values()
                  if rgt.VEC == o.rtype and adt_size(o.dt) == want[0])
        return self.gen.isa_setup().setup_dt(dt=dt, group=want[1])

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
            operation = getattr(self.gen, op.op)
            call = dict(**regs, **dts, **lanes, **masks, **parts, **sig.structural_params,
                        modifiers=set(sig.modifiers),
                        operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                           if s.modifiers})
            taken = self.scratch(sig, call)
            if taken is None:
                failures.append(f"no free register for {sig}'s scratch operands")
                continue
            why = operation.refusal(**call)
            if why:
                self.unscratch(taken)
                failures.append(why)
                continue
            # the element type set only for the signature taken
            # the element type the specializer's lsc_states set; an operation
            # whose signatures need different ones switches here
            text = (self.vtype_for(op, sig) if op.properties.get("vtype_dynamic") else "") + operation(**call)
            self.unscratch(taken)
            return text
        if all(any(orl.MASK == o.orole for o in sig.operands.values())
               for sig in _sigs(op.resolution.compute_sg)):
            raise specialization_error(
                f"every {op.op} signature needs a governing predicate, and the ISA's setup "
                f"sets up no all-true one")
        raise specialization_error(f"no signature of {op.op} takes {regs}: {failures[:2]}")

    def emit_op(self, op) -> list[str]:
        return [l.strip() for chunk in self._emit_op(op) for l in chunk.splitlines() if l.strip()]

    def _emit_op(self, op) -> list[str]:
        if isinstance(op, lsc_loop):
            return self.loop(op)
        if isinstance(op, (lsc_load, lsc_store)):
            return self.memory(op)
        if isinstance(op, lsc_state):
            return self.state(op)
        if isinstance(op, lsc_transformation):
            return [self.compute(op)]
        if isinstance(op, lsc_zero) and rgt.TILE == op.rtypes[0]:
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [asmops.zero(self.gen, reg=reg, dt=self.dts[(op.indices[0].component,
                                                              op.indices[0].indices[0])])]
        if isinstance(op, lsc_zero):
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [asmops.zero(self.gen, reg=reg, dt=self.dts[(op.indices[0].component,
                                                               op.indices[0].indices[0])])]
        if isinstance(op, lsc_addr_compute):
            return self.address(op)
        if isinstance(op, lsc_permute):
            return [self.permute(op)]
        if isinstance(op, lsc_move):
            return [self.move(op)]
        raise specialization_error(f"cannot emit {type(op).__name__}")

    def permute(self, op: lsc_permute) -> str:
        """
        Two registers permuted into a third through the operation's signature
        (asmgen's opmove PERMUTE)
        """
        regs = [self.reg(idx, rtype) for idx, rtype in zip(op.indices, op.rtypes)]
        first = op.indices[0]
        dt = self.dts[(first.component, first.indices[0])]
        for sig in _sigs(op.sigs):
            call = dict(dregs=regs, dts=[dt] * 3, modifiers=set(sig.modifiers), **sig.structural_params)
            if self.gen.move.fits(**call):
                return self.gen.move(**call)
        raise specialization_error(f"no permute signature takes {regs}")

    def move(self, op: lsc_move, src=None, dst=None) -> str:
        """
        A move between registers through the first unmasked signature taking it
        (src, dst: other physical registers than the operation's, an unrolled
        loop's rotation)
        """
        if op.properties.get("copy_sto") and rgt.TILE in (op.rtypes or []):
            raise specialization_error(f"{op.properties['copy_sto']}: a tile's copy left to emit - "
                                       f"no instruction copies a tile into another (copyprop_tiles "
                                       f"renames them away)")
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
            # a tile slice's index: the loop's register and immediate
            for n in sig.operands:
                if n.endswith(("_rowreg", "_colreg")) and "slice_reg" in op.properties:
                    blocks[n] = op.properties["slice_reg"]
                elif n.endswith(("_immrow", "_immcol")) and "slice_imm" in op.properties:
                    blocks[n] = op.properties["slice_imm"]
            call = dict(dregs=[src, dst], dts=[dt, dt], modifiers=set(sig.modifiers),
                        **masks, **sig.structural_params, **blocks,
                        operand_modifiers={n: set(s.modifiers) for n, s in sig.operands.items()
                                           if s.modifiers})
            if self.gen.move.fits(**call):
                return self.gen.move(**call)
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
            # data registers, tiles among them: an outer products' tile lives
            # on into the operations reaching it slice by slice
            return [(i.component, i.indices[0], r) for i, r in
                    zip(op.indices, op.rtypes or [])
                    if r in (rgt.VEC, rgt.FP, rgt.TILE)]

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
        # the advance in the IR already (schedulable, walks merged): the tail's
        # alone here
        in_ir = block.advance_in_ir
        for comp, oid in block.advance.items():
            step = self.bytes_of(comp, db.elements_offset(oid, strides.get(comp, {})))
            # the address registers the model set up: pointers and scratch
            # addresses are recomputed from them each iteration
            for (c, reg), areg in sorted(self.aregs.items(), key=lambda x: x[0]):
                if c == comp and (c, reg) in self.program.addr_setup:
                    if not in_ir:
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
        # the program's entry (the engine on: SME's smstart) before the rest -
        # smstart zeroes the vector and predicate registers - the exit after
        engine = bool(self.program.entry)
        setup = [l for op in self.program.entry for l in self.state(op)] + \
            lines(isa.setup(rt=self.rt, dt=dt, engine=not engine))
        self.isa_setup_lines = len(setup)
        # the last vectors' masks (tailmask): their first tail(<index>)
        # elements, set once - here, while the parameters are where the call
        # put them - each in a mask register of its own for the whole kernel
        self.tails = {}
        #: the vl route's indices: their counts read at every last vector
        self.tail_vl = {index: None for index in self.program.tail_vl}
        # adjacent short-length regions one, the schedule final (the state's
        # requirements were checked when specializing)
        merge_switches(self.program)
        # the element type the ISA's setup leaves in place, where it is state
        # the instructions run under: the narrowest, its registers ungrouped
        self.vtype = (adt_size(dt), 1) if isa.element_type_is_state() else None
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
            # data registers no later block reads or writes: free for the next
            # blocks - the loop's A and B for the epilogue's temporaries
            used = self.operand_comps(prefix[i + 1:] + case_blocks)
            for key in [k for k in self.phys if k[0] not in used]:
                self.release(key)
            for reg in counters or ():
                if reg is not None:
                    self.rt.unuse_reg("greg", reg.idx)
            self.release_params(later, set(loops[i + 1:]))
            self.release_indexes(set().union(*[self.index_keys([x]) for x in prefix[i + 1:]],
                                             *[self.index_keys(c.blocks) for c in self.program.cases]))
        # the deferred stack parameters into registers of their own, right
        # before the dispatch: their offsets once the save area is known
        loads = []
        self.deferred_regs = {}
        for name, (off, named) in self.deferred.items():
            reg = self.greg()
            for n in named:
                self.params[n] = reg
            self.live_params.add(name)
            self.deferred_regs[name] = (off, reg)
            loads.append(f"@@loadparam {name}@@")
        self.dispatch_code = loads + (self.dispatch() if self.program.cases else [])
        # every case starts with the registers where the dispatch leaves them;
        # the cases exclude each other, so they share the registers left, and
        # a parameter's register can become an address register in each
        # the registers allocated once - a clobbered mask (AVX2's gathers), a
        # tail's mask - each case's own: its tracker starts without them
        start = (dict(self.positions), dict(self.phys), dict(self.numbers),
                 copy.deepcopy(self.rt), dict(self.aregs), set(self.live_params), self.vtype,
                 dict(self.indexes), dict(self.masks), dict(self.tails))
        main_rt = self.rt
        cases = []
        for j, c in enumerate(self.program.cases):
            self.positions, self.phys, self.numbers = dict(start[0]), dict(start[1]), dict(start[2])
            self.rt, self.aregs, self.live_params = copy.deepcopy(start[3]), dict(start[4]), set(start[5])
            self.vtype = start[6]
            self.indexes = dict(start[7])
            self.masks, self.tails = dict(start[8]), dict(start[9])
            self.region_loads = self.start_addresses(case_comps[j], set())
            self.start_indexes(c.blocks)
            # a case's blocks may loop (packm's kappa == 1 copy and its multiply,
            # each looping over n): their counters set up as the prefix's
            out = []
            case_loops = [b.loop_index for b in c.blocks]
            for i, b in enumerate(c.blocks):
                counters, count_lines = None, []
                if b.loop_index is not None:
                    counters, count_lines = self.loop_counts(b, b.loop_index in case_loops[i + 1:])
                emitted = self.block(b, list(c.blocks[i + 1:]))
                emitted.loads, emitted.counters = count_lines + list(emitted.loads or []), counters
                out.append(emitted)
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
        for tag, regs in isa.clobbers().items():
            self.cc.add_clobber(tag, regs)
        save, load, restore = self.fn.get_boilerplate(cc=self.cc)
        shift = self.fn.sp_shift
        loaded = {f"@@loadparam {name}@@": [l.strip() for l in asmops.load(self.gen, 
                      areg=self.gen.greg(self.cc.spreg), offset=off + shift, dst=reg).splitlines()
                      if l.strip()]
                  for name, (off, reg) in self.deferred_regs.items()}
        # what emission found it needs: right after the ISA's setup
        late = [l.strip() for chunk in self.late_setup for l in chunk.splitlines() if l.strip()]
        setup = setup[:self.isa_setup_lines] + late + setup[self.isa_setup_lines:]
        entry, leave = lines(save) + lines(load), lines(restore) + lines(self.gen.ret())
        return emitted_program(
            gen=self.gen,
            setup=setup, blocks=blocks, cases=cases,
            teardown=lines(isa.teardown(rt=self.rt, dt=dt, engine=not engine)) +
            [l for op in self.program.exit for l in self.state(op)], data=lines(isa.data()),
            bases=bases,
            registers={k: str(v) for k, v in self.phys.items()},
            code=[x for l in self.control(blocks, cases) for x in loaded.get(l.strip(), [l])],
            # the function's parameters: C's storages' aliases are C's
            params={n: str(r) for n, r in self.params.items()
                    if self.param_comp(n) not in self.aliases},
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
        # the last vectors' elements, where they're masked (tailmask)
        names += [f"tail({index})" for index in sorted(self.program.tails)]
        # C's storages' alias components take C's parameters: base(Cr) is
        # base(C), stride(Cr,m) stride(C,m) - none of their own
        self.aliases = dict(self.ctx.composition.storage_aliases or {})
        def canonical(name):
            comp = self.param_comp(name)
            return name.replace(f"({comp}", "(C", 1) if comp in self.aliases else name
        given = list(names)
        names = list(dict.fromkeys(canonical(n) for n in given))
        self.cc = self.gen.create_callconv()
        # the callee's registers last: no save and restore unless needed
        self.cc.deprioritize_callee_saved(self.rt)
        for name in names:
            self.cc.add_param("greg", name)
        self.fn = fngen(gen=self.gen, rt=self.rt)
        self.fn.init_cc(cc=self.cc)
        self.params = {n: self.gen.greg(self.rt.aliased_regs["greg"][n]) for n in names}
        for n in given:
            self.params.setdefault(n, self.params[canonical(n)])
        self.live_params = set(names)
        # the boilerplate finds where parameters passed on the stack are
        # loaded through these aliases, which releasing a register drops
        self.param_aliases = {n: self.rt.aliased_regs["greg"][n] for n in names}
        # parameters passed on the stack no block before the cases uses
        # (beta's and C's on x86): loaded at the dispatch - outside any loop,
        # where the epilogue first needs them - not held from entry
        self.deferred = {}
        if self.program.cases:
            used = self.memory_comps(self.program.blocks)
            for name, (tag, off) in list(self.fn.required_loads.items()):
                comp = self.param_comp(name)
                if "greg" != tag or comp is None or comp in used or name not in self.params \
                        or name in self.keep_params:
                    continue
                reg = self.params[name]
                idx = self.rt.aliased_regs["greg"].pop(name, None)
                if idx is None:
                    continue
                self.rt.unuse_reg("greg", idx)
                self.param_aliases.pop(name, None)
                del self.fn.required_loads[name]
                named = [n for n, r in self.params.items() if str(r) == str(reg)]
                for n in named:
                    del self.params[n]
                self.live_params.discard(name)
                self.deferred[name] = (off, named)

    def param_comp(self, name: str):
        return name[name.index("(") + 1:].split(",")[0].rstrip(")") if "(" in name else None

    def release_params(self, later: set, later_loops: set):
        """
        Parameters no later region uses: their registers are free
        """
        aliases = self.aliases
        for name in sorted(self.live_params):
            if name.startswith("tail("):
                continue            # a tail's count: its lsc_states' (a mask, the vl route's lengths)
            comp = self.param_comp(name)
            # C's parameters are its storages' aliases' too
            needed = (comp in later or ("C" == comp and any(a in later for a in aliases))) \
                if comp is not None else name in later_loops
            if not needed:
                self.live_params.discard(name)
                reg = self.params[name]
                if reg.idx in self.rt.get_used_regs("greg"):
                    self.rt.unuse_reg("greg", reg.idx)

    def _lanes_along(self, index) -> int | None:
        """
        The elements of a vector running along index, its length fixed - one
        for every component's vectors along it; None if none run along it, or
        its length isn't fixed
        """
        if self.gen.is_vla:
            return None
        lanes = {self.gen.simd_size // adt_size(self.ctx.component_dts[comp])
                 for comp, along in self.program.vector_indices.items() if along == index}
        return lanes.pop() if 1 == len(lanes) else None

    def loop_counts(self, block, shared: bool):
        """
        A loop's counters from its k parameter (kiterkleft): the iterations,
        each taking the elements of one, and what is left for the tail
        """
        k = self.params[block.loop_index]
        terms = dict(block.step.terms)
        lanes = self._lanes_along(block.loop_index)
        if set(terms) == {("VL",)}:
            # vectors along the loop: its parameter counts chunks of a vector
            # length - the caller divides, and takes what's left of one - the
            # loop unrolled over as many chunks as a step has
            terms = {(): terms[("VL",)]}
        elif set(terms) == {()} and lanes and 0 == int(terms[()]) % lanes:
            # a fixed vector length along the loop - its step a number of
            # elements: counted in chunks of it the same, as its tail takes
            # a chunk an iteration
            terms = {(): int(terms[()]) // lanes}
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
            lines.append(asmops.mov(self.gen, src=k, dst=copy_reg))
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
            for j, (var, value) in enumerate(c.when.items()):
                if var.startswith("stride("):
                    # C's storage: its stride along an index one element - in
                    # bytes, as passed - tested in a general register
                    comp = var[len("stride("):].split(",")[0]
                    t = self.greg()
                    ok = f"ukr{self.dispatch_tag}_ok{i}_{j}"
                    lines.append(asmops.mov(gen, src=self.params[var], dst=t))
                    lines.append(asmops.add_imm(gen, 
                        reg=t, imm=-int(value) * adt_size(self.ctx.component_dts[comp])))
                    lines.append(gen.jzero(reg=t, label=ok))
                    lines.append(gen.jump(label=following))
                    lines.append(gen.label(label=ok))
                    self.rt.unuse_reg("greg", t.idx)
                    continue
                dt = self.ctx.component_dts[var]
                size = adt_size(dt)
                v, k, t = freg(dt), freg(dt), self.greg()
                lines.append(asmops.load(gen, areg=self.params[f"base({var})"], offset=0, dst=v, dt=dt))
                if 0 == float(value):
                    lines.append(asmops.zero(gen, reg=k, dt=dt))
                else:
                    bits = struct.unpack("<Q" if 8 == size else "<I",
                                         struct.pack("<d" if 8 == size else "<f", float(value)))[0]
                    lines.append(asmops.set_imm(gen, reg=t, imm=bits))
                    lines.append(asmops.bits_to_freg(gen, src=t, dst=k, dt=dt))
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
                            {m.name for m in (op.step.op_mod_reqs or set())}:
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
                    lines += [l.strip() for l in asmops.mov(self.gen, src=param, dst=areg).splitlines()
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
            # the count decremented first: the branch at the end reads a value
            # an iteration old - no wait on the decrement before it (the body
            # doesn't read the counter; every ISA's branch tests the register)
            code.extend(lines(gen.cb(reg1=reg, reg2=None, cmp=ez, label=done)))
            if self.ctx.loop_align:
                # the loop's head on a boundary: nops padding, run once
                code.extend(lines(gen.align(self.ctx.loop_align)))
            code.extend(lines(gen.label(label=label)))
            code.extend(lines(asmops.add_imm(gen, reg=reg, imm=-1)))
            code.extend(part)
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
            code.extend(lines(asmops.add_imm(gen, reg=n, imm=-1)))
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
    keep: set[str] = set()

    def emit_once(preallocate=()):
        # a stack parameter deferred to the dispatch but needed earlier (a
        # stride setup computes with): emitted again, that one from entry
        while True:
            emitter = signature_emitter(ctx, program, preallocate=preallocate, keep_params=keep)
            try:
                return emitter, emitter.emit()
            except KeyError as err:
                name = err.args[0] if err.args else None
                deferred = emitter.deferred
                key = next((k for k, (_, named) in deferred.items() if name == k or name in named), None)
                if key is None or key in keep:
                    raise
                keep.add(key)

    emitter, out = emit_once()
    for _ in range(3):
        if not any(late for _, _, late in emitter.recipes):
            return out
        emitter, out = emit_once([(n, a) for n, a, _ in emitter.recipes])
    raise specialization_error("setup's registers kept changing between emissions")
