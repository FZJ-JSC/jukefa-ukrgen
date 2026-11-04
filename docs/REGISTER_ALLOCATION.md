# Register allocation: one pass, after scheduling

## Where it is

Three places decide registers, and they have to agree:

- **The model** fits each loop input's ring (`fit_registers`: a register per
  tile or rings shared, `--COMP-data-regs`) and assigns tiles to ring registers
  by least recent use, before anything is scheduled.
- **The scheduler** counts the data values alive while placing operations
  (`_register_state`) against a budget, so its order fits (`--mru`).
- **The emitter** allocates as it emits: `reg()` takes a register when a value
  is first used - vectors from the bottom, FP scalars through the tracker's
  sharing with vector registers, register groups consecutive and aligned (RVV,
  `structfuse`), `bounds` for constrained vector registers - and `release()`
  frees it: `straight()` at a block's start (what no later block reads) and
  after a value's last use; a loop block's sections never (the model's rings);
  an element loop's body by `straight()`'s rule with liveness across its back
  edge (0325); `slices()` by its own register sets and `dead_after`. Index
  vectors (`index_vector`) and helpers' scratch registers take registers from
  the same tracker.

Every disagreement so far came from two of these: the gathers' index vectors
the scheduler didn't count (0292), a slice loop's body budgeted 28 vector
registers where the emitter held 30 (the per-copy temporaries attempt), a
scalar's liveness across loops (0325).

## Where it goes

The scheduler orders operations on virtual registers, aware of pressure; one
pass after scheduling assigns every physical register from the final order;
the emitter only looks registers up.

- **One value, one virtual register**: each copy's temporaries their own -
  no false dependencies for the scheduler.
- **Exact liveness over the scheduled program**: a value carried across a
  back edge (an accumulator, an invariant, a value preloaded at a body's end
  and read at its start) live over the whole loop, one register; copies'
  temporaries overlapping exactly as far as registers allow.
- **Classes and constraints**: slice index registers (w12-w15) and governing
  predicates (p0-p7) from the signatures' operands (asmgen's `operand_values`);
  RVV's LMUL groups aligned, structure loads' consecutive registers; ZA tiles;
  SVE's d and s registers the low parts of z registers - aliasing, not scalars
  from the top.
- **A defined failure**: what doesn't fit known where, before emitting - a
  tighter schedule, a smaller unroll or preload, a spill (ADDRESSING_PLAN step
  5) - not an emitter failing on its way.

What stays: the scheduler's pressure model (its schedules should usually fit -
a heuristic, no longer something to match), clustering (pressure).

## Steps

1. **One allocator in the emitter.** Every data register taken and freed
   through one object (`allocator`: the tracker, the virtual-to-physical map,
   groups, bounds, the FP sharing) with two operations - take a value's
   register, free it - and every release point (`straight()`'s, an element
   loop's, `slices()`') a call of it. Moved code: byte for byte the same.
2. **The allocation computed before emitting.** A pass walks the scheduled IR
   in emission order with the same allocator and the same release points -
   the registers index vectors and helpers' scratch take as events of their
   own - and leaves the map; the emitter's `reg()` looks values up. Byte for
   byte the same (the golden kernels, every shipped configuration's sizes).
3. **Loop bodies with exact liveness across the back edge**: element and
   slice loops first - each copy's temporaries their own, `slices()`' register
   sets and `dead_after` gone, no budget for the emitter to match.
4. **Constraints and aliasing**: the slice index, governing predicates, LMUL
   alignment, structure loads, SVE's scalar aliasing - from the signatures.
5. **The k loop**: the model's rings a pressure budget, the allocator assigning
   the registers, the preload shift's no-second-occupancy bound a liveness
   fact. Kernels change: measured.
6. **General registers** - pointers, walkers, counters, offset registers (and
   with them `auto`'s second run) - then spilling.

Each step's check: the golden kernels, every shipped configuration's sizes
(the tools/allcfg.py comparison), the qemu-run tests; from step 3 on,
instruction counts and runs where kernels change.
