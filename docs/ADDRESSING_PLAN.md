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
   Setup values as an IR setup block, after - below (**Setup in the IR**).

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

   **Setup in the IR.** The emitter still computes the kernel's setup
   itself (emit: parameters, then per region start_addresses, start_indexes,
   loop_counts, then the dispatch): no IR pass sees it - the speller's merge
   (merge_ops: a copy and its first step one instruction) never met the
   stride pointers' copy-then-add (0353 then added add_bytes_from to the
   emitter: against this plan, gone again here), the scheduler never placed
   it, the dispatch tests the same predicates try after try. Each value an IR
   operation instead, in the section where the emitter starts it now, the
   emitter only allocating and spelling what the IR says:
   1. **Address starts.** ir_program.addr_setup already says where each
      address register starts; an lsc_addr_compute from the component's
      base parameter (a pseudo address register, the parameter's: position
      0) to the start, in the first section of the block whose region starts
      the component (a case's own, where it starts there) - the copy and its
      first move then merge_ops' (add_bytes_from gone). The parameter's own
      register the last one's where nothing later needs the base (the
      emitter's reuse now): the start a move in place.
   2. **Loop counters.** loop_counts' k over the unroll and its remainder:
      value operations in the loop block's setup, the counters virtual
      registers.
   3. **Setup values.** The offset registry's values - strides, their
      multiples, vector lengths in bytes and elements (stride_reg,
      offset_value, vl_elements, the preallocated recipes) - value operations
      at the point the emitter places them now (region starts, the
      dispatch's setup), spelled by the speller (shift-adds, Zba). Now each a
      recipe computing into a register allocated where first needed, its code
      into late_setup (after the ISA's setup) or dispatch_setup (after the
      dispatch's loads, a stride deferred there), never scheduled; preallocate
      replaying what an emission found it needed:
      1. *Steps read their values*: a spelled step's value (`("reg",
         ("vl_bytes", dt), "add", 0)`) an operand of its operation, read by
         name (lsc_reg_type.value) - what orders it after the value's
         operation; nothing writes them yet, the kernels the same.
      2. *The values steps name, computed in the IR*: after the spelling,
         value operations (lsc_value_op) for each, in a setup block at entry;
         their recipes' code in place, not late_setup - preallocate gone for
         them.
      3. *Values of deferred strides* in the dispatch's block, once step 4
         makes it IR (dispatch_setup until then).
      4. *Offset registers as options*: the planned offsets (offset_plan, its
         ranks) value operations the emitter may give registers - in rank
         order, while registers last - each step using one carrying its
         fallback already: the eviction now (greg's) the same choice, made
         before; a kernel failing only where a needed value finds none.
   4. **The dispatch.** Its predicates - C's unit stride, beta 0 or 1, alpha
      1 - value operations computed once, the cases a decision tree of
      branches on them (a case's try now re-tests from scratch).
   5. **Index vectors and masks.** start_indexes' index vectors, the tail
      masks: setup operations of their blocks.
   6. **Scheduling across the dispatch** (optional, a flag: say
      --schedule-across-dispatch). A block is the scheduler's unit and the
      dispatch a boundary: the program's blocks are scheduled once, shared by
      the cases, each case's on its own - liveness looks across it, no
      operation moves across it: a case's C loads can't start while the k
      loop's last FMAs run (K3's strided epilogue: its loads' latency
      exposed). With the flag the dispatch moves before the k loop's last
      iteration (its predicates parameters only), each case's path one
      straight-line block - the last iteration (epilogue, tail) and its
      first block - scheduled as one; the paths' longest common scheduled
      prefix back before the branch, so code grows only where a case's
      schedule differs (twelve cases: up to twelve copies of K3 vm 4vx6's
      70-odd instructions). A few cycles off a call - in-order cores mostly
      - for code size: the user's choice. After step 4 (where the branch sits,
      how it's tested); each path allocated on its own, as the emitter's
      copied state per case does now.
   Each step: the kernels' instruction counts no higher, the golden kernels
   re-recorded where they change, the full suite and K3's kernels under qemu.

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

## RVV findings

The integer arithmetic of RVV's generated kernels (tools/addr_patterns.py),
K3's dgemm (x100: stride pointers A, B, C 4 each) and fma_vf_m2's, per kernel:

| | K3 x100 | fma_vf_m2 |
|---|---|---|
| before the k loop | 16 | 14 |
| the k loop, per iteration | 8 | 9 |
| the block after the loop | 10 | 9 |
| the epilogue's dispatch | 27 | 27 |
| the epilogue's cases, all (one runs) | 357 | 180 |
| an expression again, its sources unchanged | 54 | 12 |
| a pointer stepped forward and back | 22 | 10 |
| pointer steps between its accesses (serial) | 9 | 9 |
| a copy, then an operation on it | 7.5 | 6 |
| li and mul for a small constant | 1.6 | 1.3 |

What they are, by cost:

1. **The block after the loop restores dead pointers.** K3 vm 4vx6's:
   A's four pointers bumped for an iteration that doesn't follow, `li s4,4`
   and `mul s4,t1,s4` four times (4*t1 - the prologue's t4), the bump
   subtracted. A's pointers are dead after the loop (the epilogue walks C):
   0302's rule - a looped block's tail moves its walked registers back, it
   repeats - applied where the block doesn't repeat and the registers are
   dead. Fix: the restore only for a block that repeats or registers live
   after it; the last iteration's bumps of dead registers dropped.
2. **Loads and stores walk C with pointer sets of their own.** K3's last
   case: C + cs_c in a1, a2, s1, s3, s6; C + 2cs_c and C + 4cs_c twice each
   (from t6, a copy of a3, and from a3). Twice the arithmetic and the
   general registers - what ran out at unroll 2 (vm 4vx6: unroll 1 of 2).
   Fix: a load and the store of one address share its register.
3. **The walk forward, then back.** A walker crosses C's columns, steps back
   (`sub a0,a0,s8`, s8 = 5*cs_c), then on to the next row block (`add
   a0,a0,t5`) - after it the walk serial (`vlse64 v1,(a0); add a0,a0,a7;
   vlse64 v2,(a0); ...`: each access waiting on an add, where the first
   block's pointers were independent). Fix: rotate the pointers (each
   column's its own, independent) or walk in a serpentine order - no step
   back, no chain.
4. **Small multiples by li and mul.** 5*cs_c as `li s8,5; mul s8,a7,s8`,
   twice. Fix: shift-and-add (`sh2add s8,a7,a7`), computed once.
5. **A copy, then an operation on it.** `add t3,t1,0; sh1add t3,t1,t3`
   (`sh1add t3,t1,t1`), `add s1,a1,0; add s1,s1,t1` (`add s1,a1,t1`), `add
   t6,a6,0; add t6,t6,-8` (`addi t6,a6,-8`). Fix: three-operand forms.
6. **The dispatch repeats its tests.** Each try recomputes rs_c - 8 (`add
   t6,a6,0; add t6,t6,-8`), reloads beta and alpha, rebuilds 0.0 and 1.0
   (`fcvt.d.w`; `li` and `fmv.d.x`), and branches twice (`beq` to the case,
   `j` to the next try) - about ten tries, a hundred instructions a call.
   Fix: each predicate once, a decision tree on them.
7. **B's second pointer.** K3's B: `s3` and `a2` (8 bytes apart), both bumped
   by 48 every k step - fld takes immediates up to 2047: one pointer reaches
   all six columns. One add an iteration (B-stride-pointers 4, K3's).
8. **Unrolling where per-copy addresses don't fit.** RVV's vector loads take
   no offset: a second copy's A accesses get address registers of their
   own; where they don't fit the flow fails and the family builder halves
   the unroll (run_unrolled, the error dropped). Repeating the unroll-1 body
   - the pointers walked between copies - always fits. Fix: that fallback in
   the address stage before failing; run_unrolled saying why it halved.

