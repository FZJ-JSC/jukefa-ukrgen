# Address moves: one instruction each, decided in the specializer

## Where it is

After specialization an `lsc_addr_compute` moves a register by any
polynomial - constants, strides, vector lengths, a vector length of a
stride - and the emitter spells it: `address()` takes it from another
register in one add where it can (k vector lengths, one stride, a planned
offset), else copies and hands the polynomial to `add_bytes`, which spells
it term by term (`add_scaled`: shifted adds where the ISA shifts the
operand, a multiply into a scratch register for a long run). The offset
planner (`plan_offsets`, `offset_value`) also sits in the emitter: it reads
the specialized IR's moves by their text, ranks them, and swaps a chosen
polynomial's spelling for an add of a register computed in setup.

So the IR doesn't say what an address move costs, and the emitter decides
what the specializer should: three bugs came of it - text matched across a
stack parameter deferred to the dispatch (NEON's general C), across a
storage's alias (AVX-512's row/any), and setup built out of order (a
multiply's scratch register overwriting a vl_stride value). The scheduler
counts one instruction a move; `addrmerge` can't see that two strides are
two adds on a core without Zba, or merge a doubled add into a shifted one.

## Where it goes

After specialization every address move is one instruction of the ISA:

- an immediate add, the immediate in the ISA's range;
- an add or sub of a value register, shifted where the ISA shifts the
  operand (Zba's sh1add..sh3add, AArch64's LSL, x86's lea scale);
- SVE's incb/addvl by a vector length;
- a multiply of a value register by a count into a scratch register (the
  long run's first half; an add of the scratch its second).

Value registers are named, not allocated, in the IR: a stride parameter
(`stride(C,n)`), the vector length in bytes of an element size, k vector
lengths, a vector length of a stride, an offset the specializer registered
(`offset(n)`), a scratch register. The emitter allocates and computes them
as setup values do now (first need, preallocated before the regions) - by
name and element size, never by a polynomial's text.

A move the specializer registered an offset for stays one add of that
offset's register; any other move is spelled into its single instructions
in the IR, in order.

## Steps

1. **Spelling in the IR** - done (ukrgen 0265): emitters/signature.py
   `spell_addresses` turns every move into its steps before the emission
   (after scheduling: the steps sit where the move did, the kernels the
   same byte for byte - the golden kernels compared with and without,
   test_spelled_addresses), `address()` emits a step as its instruction;
   `add_bytes` is `move_steps` and `emit_step` too. Moving the pass before
   scheduling, where the scheduler sees each step, is step 3's: the kernels
   change there. Planned to be: a last specialization pass
   (`spell_addresses`) turns each move into its single-instruction steps by
   today's rules (`address`, `add_bytes`, `add_scaled`), each step's form a
   property of its `lsc_addr_compute`; the emitter emits a step as one
   instruction, resolving its value registers. The planner stays in the
   emitter for now: a move it would take keeps its polynomial (the pass
   leaves moves alone where `max-offset-registers` isn't 0). The kernels
   stay byte for byte as they are - the golden kernels the check.
2. **The offset registry in the specializer.** The ranking (uses, a loop's
   body tenfold, times the instructions a register saves) over the IR's own
   moves; a registered offset a named value register, computed once. The
   budget a number from the family, or `auto`: the registers free in a
   first emission, the specialization run again with them.
3. **`addrmerge` on steps.** Consecutive steps of one register merged where
   that's shorter: stride moves (never worse), a doubled add into a shifted
   one, a copy and an operation on the copy into one operation with the
   source (`slli t3,t0,2`), cancelling pairs; offset values seeded with their
   first term (`sh2add t1,a4,a4` for 5 strides). The setup values' own
   computations (`vl_multiple`'s k - 1 adds) through the same spelling.
4. **Column pointers gone.** Walks over the pattern's registers
   (`phase+rotate`, `phase+blocked:N`) in their place everywhere - once
   x86's lane walks cost no more than its lane walker, and configurations
   like the K1's have moved (`column-pointers: {C: 0}`: 2161 -> 2047
   instructions for its sgemm vm 2x14).

## Mixed precision

A vector length's bytes are a component's: a value register is keyed by
the element size it's in, and a move is spelled in its component's (FP16 A
and B into FP32 C; FP32 into FP64 on RVV). test_widen's address variants
run every kernel kind under the walks, rotating registers and offset
registers.
