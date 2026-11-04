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

Virtual registers keep their names - no SSA, by design: the names carry the
allocations a user fixes per component for the STOs (an input's ring,
--COMP-data-regs; the accumulators), the address registers' fixed ones,
and a register whose lanes or slices are written piece by piece (a lane
load, a VLA fill, a ZA tile's slices) - a partial write reads and writes
its register, it doesn't start a new value. `cluster` finds its
dependencies by the names.

- **Fixed and flexible.** A component with a fixed allocation keeps its
  registers. Others - C, the vectors a loop over slices moves through,
  scratch registers - are flexible within a budget or a max-reg limit: a
  value takes a new virtual register (a name of its own) or reuses a dead
  one.
- **The order**: `cluster` (chains together: the order of least pressure) ->
  **rename** (each flexible value onto a dead register or a new one within
  its budget - the reuse a write-after-read or write-after-write dependency
  the scheduler keeps) -> **schedule** (dependencies only: no register model
  of its own, the renaming bounds the pressure) -> **allocate in two passes**
  (an analysis pass - live ranges per virtual register across back edges
  and partial writes; each register's class and constraints from its
  operands' signatures: asmgen's operand_values for SME's slice index
  (w12-w15) and governing predicates (p0-p7), groups consecutive and aligned
  (RVV's LMUL, structure loads), tied operands (accumulating FMAs, x86's
  destructive forms), files from the tracker's pools (SVE's FP registers the
  low parts of its vector registers); the fixed allocations - then an
  allocation pass: the most constrained first, the fixed ones as given, the
  rest by least recent use, giving the scheduler room to load ahead) ->
  **emit** (registers looked up).
- **One liveness**: the analysis pass's - the renamer, the allocation and
  any check use it, nothing else computes its own.
- **A loop over slices' index register**: each virtual tile operation its
  own; fusion (fuse_slices) merges loops traversing the same value range -
  the whole VLA range - and with them their index registers, before the
  renamer; the allocation meets w12-w15.
- **A defined failure**: a fixed allocation or budget that doesn't fit, or a
  constraint no register meets, known in the analysis pass with where.

## The liveness computed now, and what replaces it

| Where | What it answers | Afterwards |
|---|---|---|
| model: `fit_registers`, rings, the preload shift's occupancy bounds | an input's registers, a tile's ring slot | the fixed allocation stays the user's; the slots the renamer's, the bounds the analysis' |
| scheduler: `_register_state`, `_across`, `live_out` | values live while it reorders | gone: the renaming bounds the pressure |
| emitter: `straight()`'s releases, 0325's loop bodies, `peak_registers` | when a physical register is free; a loop body's peak | gone: the allocation pass |
| `slices()`: local values, `dead_after`, register sets; `expand_copies`' local values | a slice loop's temporaries | gone: flexible values renamed |
| `copyprop`'s events | whether a copy's source survives its uses | the analysis pass' |

The 33 of SMESVE's 2x4x4 (0329's fallback) is what this removes: the scheduler
broke its own budget (a soft one) - after renaming there is no budget for it
to break.

## Steps

1. **One allocator in the emitter** - done (0327).
2. **The analysis pass**: live ranges per virtual register (back edges,
   partial writes: lanes, slices), classes and constraints from the
   signatures, fixed versus flexible - one function; the checks above
   answered by it, the kernels byte for byte the same.
3. **The renamer** after `cluster`: flexible values onto dead registers or
   new ones within their budgets; the scheduler's register model gone.
   Kernels change: instruction counts, runs.
4. **The allocation pass** replacing the emitter's: fixed as given, the most
   constrained first, least recent use; the emitter looks registers up.
5. **The slice index register** per virtual tile operation, merged by fusion
   on the same value range, allocated within w12-w15.
6. **The rest into the IR** - address registers' fixed allocations, walkers,
   counters, masks, index vectors, scratch, offset registers (and `auto`'s
   second run) - then spilling.

Each step's check: the golden kernels, every shipped configuration's sizes
(tools/allcfg.py), the qemu-run tests; from step 3 on, instruction counts and
runs where kernels change.
