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

1. **Spelling in the IR** - done.
   1. Steps in the IR, emitted one instruction each; the kernels byte for
      byte the same (ukrgen 0265; test_spelled_addresses compares the golden
      kernels with and without).
   2. The decisions out of the emitter: specializers/addresses.py
      (`address_speller` - the ISA's capabilities, `move_steps`,
      `scaled_steps`, the steps' deltas, the rewrite); the emit stage spells
      each program, the emitter emits a step's instruction (ukrgen 0266).
2. **The offset registry in the specializer.**
   1. *Values placed where their inputs are* - done (ukrgen 0267). A setup value - an offset,
      `vl_stride` - computed where its inputs first all exist: at entry
      when they come in registers, right after the dispatch's loads when one
      is a stack parameter the emitter defers there (C's strides, x86's
      beta), its register allocated there too (none held through the k
      loop). Deferral makes it safe: a deferred parameter's component is
      used only in the cases. The planner's exclusions go (a deferred stride,
      C's storage aliases' names), and nothing loads early - the root of
      NEON's transposed general C and AVX-512's storage branches. Each
      value's computation in order where it's placed (a scratch register
      freed for the next value: 0263's lesson).
   2. *Offsets a cache, the budget a cap* - done (ukrgen 0268). A needed
      value finding no general register takes the least valuable offset's
      instead, in that region only (a case starts from the dispatch's
      offsets): its moves spelled out from there. max-offset-registers
      limits the offsets rather than claiming registers - AVX-512's storage
      branches at 2, the K3's sgemm vm 3x6, 3x8, 4x6 at 4 build (they ran
      out).
   3. *The planner in the speller* - done (ukrgen 0269). Its ranking (uses, a loop's body
      tenfold, times the instructions a register saves) over the IR's own
      moves; a chosen offset a named value (`("offset", component,
      polynomial)`), a move it covers one step adding it - from another
      register in one add where the ISA takes three operands. Every move
      spelled, under any budget; the emitter's planner, its cost and
      `address()`'s whole-move paths go.
   4. *`auto` in the emit stage* - done (ukrgen 0269; the spare registers
      counted over the whole kernel still - before and after the dispatch
      apart is open). Spelled and emitted without offset
      registers, the spare general registers counted - before the dispatch
      and after it apart (C's offsets live only in the cases) - then
      planned again from the program as it was before spelling (a copy) and
      emitted.
   5. *Tests on the old failures* - done (test_offset_registers_deferred_
      strides, test_offset_registers_auto, test_widen's address variants): NEON's general-stride C, AVX-512's
      storage branches, the K3's vm 4x6, each under a budget; the mixed-
      precision variants (test_widen).
3. **`addrmerge` on steps, the scheduler seeing them** - done.
   1. Spelling before scheduling - done (ukrgen 0271): the post-specialize
      stage spells (after addrmerge and ldinc), the scheduler places each
      step; the golden kernels as many instructions, k loops included, in
      another order (recorded anew). `auto` the flow driver's: a first run
      without offsets measures, a second runs with the spare registers
      (families' run_flow; the command line runs once - no offsets).
   2. Merges where shorter - done (ukrgen 0272): after the spelling, before
      scheduling, adjacent steps of one register - a run of identical adds
      into shifted ones (where the ISA shifts the operand), immediates into
      one, cancelling pairs gone, a copy and a step on it into one step from
      the source (three operands). The golden kernels 4055 -> 3855
      instructions, their k loops the same; the K3's sgemm vm 2x14 2124 ->
      2044, trans14 256 -> 240, the K1's sgemm 2157 -> 2097.
   3. Setup values spelled the shortest way - done (ukrgen 0270): k vector
      lengths a shift or a multiply (`vl_multiple`'s k - 1 adds gone), the
      vector length in bytes one shift from its register, offset values
      seeded with their first term; the K3's trans14 setup 39 -> 24
      instructions, the K1's 50 -> 28.
   4. Scratch multiplies three steps - done (ukrgen 0273): the count in a
      scratch register, the multiply, the add (a group, in order - moves of
      one register - the scheduler free to place other work between them);
      no register free at the first, the last spells the run. Setup's own
      multiplies stay one step (emitted where made).
4. **Column pointers gone.**
   1. Configurations on walks (`column-pointers: {C: 0}`; the K1's sgemm vm
      2x14 2161 -> 2047 instructions).
   2. x86's lane walks no costlier than its lane walker.
   3. The mechanism removed: walks over the pattern's registers
      (`phase+rotate`, `phase+blocked:N`) everywhere.
5. **Spilling** (later): a general register saved to the stack in non-loop
   code and reloaded where needed - a user parameter, for x86's 16
   (fngen's frame its slots).
6. **The emitter's other decisions** (later): `slices` (slice loops: the
   register sets rotated across unrolled copies, preloads, the slices'
   walks, temporaries freed) - a pass's duties; setup values as an IR setup
   block.

## Mixed precision

A vector length's bytes are a component's: a value register is keyed by
the element size it's in, and a move is spelled in its component's (FP16 A
and B into FP32 C; FP32 into FP64 on RVV). test_widen's address variants
run every kernel kind under the walks, rotating registers and offset
registers.
