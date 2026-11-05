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
from ..lsc_model.ir import ir_program, ir_block, BASE_REGISTER, is_start_block
from ..components.tile import scalar_tile
from ..specializers.addresses import address_speller
from ..models.load_store_operations import (lsc_state, 
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute, lsc_loop, lsc_permute,
    lsc_value_op)
from ..models.lsc.index import lsc_reg_index


from .allocation import register_allocator
from ..lsc_model import liveness
from ..specializers.signature import (
    specialization_error, _sigs, _masked, _offset_forms, _accepts, _all_true, _usable, _vl_form, _takes, slice_columns, slice_walkers, slice_placements,
)

SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")


class _labels:
    """The labels' numbers in order - copyable (a loop emitted on trial)"""

    def __init__(self):
        self.n = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.n += 1
        return self.n - 1


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
    #: what an iteration takes off its counter (an element loop's: its unroll)
    step : int = 1
    #: whether the count may be 0 - a branch past the loop first (a vector's
    #: elements never are)
    guarded : bool = True
    #: a plain loop: its body only, counted down by its step (an element
    #: loop's) - not software-pipelined, no last iteration of its own
    plain : bool = False
    #: its labels' kind (ukrN_loop; an element loop's ukrN_elements)
    label : str = "loop"


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

    def value_reg(self, value: tuple):
        """
        The register holding a step's value - a setup value, by name and
        element size: a stride parameter, the vector length in bytes, k of
        them, a vector length of a stride, the vector length squared
        """
        kind = value[0]
        if "stride" == kind:
            return self.stride_reg(value[1])
        if "vl_bytes" == kind:
            return self.vl_bytes(value[1])
        if "vl_multiple" == kind:
            return self.vl_multiple(value[1], value[2])
        if "vl_stride" == kind:
            return self.vl_stride(value[1], value[2])
        if "vl_squared" == kind:
            return self.vl_squared(value[1])
        raise specialization_error(f"no register holds {value}")

    def emit_step(self, areg, step: tuple) -> list[str]:
        """
        One step moving areg: one instruction - the scratch multiply three,
        or its run where no general register is free
        """
        kind = step[0]
        if "imm" == kind:
            return [asmops.add_imm(self.e.gen, reg=areg, imm=step[1])]
        if "vectors" == kind:
            return [asmops.add_vectors(self.e.gen, reg=areg, offset=step[1])]
        if "reg" == kind:
            _, value, op, bit = step
            source = self.value_reg(value)
            if not bit:
                return [asmops.arith(self.e.gen, op, dst=areg, reg1=areg, reg2=source)]
            return [asmops.shifted(self.e.gen, op, dst=areg, reg1=areg, reg2=source, shift=bit)]
        if "mul" == kind:
            _, value, op, count, run = step
            source = self.value_reg(value)
            try:
                scratch = self.e.greg()
            except specialization_error:
                return [line for sub in run for line in self.emit_step(areg, sub)]
            # the product the shorter way - shift-adds (Zba's shNadd) or the
            # count's load and a multiply - then the move
            out = self.scaled_from(scratch, source, count) + \
                [asmops.arith(self.e.gen, op, dst=areg, reg1=areg, reg2=scratch)]
            self.e.rt.unuse_reg("greg", scratch.idx)
            return out
        raise specialization_error(f"no instruction for the step {step}")

    def scaled_length(self, n: int) -> int:
        """
        The instructions scaled_from takes for n times a register (n > 0) -
        as it emits them, for two registers apart (an ISA's shifts of two
        operands, x86's, a copy more; its multiply by an immediate, x86's imul,
        where shorter)
        """
        gen = self.e.gen
        return sum(len([l for l in str(o).splitlines() if l.strip()])
                   for o in self.scaled_from(gen.greg(1), gen.greg(2), n))

    def scaled_from(self, dst, source, n: int) -> list[str]:
        """
        dst = n times source (n > 0), from nothing - setup's values: n's lowest
        set bit a shift from the source (no copy, no zero set first), its
        others shifted adds where the ISA shifts the operand (Zba's shNadd,
        AArch64's LSL, x86's lea), plain adds where it doesn't - or the
        multiply by n (an immediate's load and a mul; x86's imul), the shorter
        """
        bits = [b for b in range(n.bit_length()) if n >> b & 1]
        if 0 == bits[0] and len(bits) > 1 and self.e.shifted_available("add", bits[1]):
            # an odd n: the source and itself shifted, one instruction (5x:
            # sh2add dst,src,src) - no copy first
            out = [asmops.shifted(self.e.gen, "add", dst=dst, reg1=source, reg2=source, shift=bits[1])]
            bits = bits[1:]
        else:
            out = asmops.shift_left_from(self.e.gen, src=source, dst=dst, bit_count=bits[0])
        for b in bits[1:]:
            if self.e.shifted_available("add", b):
                out.append(asmops.shifted(self.e.gen, "add", dst=dst, reg1=dst, reg2=source, shift=b))
            else:
                out += [asmops.arith(self.e.gen, "add", dst=dst, reg1=dst, reg2=source)] * (1 << b)
        # instructions, not entries: an entry may hold two (x86's shift from
        # another register: a copy and the shift)
        lines = sum(len([l for l in str(o).splitlines() if l.strip()]) for o in out)
        if lines > 2 and source != dst:
            try:
                mul = [l for l in asmops.mul_imm(self.e.gen, src=source, dst=dst, factor=n).splitlines() if l.strip()]
            except (ValueError, NotImplementedError):
                mul = None
            if mul and len(mul) < lines:
                return mul
        return out

    def add_scaled(self, areg, source, n: int) -> list[str]:
        """
        areg moved by n times a register's amount (scaled_steps), the register
        given - setup's own computations (offset_value)
        """
        out = []
        for step in self.e.speller.scaled_steps(("given",), n):
            if "mul" == step[0]:
                _, _, op, count, run = step
                try:
                    scratch = self.e.greg()
                except specialization_error:
                    out += [line for sub in run for line in self._given(areg, source, sub)]
                    continue
                out += self.scaled_from(scratch, source, count) + \
                    [asmops.arith(self.e.gen, op, dst=areg, reg1=areg, reg2=scratch)]
                self.e.rt.unuse_reg("greg", scratch.idx)
            else:
                out += self._given(areg, source, step)
        return out

    def _given(self, areg, source, step) -> list[str]:
        _, _, op, bit = step
        if not bit:
            return [asmops.arith(self.e.gen, op, dst=areg, reg1=areg, reg2=source)]
        return [asmops.shifted(self.e.gen, op, dst=areg, reg1=areg, reg2=source, shift=bit)]

    def add_bytes(self, areg, amount: sym, comp: str) -> list[str]:
        """
        Move an address register on by a number of bytes: its steps
        (move_steps), each emitted (emit_step)
        """
        return [line for step in self.e.speller.move_steps(amount, comp) for line in self.emit_step(areg, step)]

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

    def offset_value(self, amount: sym, comp: str):
        """
        A register holding an offset polynomial in bytes - constants and
        strides: a strided walk's row change, rs - (n - R) cs - computed once
        in setup, the planner's choice (max-offset-registers): an add of it
        where the walk moves
        """
        # the element size in the key: a vector length's bytes are the
        # component's (a half-precision A's VL bytes aren't an FP32 C's)
        key = f"offset {adt_size(self.e.ctx.component_dts[comp])}B {amount}"
        if key not in self.e.strides_in:
            self.e.recipes.append(("offset_value", (amount, comp), self.e.regions_started))
            reg = self.e.greg()
            self.e.strides_in[key] = reg
            # a cache of a value its moves can spell instead: given up where a
            # needed value finds no general register (greg) - the budget a cap
            plan_key = (str(amount), comp)
            self.e.evictable[key] = (reg, plan_key, self.e.offset_rank.get(plan_key, 0))
            esize = adt_size(self.e.ctx.component_dts[comp])
            # each piece in setup as it's made: a scratch register add_scaled
            # frees is free again for the next setup value (vl_stride), whose
            # computation goes in at once - collected and placed after it, the
            # scratch's uses would overwrite that value (VL*rs - 5 cs came out 0)
            # where its inputs are: right after the dispatch's loads where one
            # is a stack parameter deferred there (C's strides), else setup
            sink = self.e.dispatch_setup if self.e.placed_at_dispatch("offset_value", (amount, comp)) \
                else self.e.late_setup
            # seeded with its first positive stride term (sh2add t1,a4,a4 for 5
            # strides, not li 0, add, sh2add), the others added, the constant last
            strides = [(f[0], c // esize) for f, c in amount.terms if 1 == len(f) and f[0].startswith("stride(")]
            seed = next(((f, n) for f, n in strides if n > 0), None)
            const = dict(amount.terms).get((), 0)
            if seed is None:
                sink.append(asmops.set_imm(self.e.gen, reg=reg, imm=const))
            else:
                sink += self.scaled_from(reg, self.stride_reg(seed[0], setup=True), seed[1])
            for f, n in strides:
                if (f, n) != seed:
                    sink += self.add_scaled(reg, self.stride_reg(f, setup=True), n)
            # vector lengths (of strides) as add_bytes moves by them: setup values
            # of their own (vl_bytes, vl_multiple, vl_stride), incb on SVE
            others = {f: c for f, c in amount.terms if f and not (1 == len(f) and f[0].startswith("stride("))}
            if others:
                sink += self.add_bytes(reg, sym._make(others), comp)
            if seed is not None and const:
                sink.append(asmops.add_imm(self.e.gen, reg=reg, imm=const))
        return self.e.strides_in[key]

    def stride_elements(self, factor: str, dt):
        """
        A stride in elements (SVE's register offset form scales its index by
        the element size): the stride's bytes shifted right - computed where its
        input is (after the dispatch's loads for a deferred one)
        """
        esize = adt_size(dt)
        key = f"elements {factor} {esize}"
        if key not in self.e.strides_in:
            self.e.recipes.append(("stride_elements", (factor, dt), self.e.regions_started))
            reg = self.e.greg()
            self.e.strides_in[key] = reg
            sink = self.e.dispatch_setup if self.e.placed_at_dispatch("stride_elements", (factor, dt)) \
                else self.e.late_setup
            sink += asmops.shift_right_from(self.e.gen, src=self.stride_reg(factor, setup=True), dst=reg,
                                            bit_count=esize.bit_length() - 1)
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
            sink = self.e.dispatch_setup if self.e.placed_at_dispatch("vl_stride", (factor, dt)) \
                else self.e.late_setup
            sink.append(asmops.mul(self.e.gen, dst=reg, reg1=vlreg, reg2=self.stride_reg(factor, setup=True)))
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
            self.e.late_setup += asmops.shift_left_from(self.e.gen, src=vlreg, dst=reg,
                                                        bit_count=esize.bit_length() - 1)
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
            # (it was a copy and k - 1 adds: 13 instructions for 12 vectors)
            self.e.late_setup += self.scaled_from(reg, base, k)
        return self.e.vlm[key]

    def vector_multiple(self, amount, comp: str) -> int | None:
        """
        k where an amount of bytes is k whole vector lengths (the speller's)
        """
        return self.e.speller.vector_multiple(amount, comp)


class signature_emitter:
    """
    Turns one part's specialized IR program into assembly

    :param ctx: context after the model stage
    :param program: the program to specialize
    """

    #: shifted operands' forms asked of the operations, by (op, shift)

    def __init__(self, ctx, program: ir_program, preallocate=(), keep_params=()):
        self.ctx = ctx
        self.gen = ctx.gen
        self.program = program
        # the generator's tracker keeps the stack pointer and the like out of
        # reach; older generators don't provide one
        self.rt = self.gen.get_reg_tracker()
        #: every data register through one object (docs/REGISTER_ALLOCATION.md)
        self.alloc = register_allocator(self)
        self.phys: dict[tuple, object] = {}
        self.dts: dict[tuple, object] = self._register_types()
        self.numbers: dict[tuple, int] = {}
        self.bounds = self._register_bounds()
        self._required_priorities()
        # setup instructions found while emitting: vector length in bytes,
        # constant strides
        self.late_setup: list[str] = []
        #: setup values placed after the dispatch's loads (placed_at_dispatch):
        #: one of their inputs a stack parameter deferred there
        self.dispatch_setup: list[str] = []
        self.vlb: dict[int, object] = {}
        #: (element size, k) -> a register holding k vector lengths in bytes
        self.vlm: dict[tuple, object] = {}
        #: how address offsets are formed
        self.offsets = offset_planner(self)
        #: what the ISA does in one instruction (shifted adds, vector lengths
        #: counted, three operands) and how a move is spelled - the
        #: specializer's (specializers/addresses.py), its setup's moves too
        self.speller = address_speller(ctx)
        #: the fewest general registers free at any reservation (greg)
        self.min_free_gregs = None
        #: scratch multiplies' registers between their steps: group -> register
        #: (None: none was free, its last step spells the run)
        self.scratches: dict = {}
        #: a scratch multiply's count where shift-adds compute it (scratch_mul)
        self.scratch_counts: dict = {}
        #: offset registers a needed value may take (greg): cache key ->
        #: (register, plan key, rank); the planner's ranks
        self.evictable: dict = {}
        self.offset_rank: dict = {}
        #: offset polynomials with a register of their own (the speller's plan)
        self.offset_plan = set()
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
        self.labels = _labels()
        #: whether a value lives outside the operation emitted (straight sets it)
        self.outside = lambda k: True
        #: what's live after the operation emitted - None: not known
        self.after = None
        #: the components' last reads of their base pseudo registers in the list
        #: straight emits, and its position there (address: a start's register)
        self.base_last, self.straight_pos = {}, None
        #: values in general registers by name (lsc_value_op: a loop's counts)
        self.values: dict = {}
        #: the blocks after those straight emits (value_op: a count shared)
        self.straight_later: list = []
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

        # by the value's own register (value(): a renamed value's owner) -
        # its data type the value's, whose register it is in or not
        def note(idx, dt):
            dts.setdefault(idx.value(), dt)

        for op in self._all_ops():
            if isinstance(op, (lsc_load, lsc_store)):
                note(op.indices[1], comps[op.indices[0].component])
        for op in self._all_ops():
            for idx in op.indices:
                if idx.value()[0] in comps:
                    note(idx, comps[idx.value()[0]])
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
        """The physical register for a virtual one (register_allocator.take)"""
        return self.alloc.take(idx, rtype)

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

    def _register_caps(self):
        """
        --max-{g,f,v}regs: a file's registers beyond its cap reserved - those
        the tracker would hand out last (by priority: the callee-saved ones
        lowered, never saved then), the ones in use (arguments) counted -
        never handed out, not saved
        """
        from ..flow.stages.isaparam import register_cap
        for tag in ("greg", "freg", "vreg"):
            cap = register_cap(self.ctx.params, tag)
            if cap <= 0 or tag not in self.rt.registered_types:
                continue
            used = set(self.rt.get_used_regs(tag))
            prio = self.rt.priorities.get(tag, {})
            free = sorted((i for i in self.rt.available_regs[tag] if i not in used),
                          key=lambda i: (-prio.get(i, 0), bool(self.rt._counterparts(tag, i)), i))
            for i in free[max(0, cap - len(used)):]:
                self.rt.reserve_specific_reg(tag, i)
                for t, j in [(tag, i)] + self.rt._counterparts(tag, i):
                    self.rt.clobbered_regs[t].discard(j)

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
        """A virtual register's value is dead (register_allocator.free)"""
        self.alloc.free(key)

    def placed_at_dispatch(self, name: str, args: tuple) -> bool:
        """
        Whether a setup value's computation goes right after the dispatch's
        loads: one of its strides a stack parameter deferred there (C's) -
        used only in the cases, by the deferral's own rule
        """
        if name in ("vl_stride", "stride_elements"):
            factors = [args[0]]
        elif "offset_value" == name:
            factors = [f[-1] for f, _ in args[0].terms if f and f[-1].startswith("stride(")]
        else:
            return False
        return any(f == n or f in named for f in factors for n, (_, named) in self.deferred.items())

    def greg(self):
        try:
            reg = self.gen.greg(self.rt.reserve_any_reg("greg"))
            # the fewest general registers ever left: what offset registers
            # could have had (max-offset-registers auto)
            free = self.rt.available("greg")
            self.min_free_gregs = free if self.min_free_gregs is None else min(self.min_free_gregs, free)
            return reg
        except IndexError:
            if self.evictable:
                # an offset register given up - the least valuable - its moves
                # spelled out from here: max-offset-registers a cap, not a claim
                key = min(self.evictable, key=lambda k: self.evictable[k][2])
                reg, plan_key, _ = self.evictable.pop(key)
                self.strides_in.pop(key, None)
                self.offset_plan.discard(plan_key)
                return reg
            raise specialization_error(
                "no general register left - the parameters, A's, B's and C's address registers, "
                "their strides, a loop's counter and the offset registers (--max-offset-registers) "
                "take them all: fewer address registers (max-addr-regs), a smaller microtile, or "
                "a layout with fewer run-time strides fit") from None

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
        instruction (the speller's)
        """
        return self.speller.shifted_available(op, shift)

    def add_bytes(self, *args, **kwargs):
        return self.offsets.add_bytes(*args, **kwargs)

    def offset_value(self, *args, **kwargs):
        return self.offsets.offset_value(*args, **kwargs)

    def slices(self, op) -> list[str]:
        """
        A loop over slices, its body as scheduled - its temporaries renamed
        within the registers there are for them (lsc_model.rename), no order
        of the scheduler's holds more; the values live at once in it
        (peak_registers) checked against the room there is all the same
        """
        peak, room = self.peak_registers(op.block, "vreg"), self.room("vreg")
        if peak > room:
            raise specialization_error(
                f"{op.info.get('component')}: {peak} values live at once in a loop over slices, "
                f"{room} registers of their file there - fewer data registers or a smaller "
                f"microtile fit")
        return self._slices(op)

    #: a value's register type, the tracker's tag for it
    TAGS = {rgt.VEC: "vreg", rgt.FP: "freg", rgt.TILE: "treg"}

    def room(self, tag: str) -> int:
        """
        The registers of a file values can have: free ones and those values
        hold (the tracker's counts - those no value holds, masks and index
        vectors, not among them)
        """
        pool = self.rt.pool(tag)
        held = sum(1 for (t, n) in self.numbers.values() if t in pool)
        return self.rt.available(tag) + held

    def peak_registers(self, ops: list, tag: str) -> int:
        """
        The most values of a register file (the tracker's pool: SVE's FP
        registers the low parts of its vector registers) live at once in a
        loop's body in this order - read later before written, carried across
        the back edge, read after the loop (self.after), or held through it
        untouched
        """
        pool = self.rt.pool(tag)
        mine = lambda k: self.TAGS.get(k[2]) in pool
        held = {k for k in self.phys if mine(k)}
        after = self.after if self.after is not None else held
        writes = {k for o in ops for k in self.reads_writes(o)[1]}
        afters = self.live_afters(ops, self.exposed(ops) | (writes & after))
        touched = {k for o in ops for k in self.data_keys(o)}
        through = {k for k in held if k not in touched}
        peak = 0
        for pos, o in enumerate(ops):
            reads, writes_here = self.reads_writes(o)
            live = {k for k in afters[pos] | reads | writes_here if mine(k)}
            peak = max(peak, len(live) + len(through))
        return peak

    def _slices(self, op) -> list[str]:
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
        walk_of = {w: key for key, p in (plan or {}).items() for w in p["walks"]}
        # within the general registers allowed (--loop-gregs), a pointer per
        # access column - an offset's part beside vector lengths; tiles a
        # vector length apart share one, the rest an immediate - set before
        # the loop, stepped once an iteration: no moves between tiles. The
        # first column of a plan register is that register
        # the specializer's plan of the access columns (slice_columns): which
        # columns, which vector lengths immediates, pointers or not
        planned = op.info.get("slice_columns")
        if planned is None and plan:
            planned = slice_columns(op, plan, self.ctx.loop_gregs)
        columns, pointers, column_of = planned if planned else ({}, {}, {})
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
            # the specializer's placement (slice_placements): the move before
            # it, the vector lengths an immediate
            _, move, vectors = placed[id(b)]
            out = self.add_bytes(self.aregs[key], self.bytes_of(comp, move), comp) if move is not None else []
            return out, self.aregs[key], vectors
        def step_on(slices):
            # every register to the next iteration's home, slices on
            out = []
            if pointers:
                for (key, name), ptr in pointer_regs.items():
                    step = sym._make({f: c * slices for f, c in dict(plan[key]["step"].terms).items()})
                    out += self.add_bytes(ptr, self.bytes_of(key[0], step), key[0])
                return out
            for key, p in (plan or {}).items():
                move = sym._make({f: c * slices for f, c in dict(p["step"].terms).items()}) - end[key]
                if dict(move.terms):
                    out += self.add_bytes(self.aregs[key], self.bytes_of(key[0], move), key[0])
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
        # the specializer's walkers (slice_walkers): which walks share a
        # pointer, which a step register - allocated and set here
        planned = op.info.get("slice_walkers")
        if planned is None and not plan:
            planned = slice_walkers(op, self.program, self.ctx.component_dts)
        for w in ([] if plan else planned):
            wcomp, wreg, elements, terms, key, start = (w["comp"], w["reg"], w["elements"], w["terms"],
                                                        w["key"], w["start"])
            wdt = self.ctx.component_dts[wcomp]
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
        # the block's own vector temporaries: written before read (lsc_model.liveness)
        local = liveness.local(op.block)
        sets = [{} for _ in range(rotate)]
        # with one register set, a temporary is free again after its last use
        # in the iteration - the next tile's slice takes its register (cluster
        # and the scheduler's budget ordered the tiles' chains one by one)
        dead_after = {}
        if 1 == rotate:
            last_use = {}
            for pos, b in enumerate(op.block):
                for k in keys(b, list(b.reads) + list(b.writes)):
                    if k in local:
                        last_use[k] = pos
            for k, pos in last_use.items():
                dead_after.setdefault(pos, []).append(k)
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
        mem = lambda ops: [b for b in ops if isinstance(b, (lsc_load, lsc_store))]
        if plan and not pointers:
            order = mem([b for b in op.block if early(b)] + [b for b in op.block if not early(b)]) \
                if preload else mem(op.block)
            placed, end = slice_placements(order, plan, walk_of)
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
                        n = self.alloc.reserve("vreg")
                        sets[group][k] = (n, self.gen.vreg(n))
                    saved[k] = self.phys[k]
                    self.alloc.bind(k, sets[group][k][1])
            for pos, b in enumerate(op.block):
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
                for k in dead_after.get(pos, ()):
                    if k in self.phys:
                        self.release(k)
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
                self.alloc.unreserve("vreg", n)
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
        time. The loop stage made its copies (flow/stages/loops.py copies),
        the addresses stage set up its walker (walker_start), its steps are
        address steps: its counter here, then its body - each operation as
        any, a copy's scalar freed after its last read - a plain loop of
        loop_code, counted down by its unroll
        """
        if "slices" == op.info.get("kind"):
            return self.slices(op)
        from ..flow.stages.loops import WALKER
        anchor = op.walks[0].anchor
        comp = anchor.indices[0].component
        dt = self.ctx.component_dts[comp]
        if not op.subtiling.count.runtime or 1 != op.subtiling.count.size:
            raise specialization_error(f"{op.info.get('component')}: a loop of "
                                       f"{op.subtiling.count} iterations is not emitted yet")
        if not (op.info.get("copies") and op.info.get("walker")):
            raise specialization_error(f"{op.info.get('component')}: an element loop without the loop "
                                       f"stage's copies and walker (flow/stages/loops.py)")
        # the scratch scalars in the body hold the component's elements
        for s in op.block:
            for idx in s.indices:
                self.dts.setdefault((idx.component, idx.indices[0]), dt)
        counter = self.greg()
        frame = [asmops.mov(self.gen, src=self.slice_count(op, dt), dst=counter)]
        # its body renamed as straight renames: a register taken as its value
        # is written, free after its last read - unless the body reads it
        # before writing it (carried across the back edge) or it lives outside
        # the loop (the vector it fills, read after it)
        carried, seen, last = set(), set(), {}
        for i, b in enumerate(op.block):
            for p, (idx, r) in enumerate(zip(b.indices, b.rtypes or [])):
                if r not in (rgt.VEC, rgt.FP, rgt.TILE):
                    continue
                k = (idx.component, idx.indices[0], r)
                if k not in seen and p in (b.reads or []):
                    carried.add(k)
                seen.add(k)
                last[k] = i
        body = []
        for i, b in enumerate(op.block):
            # every operation as any: its accesses at the walker (their
            # elements' offsets where its set-up and steps put it), its steps
            # (address), its fills, extracts and shifts (move)
            body += self.emit_op(b)
            for k in self.data_keys(b):
                if last.get(k) == i and k not in carried and not self.outside(k):
                    self.release(k)
        lines = frame + self.loop_code(emitted_block(
            name=f"elements of {comp}", loop_index=op.info.get("index") or "elements",
            sections={"body": body}, counters=(counter, None), step=op.subtiling.unroll,
            guarded=False, plain=True, label="elements"))
        self.rt.unuse_reg("greg", counter.idx)
        # the walker dead after its loop
        self.rt.unuse_reg("greg", self.aregs[(comp, WALKER)].idx)
        del self.aregs[(comp, WALKER)]
        self.positions.pop((comp, WALKER), None)
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
            self.alloc.reserve("vreg", 0)
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
        goffset = op.properties.get("goffset")
        if goffset is not None:
            rel.pop((goffset,), None)       # the register offset form's index
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
            strides = [f for f in dict(increment.terms) if f]
            inc_step = (op.properties or {}).get("increment_step")
            if inc_step is not None:
                # by an offset's register (a walk's offset step fused: ldinc),
                # where this region still has it - else the access, then the
                # step's spelling (the register given up for a needed value)
                _, comp_o, amount_o, fallback = inc_step
                inc_reg = None
                if (str(amount_o), comp_o) in self.offset_plan:
                    try:
                        inc_reg = self.offset_value(amount_o, comp_o)
                    except (IndexError, specialization_error):
                        inc_reg = None
                data = self.reg(op.indices[1], op.rtypes[1])
                if inc_reg is not None:
                    line = self._mem(op, data, areg, immediate, increment_reg=inc_reg)
                else:
                    line = self._mem(op, data, areg, immediate)
                    if line is not None:
                        line = "\n".join([line] + [l for sub in fallback for l in self.move_step(sub, areg, areg)])
            elif strides:
                # by a stride's register (a walk's step fused: ldinc)
                line = self._mem(op, self.reg(op.indices[1], op.rtypes[1]), areg, immediate,
                                 increment_reg=self.stride_reg(strides[0][0]))
            else:
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
                self.masks[rtype] = self.gen.vreg(self.alloc.reserve("vreg"))
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
            vreg = self.gen.vreg(self.alloc.reserve("vreg"))
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

    def stride_elements(self, *args, **kwargs):
        return self.offsets.stride_elements(*args, **kwargs)

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

    def move_step(self, step: tuple, src, dest) -> list[str]:
        """
        A step's instruction: a copy from src, one add from src (k vector
        lengths, one stride), else dest moved by it (emit_step)
        """
        if "copy" == step[0]:
            # a register onto itself (a start taking the base's register): none
            if src.idx == dest.idx:
                return []
            return [asmops.mov(self.gen, src=src, dst=dest)]
        if "from_vectors" == step[0]:
            return [asmops.add(self.gen, dst=dest, reg1=src, reg2=self.vl_multiple(step[1], step[2]))]
        if "from_stride" == step[0]:
            return [asmops.add(self.gen, dst=dest, reg1=src, reg2=self.stride_reg(step[1]))]
        if "from_imm" == step[0]:
            return [asmops.add_imm_from(self.gen, src=src, dst=dest, imm=step[1])]
        if "scratch_set" == step[0]:
            # a scratch multiply's first step: its register - none free, the
            # group's last step spells its run instead
            try:
                reg = self.greg()
            except specialization_error:
                self.scratches[step[1]] = None
                return []
            self.scratches[step[1]] = reg
            if self.offsets.scaled_length(step[2]) <= 2:
                # shift-adds no longer than the count's load and the multiply
                # (Zba: 5x one sh2add): computed at the multiply's step
                self.scratch_counts[step[1]] = step[2]
                return []
            return [asmops.set_imm(self.gen, reg=reg, imm=step[2])]
        if "scratch_mul" == step[0]:
            reg = self.scratches.get(step[1])
            if reg is None:
                return []
            source = self.offsets.value_reg(step[2])
            count = self.scratch_counts.pop(step[1], None)
            if count is not None:
                return self.offsets.scaled_from(reg, source, count)
            return [asmops.mul(self.gen, dst=reg, reg1=source, reg2=reg)]
        if "scratch_add" == step[0]:
            _, gid, op, _, _, run = step
            reg = self.scratches.pop(gid, None)
            if reg is None:
                return [l for sub in run for l in self.offsets.emit_step(dest, sub)]
            line = asmops.arith(self.gen, op, dst=dest, reg1=dest, reg2=reg)
            self.rt.unuse_reg("greg", reg.idx)
            return [line]
        if "from" == step[0]:
            # a copy and a step merged: dest = src op (value << shift), one
            # instruction of three operands
            _, (_, value, op, bit) = step
            source = self.offsets.value_reg(value)
            if not bit:
                return [asmops.arith(self.gen, op, dst=dest, reg1=src, reg2=source)]
            return [asmops.shifted(self.gen, op, dst=dest, reg1=src, reg2=source, shift=bit)]
        return self.offsets.emit_step(dest, step)

    def address(self, op: lsc_addr_compute) -> list[str]:
        """
        An address register set from another plus an offset
        """
        comp = op.indices[0].component
        src_key = (comp, op.indices[0].indices[0])
        dest_key = (comp, op.indices[1].indices[0])
        if dest_key not in self.aregs and BASE_REGISTER == src_key[1]:
            # a start from the base parameter: the last read of the base takes
            # its register (moved in place) where the parameter is free - the
            # IR's option, the emitter's choice
            name = f"base({comp})"
            if name in self.live_params and self.base_last.get(comp) == self.straight_pos:
                self.aregs[dest_key] = self.params[name]
                self.live_params.discard(name)
        if dest_key not in self.aregs:
            self.aregs[dest_key] = self.greg()
        dest = self.aregs[dest_key]
        step = (op.properties or {}).get("step")
        if step is not None:
            # one step of a spelled move (specializers/addresses.py): its instruction
            if "offset" == step[0]:
                # an offset's register, where this region still has it - else
                # its spelling (the register given up for a needed value)
                _, comp_o, amount_o, fallback = step
                reg = None
                if (str(amount_o), comp_o) in self.offset_plan:
                    try:
                        reg = self.offset_value(amount_o, comp_o)
                    except (IndexError, specialization_error):
                        reg = None
                if reg is not None:
                    lines = [asmops.add(self.gen, dst=dest, reg1=self.aregs[src_key], reg2=reg)]
                else:
                    lines = [l for sub in fallback for l in self.move_step(sub, self.aregs[src_key], dest)]
            else:
                lines = self.move_step(step, self.aregs[src_key], dest)
            advance = (op.properties or {}).get("advance")
            self.positions[dest_key] = self.positions[src_key] + op.delta - (advance or sym.const(0))
            return lines
        amount = self.bytes_of(comp, op.delta)
        k = self.vector_multiple(amount, comp)
        terms = dict(amount.terms)
        once = None
        if src_key != dest_key and k is None and 1 == len(terms):
            (factors, coeff), = terms.items()
            if 1 == len(factors) and factors[0].startswith("stride(") \
                    and coeff == adt_size(self.ctx.component_dts[comp]):
                once = factors[0]
        if src_key != dest_key and k is not None:
            # k vectors on from another pointer: one add, as the scheduler counts it
            dt = self.ctx.component_dts[comp]
            lines = [asmops.add(self.gen, dst=dest, reg1=self.aregs[src_key],
                                            reg2=self.vl_multiple(dt, k))]
        elif once is not None and 1 == len([l for l in asmops.add(
                self.gen, dst=dest, reg1=self.aregs[src_key], reg2=self.stride_reg(once)).splitlines() if l.strip()]):
            # a stride on from another pointer (a k:s walk's leapfrog, a
            # stride pointer): one add of the stride's register, not a copy
            # and an add - where an add takes three registers (not x86's)
            lines = [asmops.add(self.gen, dst=dest, reg1=self.aregs[src_key], reg2=self.stride_reg(once))]
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
             voffset: int | None = None, increment_reg=None) -> str | None:
        """
        The access through the first signature taking it with this immediate
        offset (0: one without an offset)
        """
        dt = self.ctx.component_dts[op.indices[0].component]
        lane = op.properties.get("lane")
        scaled = op.properties.get("scaled_index")
        goffset = op.properties.get("goffset")
        for sig in sorted(_sigs(op.sigs), key=lambda s: len(s.modifiers)):
            mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
            kwargs = {}
            call_mods = set(sig.modifiers)
            if goffset is not None:
                # SVE's register offset: the stride in elements, scaled by the
                # element size ([x0, x_cs, lsl #3]) - the access's plain form,
                # the offset register added (asmgen's signatures checking it)
                from asmgen.asmblocks.op import opmem_modifier as omod
                if mods or immediate or voffset is not None or increment is not None \
                        or increment_reg is not None:
                    continue
                call_mods = call_mods | {omod.GOFFSET}
                kwargs["offreg"] = self.offsets.stride_elements(goffset, dt)
            elif scaled is not None:
                # base + the stride's register x its count (+ the immediate):
                # the access's plain or immediate form, the index added - the
                # ISA's own signatures checking it
                from asmgen.asmblocks.op import opmem_modifier as omod
                name, count = scaled
                if mods - {"IOFFSET"} or voffset is not None or increment is not None \
                        or increment_reg is not None:
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
            elif increment_reg is not None:
                if {"POSTINC"} != mods or immediate or "increg" not in sig.operands:
                    continue
                kwargs["increg"] = increment_reg
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
            return [asmops.zero(self.gen, reg=reg, dt=self.dts[op.indices[0].value()])]
        if isinstance(op, lsc_zero):
            reg = self.reg(op.indices[0], op.rtypes[0])
            return [asmops.zero(self.gen, reg=reg, dt=self.dts[op.indices[0].value()])]
        if isinstance(op, lsc_addr_compute):
            return self.address(op)
        if isinstance(op, lsc_value_op):
            return self.value_op(op)
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
        dt = self.dts[first.value()]
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
        dt = self.dts.get(op.indices[1].value()) or self.dts[op.indices[0].value()]
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
            # a loop block's own registers fixed (the model's rings): nothing
            # released - but the loops in its sections rename their bodies,
            # what's live after each of them known (the back edge: what the
            # body and the tail read before writing live at their ends)
            after = self.exposed([o for b in later for section in SECTIONS for o in getattr(b, section) or []])
            parts = [("init", [op for op in prologue if first(op)]),
                     ("prologue", [op for op in prologue if not first(op)])] + \
                [(section, list(getattr(block, section))) for section in ("body", "epilogue", "tail", "subtail")]
            following = set(after)
            ends = {}
            for name, ops in reversed(parts):
                ends[name] = set(following) | (self.exposed(ops) if name in ("body", "tail") else set())
                following = self.exposed(ops) | (following - {k for o in ops for k in self.reads_writes(o)[1]})
            outside = self.outside
            for name, ops in parts:
                afters = self.live_afters(ops, ends[name])
                lines = []
                for pos, op in enumerate(ops):
                    self.outside = lambda k, a=afters[pos]: k in a
                    self.after = afters[pos]
                    lines += self.emit_op(op)
                out.sections[name] = lines
            self.outside = outside
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
        keys = self.data_keys
        # what's live after each operation: read by a later one before it's
        # written, or by a later block before it writes it - a register
        # written in parts (lanes, blocks, a tile's slices) held whole
        rw = liveness.reads_writes
        exposed, written = set(), set()
        for b in later:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                for o in getattr(b, section) or []:
                    reads, writes = rw(o)
                    exposed |= reads - written
                    written |= writes
        live, live_after = set(exposed), [None] * len(ops)
        for pos in reversed(range(len(ops))):
            live_after[pos] = set(live)
            reads, writes = rw(ops[pos])
            live = (live - writes) | reads
        # a register free once its value is dead - not held while its name
        # comes again (a renamed value in a dead one's register): taken again
        # then
        for key in list(self.phys):
            if key not in live:
                self.release(key)
        lines = []
        outside = self.outside
        # each component's last read of its base pseudo register here: that
        # start may take the base parameter's register (address)
        self.straight_later = list(later)
        self.base_last = {op.indices[0].component: pos for pos, op in enumerate(ops)
                          if isinstance(op, lsc_addr_compute) and BASE_REGISTER == op.indices[0].indices[0]}
        for pos, op in enumerate(ops):
            self.outside = lambda k, after=live_after[pos]: k in after
            self.after = live_after[pos]
            self.straight_pos = pos
            lines += self.emit_op(op)
            for k in keys(op):
                if k not in live_after[pos] and k in self.phys:
                    self.release(k)
        self.outside = outside
        return lines

    def exposed(self, ops: list) -> set:
        """The data registers operations read before they write them (lsc_model.liveness)"""
        return liveness.exposed(ops)

    def live_afters(self, ops: list, end: set) -> list:
        """What's live after each operation (lsc_model.liveness)"""
        return liveness.live_afters(ops, end)

    def reads_writes(self, op) -> tuple[set, set]:
        """The data registers an operation reads and writes (lsc_model.liveness)"""
        return liveness.reads_writes(op)

    def data_keys(self, op) -> list:
        """
        An operation's data registers - vectors, scalars, tiles (an outer
        products' tile lives on into the operations reaching it slice by
        slice): what the renamer (straight, a loop's body) gives registers to
        """
        return [k for p in range(len(op.indices)) for k in [liveness.data_key(op, p)] if k is not None]

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
        # (or the caller's: --assume-state - neither the program's nor the
        # setup's switch)
        # the last vectors' masks (tailmask), in the entry: their first
        # tail(<index>) elements, set once - here, while the parameters are
        # where the call put them - each in a mask register of its own for the
        # whole kernel
        self.tails = {}
        #: the vl route's indices: their counts read at every last vector
        self.tail_vl = {index: None for index in self.program.tail_vl}
        engine = isa.engine()
        switched = engine is not None and any(
            isinstance(op, lsc_state) and op.values == engine[0] for op in self.program.entry)
        switches = not (switched or self.program.engine_assumed)
        # the engine's switch first (smstart zeroes the predicates), the
        # setup's own (an all-true predicate: p0), then the rest of the entry
        # (the tails' masks: the predicates left)
        first = [op for op in self.program.entry if engine is not None
                 and isinstance(op, lsc_state) and op.values == engine[0]]
        setup = [l for op in first for l in self.state(op)] + \
            lines(isa.setup(rt=self.rt, dt=dt, engine=switches)) + \
            [l for op in self.program.entry if not any(op is f for f in first) for l in self.state(op)]
        self.isa_setup_lines = len(setup)
        # adjacent short-length regions one, the schedule final (the state's
        # requirements were checked when specializing)
        merge_switches(self.program)
        # the element type the ISA's setup leaves in place, where it is state
        # the instructions run under: the narrowest, its registers ungrouped
        self.vtype = (adt_size(dt), 1) if isa.element_type_is_state() else None
        # setup-time values found needed by a previous emission: allocated
        # here, before any region, so every region knows their registers
        for name, args in self.preallocate:
            if not self.placed_at_dispatch(name, args):
                getattr(self, name)(*args)
        # the offsets the speller chose (specializers/addresses.py plan)
        self.offset_plan = set(self.program.offset_plan)
        self.offset_rank = dict(self.program.offset_plan)
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
        blocks, pending = [], []
        for i, b in enumerate(prefix):
            later = set().union(*regions[i + 1:], *case_comps, conditions)
            new_before = set(self.aregs)
            self.region_loads = self.start_addresses(regions[i], later)
            self.start_indexes([b])
            # a loop's counters: its setup block's counts (value_op)
            counters = (self.values.get(f"iter({b.name})"), self.values.get(f"left({b.name})")) \
                if b.loop_index is not None else None
            out = self.block(b, prefix[i + 1:] + case_blocks)
            out.loads, out.counters = self.region_loads, counters
            if is_start_block(b):
                # a setup block's code leads the next block's (as the emitter's
                # starts did): the emitted blocks the IR's other blocks
                pending = list(out.loads or []) + [l for part in out.sections.values() for l in part]
            else:
                if pending:
                    out.loads = pending + list(out.loads or [])
                    pending = []
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
        # setup values whose inputs are those parameters: allocated and
        # computed here, in order - no register held through the k loop for
        # them, nothing loaded early
        # (before every case's region: recorded as such, the emissions settle)
        started, self.regions_started = self.regions_started, False
        for name, args in self.preallocate:
            if self.placed_at_dispatch(name, args):
                getattr(self, name)(*args)
        self.regions_started = started
        self.dispatch_code = loads + (["@@dispatchsetup@@"] + self.dispatch() if self.program.cases else [])
        # every case starts with the registers where the dispatch leaves them;
        # the cases exclude each other, so they share the registers left, and
        # a parameter's register can become an address register in each
        # the registers allocated once - a clobbered mask (AVX2's gathers), a
        # tail's mask - each case's own: its tracker starts without them
        start = (dict(self.positions), dict(self.phys), dict(self.numbers),
                 copy.deepcopy(self.rt), dict(self.aregs), set(self.live_params), self.vtype,
                 dict(self.indexes), dict(self.masks), dict(self.tails),
                 # the offsets as the dispatch leaves them: a case giving one's
                 # register up (greg) spells it out itself, the others keep it
                 dict(self.evictable), set(self.offset_plan), dict(self.strides_in))
        main_rt = self.rt
        cases = []
        for j, c in enumerate(self.program.cases):
            self.positions, self.phys, self.numbers = dict(start[0]), dict(start[1]), dict(start[2])
            self.rt, self.aregs, self.live_params = copy.deepcopy(start[3]), dict(start[4]), set(start[5])
            self.vtype = start[6]
            self.indexes = dict(start[7])
            self.evictable, self.offset_plan, self.strides_in = dict(start[10]), set(start[11]), dict(start[12])
            self.masks, self.tails = dict(start[8]), dict(start[9])
            self.region_loads = self.start_addresses(case_comps[j], set())
            self.start_indexes(c.blocks)
            # a case's blocks may loop (packm's kappa == 1 copy and its multiply,
            # each looping over n): their counters set up as the prefix's
            out = []
            case_loops = [b.loop_index for b in c.blocks]
            case_pending = []
            for i, b in enumerate(c.blocks):
                counters, count_lines = None, []
                if b.loop_index is not None:
                    counters = (self.values.get(f"iter({b.name})"), self.values.get(f"left({b.name})"))
                emitted = self.block(b, list(c.blocks[i + 1:]))
                emitted.loads, emitted.counters = count_lines + list(emitted.loads or []), counters
                if is_start_block(b):
                    case_pending += list(emitted.loads or []) + [l for part in emitted.sections.values() for l in part]
                    continue
                if case_pending:
                    emitted.loads = case_pending + list(emitted.loads or [])
                    case_pending = []
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
        # (an engine the caller keeps on switches nowhere here: not the kernel's)
        for tag, regs in ({} if self.program.engine_assumed else isa.clobbers()).items():
            self.cc.add_clobber(tag, regs)
        save, load, restore = self.fn.get_boilerplate(cc=self.cc)
        shift = self.fn.sp_shift
        loaded = {f"@@loadparam {name}@@": [l.strip() for l in asmops.load(self.gen, 
                      areg=self.gen.greg(self.cc.spreg), offset=off + shift, dst=reg).splitlines()
                      if l.strip()]
                  for name, (off, reg) in self.deferred_regs.items()}
        loaded["@@dispatchsetup@@"] = [l.strip() for chunk in self.dispatch_setup
                                       for l in chunk.splitlines() if l.strip()]
        # what emission found it needs: right after the ISA's setup
        late = [l.strip() for chunk in self.late_setup for l in chunk.splitlines() if l.strip()]
        setup = setup[:self.isa_setup_lines] + late + setup[self.isa_setup_lines:]
        entry, leave = lines(save) + lines(load), lines(restore) + lines(self.gen.ret())
        return emitted_program(
            gen=self.gen,
            setup=setup, blocks=blocks, cases=cases,
            teardown=lines(isa.teardown(rt=self.rt, dt=dt, engine=switches)) +
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
            base = self.ctx.composition.storage_bases.get(comp, "C")
            return name.replace(f"({comp}", f"({base}", 1) if comp in self.aliases else name
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
        self._register_caps()
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

    def value_op(self, op) -> list[str]:
        """
        A value operation (lsc_value_op): a loop's counts - its iterations and
        what's left (loop_counts: the unroll its step's; a copy of the count
        parameter where a later loop counts the same, else counted in place;
        none for a loop stepping one element) - kept by the values' names
        """
        if "counts" == op.kind:
            from types import SimpleNamespace
            index, loop = op.read_names[0], op.params["loop"]
            shared = any(b.loop_index == index for b in self.straight_later
                         if b.name != loop and b.loop_index is not None)
            counters, lines = self.loop_counts(
                SimpleNamespace(loop_index=index, step=op.params["step"], name=loop), shared)
            for name, reg in zip(op.write_names, counters):
                self.values[name] = reg
            return lines
        raise specialization_error(f"no value operation {op.kind} emitted yet")

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
            return gen.freg(self.alloc.reserve("freg"), dt)

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
                    self.alloc.unreserve("freg", r.idx)
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
            self.alloc.unreserve("vreg", self.indexes.pop(key).idx)

    def start_addresses(self, comps, later) -> list[str]:
        """
        These components' base parameters as their base pseudo registers
        (BASE_REGISTER, position 0): the IR's setup blocks move each address
        register from it to its start (the specializer's start_blocks)
        """
        for comp in sorted(comps):
            name = f"base({comp})"
            if name in self.params and (comp, BASE_REGISTER) not in self.aregs:
                self.aregs[(comp, BASE_REGISTER)] = self.params[name]
                self.positions[(comp, BASE_REGISTER)] = sym.const(0)
        return []

    def release_aregs(self, keys):
        for key in keys:
            reg = self.aregs.pop(key)
            if BASE_REGISTER != key[1]:
                # (a base pseudo register's is the parameter's: its own release)
                self.rt.unuse_reg("greg", reg.idx)

    def loop_code(self, block: emitted_block) -> list[str]:
        """
        A block's code with its loop's control around its sections, branching
        with cb - software-pipelined (control); a plain loop - a body only, no
        prologue or last iteration (an element loop) - its body counted down
        by the block's step, past it first only where the count may be 0
        """
        lines = lambda text: [l.strip() for l in text.splitlines() if l.strip()]
        gen = self.gen
        code: list[str] = []
        ez, nz = comparison.EZ, comparison.NZ

        def counted(reg, label, part, done, step=1, guarded=True):
            # the count decremented first: the branch at the end reads a value
            # an iteration old - no wait on the decrement before it (the body
            # doesn't read the counter; every ISA's branch tests the register)
            if guarded:
                code.extend(lines(gen.cb(reg1=reg, reg2=None, cmp=ez, label=done)))
            if self.ctx.loop_align:
                # the loop's head on a boundary: nops padding, run once
                code.extend(lines(gen.align(self.ctx.loop_align)))
            code.extend(lines(gen.label(label=label)))
            code.extend(lines(asmops.add_imm(gen, reg=reg, imm=-step)))
            code.extend(part)
            code.extend(lines(gen.cb(reg1=reg, reg2=None, cmp=nz, label=label)))
            if guarded:
                code.extend(lines(gen.label(label=done)))

        code.extend(block.loads)
        sec = block.sections
        if block.loop_index is None:
            for part in sec.values():
                code.extend(part)
            code.extend(block.advance + block.tail_advance)
            return code
        n, left = block.counters
        n = n or self.params[block.loop_index]
        tag = next(self.labels)
        done = f"ukr{tag}_done"
        if block.plain:
            # a plain loop (an element loop): its body counted down by its step
            counted(n, f"ukr{tag}_{block.label}", sec.get("body", []) + block.advance, done,
                    step=block.step, guarded=block.guarded)
            return code
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
        return code

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

        def block_code(block):
            code.extend(self.loop_code(block))

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



#: the last emission's fewest free general registers (emit_program_measured)
_last_min_free = [None]

#: the most offset registers max-offset-registers auto takes
AUTO_OFFSET_REGISTERS = 8


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

    def emit_all():
        emitter, out = emit_once()
        for _ in range(3):
            if not any(late for _, _, late in emitter.recipes):
                _last_min_free[0] = emitter.min_free_gregs
                return emitter, out
            emitter, out = emit_once([(n, a) for n, a, _ in emitter.recipes])
        raise specialization_error("setup's registers kept changing between emissions")
    return emit_all()[1]


def emit_program_measured(ctx, program: ir_program) -> tuple:
    """
    A program emitted, with the fewest general registers left free at any
    reservation: what offset registers could have (max-offset-registers
    auto, the emit stage's)
    """
    out = emit_program(ctx, program)
    return out, _last_min_free[0]
