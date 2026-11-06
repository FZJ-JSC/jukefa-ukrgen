# Register allocation: two passes, after scheduling

## Where it is

Four places decide registers, and they have to agree:

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
- **The address registers** (the general file): the model numbers a component's
  (`--COMP-addr-regs`, its pattern), the specializer adds more with `new_reg`
  - stride pointers, a loop over slices' columns and walkers, a scratch
  address - and the emitter gives each a general register when it is first
  named (`aregs`, lazily) and frees it by hand: a loop over slices' pointers
  at its end (`release_pointers`; the columns' after, ADDRESSING_PLAN 6.6.4),
  a block's at its end (`release_aregs`). No liveness and no MRU: a column's
  register is the allocation order's accident, and holding one to a block's
  end cost three packm kernels their build.

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
- **Address registers are virtual too.** A component's numbered address
  register, a stride pointer, a loop over slices' column or walker, a scratch
  address, a counter, a mask, an index vector: names, not registers. The fixed
  ones stay as given - the base parameters' (the calling convention's
  registers), a loop's carried pointers, SME's slice index (w12-w15), a
  counter an ISA requires in a named one - the flexible ones renamed and
  allocated as any other value: a column alive from its setup to the end of
  its loop, a walker, a scratch address, an offset's register. Least recent
  use among the file's registers left (`--max-gregs`, the callee-saved ones
  by the tracker's priority).
- **The allocation is static, the operation keeps its component.** The
  allocation pass binds each virtual register - of either kind - to a physical
  one once; the emitter looks the number up. An address register's instruction
  is formed from the operation's own component and register type: a
  half-precision A's address register, an FP32 C's and a tile's index each
  their element size and file - never from a value found while emitting.
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
  rest by least recent use, giving the scheduler room to load ahead; the
  address registers in the same two passes, their live ranges the IR's) ->
  **emit** (registers looked up, nothing taken).
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
| emitter: `aregs` taking a general register when first named, `release_aregs` per block, `release_pointers`, the columns' release after a loop, `index_vector`'s reservation | which general register a pointer, a column, a walker, an index vector has, and when it is free | the analysis pass' live ranges, the allocation pass' choice |
| `copyprop`'s events | whether a copy's source survives its uses | the analysis pass' |

The 33 of SMESVE's 2x4x4 (0329's fallback) is what this removes: the scheduler
broke its own budget (a soft one) - after renaming there is no budget for it
to break.

## Steps

1. **One allocator in the emitter** - done (0327).
2. **The analysis pass**: live ranges per virtual register (back edges,
   partial writes: lanes, slices), classes and constraints from the
   signatures, fixed versus flexible - one function; the checks above
   answered by it, the kernels byte for byte the same. Done: one liveness
   (`lsc_model/liveness.py`: the emitter's, the scheduler's, `copyprop`'s,
   `slices()`' and `expand_copies`' local temporaries - 0333, 0334); a
   value's register class, its units and fit by the tracker's knowledge
   (`lsc_model/classes.py`, asmgen's tile types and `storage` - 0336, 0338,
   0341); a renamed value's data type its own (`owner`, `value()` - 0335).
   Open: a vector's bounds still the emitter's (`_register_bounds`).
3. **The renamer** after `cluster`: flexible values onto dead registers or
   new ones within their budgets; the scheduler's register model gone.
   Kernels change: instruction counts, runs. Done: a loop body's
   temporaries within the registers there are (0337, no serial fallback
   since: 0339); a straight-line section's flexible values (0342; the
   default since 0347, `--no-rename`), `--rename-from` new (the default),
   dead, distance (0343: `new` schedules best - the straight-line sections'
   distance shortfall NEON -26%, SVE -51%, RVV -15%, AVX2 the same, K3's
   modelled cycles -14%; `dead` four times worse); `--max-{g,f,v,t}regs`
   (0343: callee-saved registers left out by priority); registers released
   by liveness, not their names' mentions (0345); a lane or block written
   reading the rest (`liveness.keeps`, 0344, 0346), a part waiting for the
   part before unless `--schedule-partials-independently`. The scheduler's
   register model still schedules loop bodies and sections whose names
   don't bound what's live. A tile's slices (0348): inside a loop over
   slices a slice written keeps the rest of the tile, as a lane does (one
   slice index, a slice by its immediate); the loop, covering its tiles'
   slices, writes them whole - `copyprop_tiles` sees no read of a tile so
   built, `--schedule-partials-independently` covers slices. Open: register
   groups not renamed; the k loop's rings.
4. **The allocation pass** replacing the emitter's, for the data registers:
   fixed as given, the most constrained first, least recent use; the emitter
   looks registers up. The address registers' the same pass, step 6.
5. **The slice index register** per virtual tile operation, merged by fusion
   on the same value range, allocated within w12-w15.
6. **The address registers, walkers, counters, masks, index vectors, offset
   registers - the same two passes.** The analysis': live ranges over the IR -
   a loop's carried pointers through its back edge, a column from its setup to
   the end of its loop, a walker's, a scratch address's, a mask's and an index
   vector's region, an offset's register, each loop's counter - the fixed ones
   as given (the base parameters' and the calling convention's, SME's slice
   index within w12-w15, a counter the ISA requires in a named register), each
   other's constraints from the instructions taking it (asmgen's
   operand_values), and every constrained register's priority lowered - the
   slice index's, a governing predicate's, an indexed operand's - so the
   allocation takes it last for anything else (the emitter's
   `_required_priorities`, the analysis'). The allocation's: the fixed ones as
   given, the most constrained next, the rest by least recent use among the
   file's registers (`--max-gregs`, the callee-saved priority), a column or a
   walker dead where its loop ends. Then the emitter's `aregs` on first
   naming, its per-block `release_aregs`, `release_pointers` and the columns'
   release go: it looks the number up and forms the instruction from the
   operation's component. Then spilling.

Each step's check: the golden kernels, every shipped configuration's sizes
(tools/allcfg.py), the qemu-run tests; from step 3 on, instruction counts and
runs where kernels change.
