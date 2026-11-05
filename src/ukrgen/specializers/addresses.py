"""
Address moves as steps of one instruction each (docs/ADDRESSING_PLAN.md).

An lsc_addr_compute moves an address register by a polynomial - constants,
strides, vector lengths, vector lengths of strides. Here it becomes its
steps, each one instruction of the ISA: an immediate; incb/decb by vector
lengths (SVE); an add or sub of a named value - a stride parameter, the
vector length in bytes, k of them, a vector length of a stride, the vector
length squared - shifted where the ISA shifts the operand; from another
register one add where it can (k vector lengths, one stride), else a copy
first. A run of more than three of one value: the count times it in a
scratch register, one step of three instructions until the IR has scratch
registers (its run kept, for where no general register is free).

The emitter turns a step into its instruction, the value register it names
resolved as a setup value (by name and element size).
"""

from __future__ import annotations

from asmgen.asmblocks.op import operand_modifier as opd_mod
from asmgen.registers import adt_size, asm_data_type as adt

from ..components.tile import scalar_tile
from ..emitters import asmops
from ..lsc_model.addressing import sym
from ..lsc_model.ir import ir_program
from ..models.lsc.index import lsc_reg_index
from ..models.lsc.reg import lsc_reg_type
from ..models.load_store_operations import lsc_addr_compute, lsc_loop
from .signature import specialization_error

#: address moves spelled as steps before emitting - the kernels byte for byte
#: the same either way; off for comparing
SPELL_ADDRESSES = True

SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")


def plannable(factors: tuple) -> bool:
    """
    A term of an address move an offset register can hold, computed once: a
    stride, the vector length, a vector length of a stride, the vector
    length squared (a loop's advance less its walk: VL - 12 rs)
    """
    if 1 == len(factors):
        return factors[0].startswith("stride(") or "VL" == factors[0]
    return 2 == len(factors) and "VL" == factors[0] and (factors[1].startswith("stride(") or "VL" == factors[1])


