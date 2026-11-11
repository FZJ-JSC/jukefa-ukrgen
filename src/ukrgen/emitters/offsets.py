"""
The offset planner: setup values - strides, vector lengths, offset
registers - and the address steps spelled from them (split from
emitters/signature.py)
"""





from . import asmops
from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.registers import adt_size

from ..lsc_model.addressing import offpoly


from ..specializers.signature import specialization_error
from ..offset_polynomial import offset_polynomial as offpoly


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

    def add_bytes(self, areg, amount: offpoly, comp: str) -> list[str]:
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

    def offset_value(self, amount: offpoly, comp: str):
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
                sink += self.add_bytes(reg, offpoly._make(others), comp)
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
