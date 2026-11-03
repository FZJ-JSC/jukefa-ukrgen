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
4. **Stride pointers gone** - done as a default.
   1. Configurations on walks; none by default (0292: every shipped
      configuration compared, no size lost - the K3's kept by its tuner's
      measurement, RVV's walks dependent adds).
   2. x86's lane walks no costlier than its lane walker (0274, 0275).
   3. The mechanism stays, a user parameter: `stride-pointers` (0294 - kept
      per component, base and strided term: a vn's rows as a vm's columns).
5. **Spilling** (later): a general register saved to the stack in non-loop
   code and reloaded where needed - a user parameter, for x86's 16
   (fngen's frame its slots).
6. **The emitter's other decisions.** `slices` decided a slice loop's
   addresses itself; moved to the specializer's module, the kernels byte for
   byte the same: its access columns (0296: which columns, vector lengths as
   immediates, a pointer each within `--loop-gregs`), its walkers for run-time
   counts (0303), its placements (0306: each access's move and immediate, an
   iteration's step on). The rest - register sets rotated across copies,
   temporaries freed after their last read, preloading - goes with the loop
   itself into the IR. `lsc_loop` was an actual loop - its block an IR
   block, loops among its operations - and narrowed into a virtual
   instruction for one tile: one iteration's template, the emitter making
   the loop of it (SME's slices; the general VLA loops: `vla_lanes`' fills
   and drains - RVV's fld + vfslide1down, vfmv.f.s + vslidedown + fsd; SVE's
   insr). The builder makes the loop as it walks a resolution's steps
   (`slice_loop` for a level of slices, `move_vla`/`drain_vla` for a count
   known at run time only), so the IR never holds the operation the solver
   chose. Back to a loop of the IR, made late:
   1. **Tile operations until specialization.** The builder emits the
      operation - an `lsc_load`, `lsc_store` or `lsc_transformation` of the
      whole tile or vector (the loop's anchor: a vector access from its first
      element) - its loop kept with it. Done for the VLA fills and drains
      (0309: the k loop's building treats one as the loop it stands for - its
      copies a loop of their own; `vectorize_loops`, `unroll_loops`,
      `cluster`, `copyprop` see through it), the kernels the same; SME's
      slices next (`hoist_slices` needless, `forward_slices` forwarding at
      tile level).
   2. **The specializer split: forms, then addresses.** An access's signature
      depends on its address only through which forms take the immediate:
      every operation's forms first (0310: usable signatures, checks), the
      addresses after - next as a stage of their own after `isa_specialize`.
   3. **A loop-building stage between them**: each standing operation's loop
      as an `ir_block` - its index, count, copies (each copy's temporaries
      virtual tiles of their own), sections (prologue, body, last iteration,
      tail), advance, the k loop's preloads per stream - adjacent operations
      over the same tile, orientation and count fused into one loop as it's
      made (`fuse_slices`' condition). Its decisions after the forms are
      known: the immediates a form takes (SME's slice operand: the unroll's
      copies), post-increments, a vector access instead (`vectorize_loops`),
      register classes (ZA's index registers). Element loops first; the k
      loop later - the model builder emitting one iteration and a loop
      descriptor, every loop built one way.
   4. **Addresses after the loops**: positions, walks, moves back, advances,
      immediates, offsets over every section, nested or not - each copy its
      own address, its form the one that address allows.
   5. **The scheduler in a loop's sections**: within the registers the
      enclosing section leaves, the copies' tiles renamed into them - no
      register sets rotated, nothing freed by hand.
   6. **The emitter's `block` for nested blocks**: the count, the index (SME's
      w12-w15 a register class; the slice operand its index and the copy's
      immediate); `slices` and `loop` gone.
   7. **General first**: the VLA element loops (RVV's `vla_lanes`,
      tests/specializers/test_vla_repeat.py under qemu at two VLENs; SVE's
      insr) before SME's slices (tests/stages/test_sme.py, the SME and SMESVE
      configurations) - nothing of either special to the other. Measured:
      instructions, right under qemu.
   Setup values as an IR setup block, after.

   **Loops, from here** (after 0309-0323: the VLA element loops wholly the
   IR's but their counter; SME's tile slice loops standing operations):
   - **An STO as a virtual tile operation of a higher-level STO.** What a
     loop over slices does to a tile (slice_compute: a slice moved out, its
     arithmetic and accesses, moved back) is an STO; the higher-level STO's
     operation on the whole tile stands in the IR for the loop of it - the
     standing operations' general form (a VLA fill or a tile's load: an STO
     of one access an element). Fusion where adjacent virtual tile
     operations over one tile and its slices are made one loop; recursive.
   - **The renamer in a loop's body**: copies' temporaries virtual tiles
     renamed within the registers the enclosing section leaves - a value
     carried across the back edge one register, a preload loaded at the
     body's end into the register the next iteration's start reads - the
     emitter only applying it (the element loops' scalars, allocated by the
     emitter since 0315, and the slice loops' register sets too).
   - **Preloading by the mm STO's mechanism**: the builder's preload shift
     (prologue, shifted copies at the body's end, the last iteration
     without) for a nested loop's block as for the k loop - one code.
   - **Constrained virtual registers**: a virtual register's file narrowed
     to what its operands' signatures allow (asmgen's operand_values) - SME's
     slice index (a slice access's _rowreg/_colreg: w12-w15), SVE's governing
     predicates (p0-p7) - the renamer allocating from that set; no register
     type of asmgen's (its gen.valid_rcregs unused).

7. **Data offsets, resolved late** (later): carry only what each data
   register must hold at each point - the data's offsets - and resolve them
   into loads, stores, address bumps and pointers where everything is known:
   forms, copies, the schedule's order, the registers left. Loads, stores and
   address generation then fully decoupled - the end state of steps 1-6.

## Mixed precision

A vector length's bytes are a component's: a value register is keyed by
the element size it's in, and a move is spelled in its component's (FP16 A
and B into FP32 C; FP32 into FP64 on RVV). test_widen's address variants
run every kernel kind under the walks, rotating registers and offset
registers.