class address_speller:
    """
    A program's address moves as one-instruction steps, the ISA asked what it
    does in one: shifted adds, vector lengths counted (incb), three operands

    :param ctx: the flow's context (its generator, the components' types)
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.gen = ctx.gen
        #: SVE counts vector lengths in an instruction (incb), RVV keeps the
        #: vector length in a register
        self.vector_length_kept = "IMPLICIT" == self.gen.isa_setup().predication().name
        self._shifted: dict[tuple[str, int], bool] = {}
        #: the offsets planned for the program being spelled
        self.planned: set = set()
        #: a scratch multiply's three steps' group, numbered
        self.next_scratch = 0
        reg = self.gen.greg(0)
        #: an immediate added into another register one instruction
        self.imm_from = 1 == len([l for l in asmops.add_imm_from(self.gen, src=self.gen.greg(1), dst=reg, imm=16)
                                  .splitlines() if l.strip()])
        #: an add of three registers one instruction (not x86's: a copy too)
        self.three_operands = 1 == len([l for l in asmops.add(self.gen, dst=reg, reg1=self.gen.greg(1),
                                                              reg2=self.gen.greg(2)).splitlines() if l.strip()])

    def esize(self, comp: str) -> int:
        return adt_size(self.ctx.component_dts[comp])

    def bytes_of(self, comp: str, elements: sym) -> sym:
        return elements * self.esize(comp)

    def shifted_available(self, op: str, shift: int) -> bool:
        """
        Whether the ISA adds or subtracts a register shifted by shift in one
        instruction - a generator raises NotImplementedError where it doesn't
        """
        if (op, shift) not in self._shifted:
            reg = self.gen.greg(0)
            self._shifted[(op, shift)] = getattr(self.gen, op).fits(
                adreg=reg, bdreg=reg, cdreg=reg, a_dt=adt.UINT64, b_dt=adt.UINT64, c_dt=adt.UINT64,
                operand_modifiers={"bdreg": {opd_mod.ISHIFT}}, bdreg_shift=shift) is not None
        return self._shifted[(op, shift)]

    def vector_multiple(self, amount: sym, comp: str) -> int | None:
        """
        k where an amount of bytes is k whole vector lengths (k > 0) and the
        ISA keeps the vector length in a register; else None
        """
        if not self.vector_length_kept:
            return None
        terms = list(amount.terms)
        if 1 != len(terms) or ("VL",) != tuple(terms[0][0]):
            return None
        coeff, esize = terms[0][1], self.esize(comp)
        return coeff // esize if coeff > 0 and 0 == coeff % esize else None

    def scaled_steps(self, value: tuple, n: int, split: bool = False) -> list[tuple]:
        """
        A value n times, n negative backwards: an add or sub per set bit of n,
        shifted where the ISA shifts the operand (AArch64 LSL, x86 lea, Zba's
        shNadd), plain adds or subs repeated where it doesn't; a run longer
        than three the scratch multiply, its run kept
        """
        op = "sub" if n < 0 else "add"
        out, k, bit = [], abs(n), 0
        while k:
            if k & 1:
                if not bit or self.shifted_available(op, bit):
                    out.append(("reg", value, op, bit))
                else:
                    out += [("reg", value, op, 0)] * (1 << bit)
            k >>= 1
            bit += 1
        if len(out) > 3:
            if split:
                # three steps the scheduler can spread: the count in a scratch
                # register, the multiply, the add - its run where none is free
                self.next_scratch += 1
                gid = self.next_scratch
                return [("scratch_set", gid, abs(n)), ("scratch_mul", gid, value),
                        ("scratch_add", gid, op, value, abs(n), tuple(out))]
            return [("mul", value, op, abs(n), tuple(out))]
        return out

    def move_steps(self, amount: sym, comp: str, split: bool = False) -> list[tuple]:
        """
        The steps moving an address register by a number of bytes: constants
        as an immediate; whole vectors with incb/decb where the ISA counts them
        so; multiples of a value - strides, the vector length (RVV), vector
        lengths of strides or of vectors, each held in bytes - scaled_steps
        """
        dt = self.ctx.component_dts[comp]
        esize = adt_size(dt)
        steps = []
        for factors, coeff in amount.terms:
            if not factors:
                steps.append(("imm", coeff))
                continue
            if 0 != coeff % esize:
                raise specialization_error(
                    f"moving {comp}'s address by {amount} bytes: {coeff} isn't whole elements")
            n = coeff // esize
            if ("VL",) == factors and not self.vector_length_kept:
                steps.append(("vectors", n))            # whole vectors, forward or back: incb, decb
                continue
            if ("VL",) == factors and n > 1:
                steps.append(("reg", ("vl_multiple", dt, n), "add", 0))   # RVV: k vector lengths, one add
                continue
            if ("VL",) == factors:
                value = ("vl_bytes", dt)                # RVV: the vector length in bytes
            elif 1 == len(factors) and factors[0].startswith("stride("):
                value = ("stride", factors[0])
            elif 2 == len(factors) and "VL" == factors[0] and factors[1].startswith("stride("):
                value = ("vl_stride", factors[1], dt)   # a vector length of strided elements
            elif ("VL", "VL") == factors:
                value = ("vl_squared", dt)              # vector lengths of vectors: a packed layout's next tile
            else:
                raise specialization_error(
                    f"moving {comp}'s address by {amount} bytes needs run-time arithmetic "
                    f"(vector length), which is not specialized yet")
            steps += self.scaled_steps(value, n, split)
        return steps

    def offset_cost(self, amount: sym, comp: str) -> int:
        """
        The instructions moving an address by amount takes spelled out: an
        immediate's add, a vector length's one, a stride's per set bit (where
        the ISA shifts the operand, else as many as the bit is worth), at most
        three a term (the scratch multiply)
        """
        esize = self.esize(comp)
        cost = 0
        for factors, coeff in amount.terms:
            if not factors:
                cost += 1 if coeff else 0
                continue
            if ("VL",) == factors:
                cost += 1
                continue
            n, bit, op, term = abs(coeff // esize), 0, "sub" if coeff < 0 else "add", 0
            while n:
                if n & 1:
                    term += 1 if not bit or self.shifted_available(op, bit) else 1 << bit
                n >>= 1
                bit += 1
            cost += min(term, 3)
        return cost

    def plan(self, program: ir_program) -> dict:
        """
        The offsets that get a register of their own (max-offset-registers):
        every move of strides and vector lengths taking more than one
        instruction spelled out, its uses weighted - a loop's body tenfold -
        times the instructions a register saves; the most first. Stride
        parameters on the stack too: the emitter computes an offset where its
        inputs are (after the dispatch's loads)

        :return: (polynomial's text, component) -> (polynomial, rank)
        """
        budget = program.offset_registers or 0
        if budget <= 0:
            return {}
        found = {}
        def visit(ops, weight):
            for op in ops:
                if isinstance(op, lsc_loop):
                    visit(op.block, weight)
                    continue
                if not isinstance(op, lsc_addr_compute) or "step" in (op.properties or {}):
                    continue
                comp = op.indices[0].component
                amount = self.bytes_of(comp, op.delta)
                if not all(plannable(f) for f, _ in amount.terms if f):
                    continue
                cost = self.offset_cost(amount, comp)
                if cost > 1:
                    entry = found.setdefault((str(amount), comp), [0, cost, amount])
                    entry[0] += weight
        for block in program.blocks + [b for case in program.cases for b in case.blocks]:
            for section in SECTIONS:
                visit(getattr(block, section) or [], 10 if "body" == section else 1)
        ranked = sorted(found.items(), key=lambda kv: -kv[1][0] * (kv[1][1] - 1))
        return {key: (amount, uses * (cost - 1)) for key, (uses, cost, amount) in ranked[:budget]}

    def step_delta(self, step: tuple, comp: str) -> sym:
        """
        A step's move in the component's elements: a move's steps add up to it
        """
        kind = step[0]
        if "copy" == kind:
            return sym.const(0)
        if "imm" == kind:
            return sym.const(step[1] // self.esize(comp))
        if "vectors" == kind:
            return sym._make({("VL",): step[1]})
        if "from_vectors" == kind:
            return sym._make({("VL",): step[2]})
        if "from_stride" == kind:
            return sym._make({(step[1],): 1})
        if "offset" == kind:
            return self.elements_of(step[1], step[2])
        if "from" == kind:
            return self.step_delta(step[1], comp)
        if "from_imm" == kind:
            return sym.const(step[1] // self.esize(comp))
        if kind in ("scratch_set", "scratch_mul"):
            return sym.const(0)
        if "scratch_add" == kind:
            return self.step_delta(("mul", step[3], step[2], step[4], ()), comp)
        value, sign = step[1], -1 if "sub" == step[2] else 1
        times = step[3] if "mul" == kind else 1 << step[3]
        if "stride" == value[0]:
            factors = (value[1],)
        elif "vl_stride" == value[0]:
            factors = ("VL", value[1])
        elif "vl_squared" == value[0]:
            factors = ("VL", "VL")
        else:
            factors = ("VL",)
            if "vl_multiple" == value[0]:
                times *= value[2]
        return sym._make({factors: sign * times})

    def elements_of(self, comp: str, amount: sym) -> sym:
        """
        A polynomial in bytes back in the component's elements
        """
        esize = self.esize(comp)
        return sym._make({f: c // esize for f, c in amount.terms})

    def spelled(self, op: lsc_addr_compute) -> list:
        """
        An address move as its steps: from another register one add where it
        can (k vector lengths, one stride - where an add takes three
        registers), else a copy and the move's steps; a loop's advance on the
        last; a move of nothing as it was
        """
        comp = op.indices[0].component
        src, dst = op.indices[0].indices[0], op.indices[1].indices[0]
        dt = self.ctx.component_dts[comp]
        amount = self.bytes_of(comp, op.delta)
        k = self.vector_multiple(amount, comp)
        terms = dict(amount.terms)
        one = next(iter(terms)) if 1 == len(terms) else None
        whole = []
        if src != dst and k is not None:
            whole = [(src, ("from_vectors", dt, k))]
        elif src != dst and one is not None and 1 == len(one) and one[0].startswith("stride(") \
                and terms[one] == adt_size(dt) and self.three_operands:
            whole = [(src, ("from_stride", one[0]))]
        if (str(amount), comp) in self.planned and not whole:
            # one add of the offset's register, its spelling carried for where
            # the register was given up (the emitter's choice, per region)
            fallback = ((("copy",),) if src != dst else ()) + tuple(self.move_steps(amount, comp))
            steps = [(src, ("offset", comp, amount, fallback))]
        elif src != dst and k is not None:
            steps = [(src, ("from_vectors", dt, k))]
        elif src != dst and one is not None and 1 == len(one) and one[0].startswith("stride(") \
                and terms[one] == adt_size(dt) and self.three_operands:
            steps = [(src, ("from_stride", one[0]))]
        else:
            steps = ([(src, ("copy",))] if src != dst else []) + \
                [(dst, s) for s in self.move_steps(amount, comp, split=True)]
        if not steps:
            return [op]
        props = dict(op.properties or {})
        advance = props.pop("advance", None)
        out = []
        for n, (s_src, step) in enumerate(steps):
            o = lsc_addr_compute(comp, s_src, dst, self.step_delta(step, comp), scalar_tile)
            o.properties = dict(props, step=step)
            if advance is not None and len(steps) - 1 == n:
                o.properties["advance"] = advance
            out.append(o)
        total = sym.const(0)
        for o in out:
            total = total + o.delta
        if dict(total.terms) != dict(op.delta.terms):
            raise specialization_error(f"spelling {comp}'s move by {op.delta}: steps add up to {total}")
        return out

    def merged_run(self, run: list) -> list | None:
        """
        A run of identical plain adds or subs of one value as one shifted
        step a set bit of its length - where the ISA shifts the operand and
        that's fewer; None where not
        """
        _, value, op, bit = run[0]
        n = len(run)
        bits = [b for b in range(n.bit_length()) if n >> b & 1]
        if any(b and not self.shifted_available(op, b) for b in bits) or len(bits) >= n:
            return None
        return [("reg", value, op, b) for b in bits]

    def merge_ops(self, ops: list) -> list:
        """
        Adjacent steps moving one register merged where that's shorter - before
        scheduling, steps of one move (and moves of one register) adjacent:
        a run of identical adds into shifted ones, immediates into one,
        cancelling pairs gone, a copy and a step on it into one step from the
        source (three operands)
        """
        out = []
        i = 0
        while i < len(ops):
            op = ops[i]
            st = _step(op)
            if st is None:
                out.append(op)
                i += 1
                continue
            comp, src, dst = _regs(op)
            # a run of the same plain step on one register
            if "reg" == st[0] and 0 == st[3] and src == dst:
                j = i + 1
                while j < len(ops) and _step(ops[j]) == st and _regs(ops[j]) == (comp, dst, dst) \
                        and "advance" not in (ops[j - 1].properties or {}):
                    j += 1
                merged = self.merged_run([st] * (j - i)) if j - i > 1 else None
                if merged is not None:
                    out += self.rebuilt(ops[i:j], merged, comp, dst, dst)
                    i = j
                    continue
            nxt = ops[i + 1] if i + 1 < len(ops) else None
            ns = _step(nxt) if nxt is not None else None
            if ns is not None and "advance" not in (op.properties or {}) and _regs(nxt) == (comp, dst, dst):
                # immediates into one; cancelling pairs gone
                if "imm" == st[0] == ns[0] and src == dst and abs(st[1] + ns[1]) <= MERGED_IMMEDIATE:
                    total = st[1] + ns[1]
                    out += self.rebuilt([op, nxt], [("imm", total)] if total else [], comp, dst, dst)
                    i += 2
                    continue
                if "reg" == st[0] == ns[0] and src == dst and st[1] == ns[1] and st[3] == ns[3] \
                        and {st[2], ns[2]} == {"add", "sub"}:
                    out += self.rebuilt([op, nxt], [], comp, dst, dst)
                    i += 2
                    continue
                # a copy and an immediate: one add from the source
                if "copy" == st[0] and "imm" == ns[0] and self.imm_from and abs(ns[1]) <= MERGED_IMMEDIATE:
                    out += self.rebuilt([op, nxt], [("from_imm", ns[1])], comp, src, dst)
                    i += 2
                    continue
                # a copy and a step on it: one step from the source
                if "copy" == st[0] and "reg" == ns[0] and self.three_operands:
                    out += self.rebuilt([op, nxt], [("from", ns)], comp, src, dst)
                    i += 2
                    continue
            out.append(op)
            i += 1
        return out

    def rebuilt(self, ops: list, steps: list, comp: str, src: int, dst: int) -> list:
        """
        ops' moves as steps (from src into dst), the same delta in all - a
        loop's advance on the last; nothing where they cancel (a move of
        nothing kept where an advance rides on it)
        """
        advance = next(((o.properties or {}).get("advance") for o in reversed(ops)
                        if "advance" in (o.properties or {})), None)
        props = {k: v for k, v in (ops[0].properties or {}).items() if k not in ("step", "advance")}
        if not steps and advance is not None:
            steps = [("imm", 0)]
        out = []
        for n, st in enumerate(steps):
            o = lsc_addr_compute(comp, src if 0 == n else dst, dst, self.step_delta(st, comp), scalar_tile)
            o.properties = dict(props, step=st)
            # the values it adds read by name: what orders it after their
            # setup's operations (docs/ADDRESSING_PLAN.md setup values, 1)
            for value in step_values(st):
                o.indices.append(lsc_reg_index(value_name(value), [0]))
                o.tiles.append(scalar_tile)
                o.reg_types.append(lsc_reg_type.value)
                o.reads.append(len(o.indices) - 1)
            if advance is not None and len(steps) - 1 == n:
                o.properties["advance"] = advance
            out.append(o)
        before = sym.const(0)
        for o in ops:
            before = before + o.delta
        after = sym.const(0)
        for o in out:
            after = after + o.delta
        if dict(before.terms) != dict(after.terms):
            raise specialization_error(f"merging {comp}'s steps: {before} became {after}")
        return out

    def merge(self, program: ir_program) -> None:
        """
        Every program's adjacent steps merged (merge_ops) - in its sections,
        its loops' blocks, its cases'
        """
        def walk(ops):
            for op in ops:
                if isinstance(op, lsc_loop):
                    op.block = self.merge_ops(walk(list(op.block)))
                    op.refresh()
            return ops
        for block in program.blocks + [b for case in program.cases for b in case.blocks]:
            for section in SECTIONS:
                ops = getattr(block, section)
                if ops:
                    setattr(block, section, self.merge_ops(walk(list(ops))))

    def spell(self, program: ir_program) -> None:
        """
        Every address move of the program as its steps - in its sections, its
        loops' blocks, its cases' - the offsets planned first (plan), a move
        one covers one step adding it. Done once: a step isn't spelled again
        """
        chosen = self.plan(program)
        self.planned = set(chosen)
        program.offset_plan = {key: rank for key, (_, rank) in chosen.items()}
        def rewrite(ops):
            out = []
            for op in ops:
                if isinstance(op, lsc_loop):
                    op.block = rewrite(list(op.block))
                    op.refresh()
                elif isinstance(op, lsc_addr_compute) and "step" not in (op.properties or {}):
                    out += self.spelled(op)
                    continue
                out.append(op)
            return out
        for block in program.blocks + [b for case in program.cases for b in case.blocks]:
            for section in SECTIONS:
                ops = getattr(block, section)
                if ops:
                    setattr(block, section, rewrite(list(ops)))


def value_name(value: tuple) -> str:
    """A setup value's name as an operand: value: and its tuple"""
    return f"value:{value}"


def step_values(step: tuple) -> list:
    """
    The setup values a spelled step adds (the emitter's value_reg's): a
    register's (reg, mul, the split multiply's), a vector length multiple
    (from_vectors), a stride (from_stride); a copy-and-step's inner step's;
    an offset step's fallback's (its register the offsets' own)
    """
    kind = step[0]
    if kind in ("reg", "mul"):
        return [step[1]]
    if "scratch_mul" == kind:
        return [step[2]]
    if "scratch_add" == kind:
        return [step[3]]
    if "from" == kind:
        return step_values(step[1])
    if "from_vectors" == kind:
        return [("vl_multiple", step[1], step[2])]
    if "from_stride" == kind:
        return [("stride", step[1])]
    if "offset" == kind:
        return [v for sub in step[3] for v in step_values(sub)]
    return []


def value_setup(program) -> int:
    """
    The setup values spelled steps add (step_values) computed in the IR: a
    value operation for each, in a setup block at the program's start - the
    emitter's recipes' code in place, ordered by the values the steps read
    (docs/ADDRESSING_PLAN.md setup values, 2). A value of a stride deferred to
    the dispatch the emitter leaves there. :return: the values
    """
    from ..lsc_model.ir import ir_block, START_BLOCK
    from ..models.load_store_operations import lsc_value_op
    values = {}

    def visit(ops):
        for op in ops or []:
            if isinstance(op, lsc_loop):
                visit(op.block)
            step = (op.properties or {}).get("step")
            if step is not None:
                for value in step_values(step):
                    values.setdefault(value_name(value), value)
    for block in program.blocks + [b for case in program.cases for b in case.blocks]:
        for section in SECTIONS:
            visit(getattr(block, section))
    if values:
        ops = [lsc_value_op("value", writes=[name], reads=[], value=values[name]) for name in sorted(values)]
        program.blocks = [ir_block(name=f"{START_BLOCK}values", body=ops)] + list(program.blocks)
    return len(values)


#: an immediate two adds merge into - within every ISA's add of one
#: (RISC-V's addi: 12 bits signed)
MERGED_IMMEDIATE = 2047


def _step(op):
    return (op.properties or {}).get("step") if isinstance(op, lsc_addr_compute) else None


def _regs(op):
    return op.indices[0].component, op.indices[0].indices[0], op.indices[1].indices[0]


def spells(program: ir_program) -> bool:
    """
    Whether a program's moves are spelled (SPELL_ADDRESSES) - under any
    budget: the offsets planned with them
    """
    return SPELL_ADDRESSES
