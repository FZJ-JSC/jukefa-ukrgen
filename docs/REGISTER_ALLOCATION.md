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
  edge (0325); `slices()` by its own register sets. Index
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

A fifth decides *and feeds back*: the emit stage's fewest general registers
left free (`min_free_gregs`), which the flow's driver re-runs the whole flow
with, `max-offset-registers auto`'s budget - the second specialisation that
the decisions below replace.

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
| `slices()`: local values, register sets; `expand_copies`' local values | a slice loop's temporaries | gone: flexible values renamed |
| emitter: `aregs` taking a general register when first named, `release_aregs` per block, `release_pointers`, the columns' release after a loop, `index_vector`'s reservation | which general register a pointer, a column, a walker, an index vector has, and when it is free | the analysis pass' live ranges, the allocation pass' choice |
| `copyprop`'s events | whether a copy's source survives its uses | the analysis pass' |

The 33 of SMESVE's 2x4x4 (0329's fallback) is what this removes: the scheduler
broke its own budget (a soft one) - after renaming there is no budget for it
to break.

## One allocator, two passes: where it lives

`models/lsc/allocation.py`, one class over the IR - `allocation` - the stage's
only driver. Two methods, no state carried between them but the problem it
returns:

`analyse(program, resources) -> allocation_problem` - every virtual register (a data
value, an address register, a value in a general register), with:

- its **file and class**: the tracker's tag, its units (a group's ways, a
  structfuse part's size), its alignment (RVV's groups, structure loads), the
  dtype its instruction is formed from (`owner`);
- its **constraints**: what its operands' signatures allow (`operand_values`:
  SME's slice index in w12-w15, a governing predicate in p0-p7, an indexed
  operand's 4-bit field), ties (accumulating FMAs), and what it shares with
  another file (SVE's scalars the low halves of its vectors - one file with two
  views, so the two must not cross);
- its **live ranges**: positions over the program's linearised IR - block,
  section, operation - with the two things that make a loop a loop written as
  edges rather than as extra positions: a value live from the end of a body to
  the start of the next is **carried** (one range spanning the back edge), and a
  value in a loop's prologue is the same value its body reads (the sections are
  one sequence, the loop one iteration);
- **written in parts** (a lane, a block, a ZA slice): one value, never split
  (`liveness.keeps`);
- **fixed or flexible**: the user's and the model's fixed allocations (rings,
  accumulators, the base parameters' and the calling convention's registers,
  SME's slice index, a counter an ISA names) as given, everything else
  flexible;
- **demand**: per section the values live at once and the names a file needs,
  and per program the demands that don't fit, with where.

`allocate(problem, resources) -> bindings` - static, in one order: the fixed ones first,
then the most constrained (short bounds, ties, groups, slice indices), then the
rest by least recent use over the file's registers left, the low ones kept for
the scheduler to load ahead; a group's registers consecutive and aligned; the
result one number each, bound into the program. No emission, no emitter state.

The emitter then looks every number up: `reg()`, `aregs`, and forms the
instruction from the operation's own component and register type. Which means
these go, all of them the analysis' now: `take`'s lazy allocation,
`free`/`release_aregs`/`release_pointers`/the columns' release/`straight()`'s
per-block releases, the releases after a last use, `reserve`/`unreserve`/`bind` (an anonymous
register is an anonymous live range, a slice loop's set a set of ranges the
allocation keeps together), `peak_registers`/`bounded`/`room` (the problem's
demand), `_register_bounds` (the problem's constraints), and the tracker's
priorities (the allocation's order).

The migration, each step its own commit:

1. **The analysis** - the module, the problem, its numbers; nothing allocated
   from it yet, so the kernels are byte for byte the same. Its first use is
   diagnostic: the counts explain the failures the emitter hits - a loop over
   slices of 36 names for 32 registers, printed with the section and the values.
2. **Data registers allocated from it** - the emitter's `take`/`free` become
   lookups; kernels change (goldens, qemu, counts).
3. **The emitter's dynamic machinery deleted** - the releases, the sets, the
   peak check.
4. **The address registers through the same two passes** (step 6) - `new_reg`'s
   emitter-side numbering, `aregs`' laziness, `release_*`, `settle`.

## The signatures' operands in the IR: the registers an operation never named

An operation's `indices` are the register operands the *model* made: a load's
address and destination, a store's, a transformation's (through `hw_operands`,
the names the builder paired with them). Everything else the chosen signature
names - a governing predicate (`mask(m)`), SME's slice index (`slice_reg`), an
instruction's clobbered operand (AVX's `amreg`) - is not in the operation. The
emitter carries those in `properties`, in `self.masks` and `self.tails`, or as
state (`lsc_state`'s `mask(m)`), and binds them by name while it forms the
instruction (`_predicate`, `slices()`, `signature.py:1291`).

That is what the masks' first move to a value ran into, and what keeps
`_register_bounds` from seeing a load's constraint: the bound comes from
`operand_values` over the chosen signature's operand, and there is no slot to
name it by. So the operands come into the IR, once, after `isa_specialize` has
chosen the signatures:

- **`hw_operands` on every operation**, not only `lsc_transformation`: a
  signature operand name per index slot;
- **a binding pass** after `isa_specialize` that, for each operation's chosen
  signature, pairs the register operands it already carries and appends the
  ones it doesn't - a new `lsc_reg_index` with the operand's `rgt` and a name no
  memory component has (`mask(m)`, `slice(C,0)`: `dtypes.register_types` keys
  by component and number, so a shared name would take a component's data type);
- **`reads` for what the instruction reads, `writes` for what it writes, both
  for a clobbered operand** - `sig.clobber_list` holds operand *names*
  (`asmgen/asmblocks/avx/opmem/signatures.py:89`, `'amreg'`), and a clobbered
  register is read and written by the same instruction: in `writes` alone a
  later reader would be scheduled across it;
- **a class from the `rgt`**, which `classes.TAGS` answers now (asmgen's
  `register_type.tag`).

Then liveness, the renamer and the allocation see them as values: a mask's
range from the set that writes it to its last reader, a slice index's from the
frame to the loop's end, a clobbered operand's as a read-modify-write. And the
emitter forms the instruction from the operation alone - `self.reg(idx, rtype)`
for every operand the signature names, no `properties`, no side table.

Three things that bite:

- **state and the operand are the same fact twice**: a mask is `lsc_state`'s
  `mask(m)` *and*, after this, a value its readers read. `check_state` prunes
  `op.sigs` against the state it walks, so the state entry stays until that
  pruning moves into `isa_specialize`; dropping it first is what lost SME's
  slice store its form (*"no store of a slice's Y takes a plain address at
  slice immediate 0"*).
- **`state_requires` names the mask's value** (`tail(m)`) and the pruning
  compares strings: whatever writes the value has to write that name, or the
  form disappears.
- **the first operation whose mask or slice index enters the allocation
  changes numbering** - re-record and qemu, not byte-identical.

The order, each its own commit:

| phase | change | kernels |
|---|---|---|
| (a) | `hw_operands` on every op and the binding pass; the slots exist, the accesses' masks first - **done** | same |
| (c) | **for masks, this comes before (b):** the mask's value gets a set of its own - `lsc_set(set_mask_tail)` / `set_mask_alltrue` in the entry, its register numbered before the accesses are specialised | same, if the register is the one `tail_mask` took |
| (b) | the emitter reads them: `_predicate`, `slice_reg`/`slice_imm`, `clobbered_mask`, `self.masks`, `self.tails`; the slots become reads, transformations' included | change where numbering does; re-record, qemu |
| (d) | `check_state`'s `op.sigs` pruning into `isa_specialize`, then masks can be values anywhere | same |

Phase (a) is done as far as the accesses go: `bind_operands`
(`irmod/lsc/bind.py`, a required post-specialize pass) gives a masked load,
store or move a slot for its mask - `rtypes` the operand's, `hw_operands` the
operand's name (`amreg`), the operation's `mask_slot` the slot - the value
named `mask(<index>)` where the operation carries its tail's index and `mask`
otherwise, and `sig.clobber_list` is looked at for the write. Nothing is read
or written by the slot yet, and `take` learned the mask file: the lowest free
`mreg` (a governing predicate is p0-p7 and the tracker hands out the highest
first), or a vector register where masks are vectors.

**(b) was tried, for the tail's masks, and it cannot come first.** Reading the
mask from the slot at emission time - `_predicate` through
`self.reg(op.indices[op.mask_slot], rtype)` with the tail's set registering the
register it makes - breaks the **slice store**: *"no store of a slice's Y takes
a plain address at slice immediate 0"*. The cause is not the mask: it is the
**second flow run**. Emission measures the fewest general registers left free
(`min_free_gregs`, `signature.py:280`), and `families.py:54-61` re-runs the
whole flow with `max-offset-registers auto` set from it; registering the mask
value moved that measurement by one, the re-run's offset budget dropped, and
`isa_specialize` chose other forms for the store. Two different machines, two
different answers - and nothing about masks was wrong.

Once the decisions below are in, phases (c) and (b) are small: one path is
left when the allocator has decided, so the speller never meets a variant it
cannot use, and the emitter reads a slot whose register exists.

## Decisions: every path generated, one chosen once

The register budgets are in the wrong places, and the retries paper over it.
There are three notions of "budget" today:

| budget | where | counts | uses `--max-*regs` |
|---|---|---|---|
| the **pool** | the tracker's `max_regs` per file | registers, aliases, reserved ones | no |
| a **section's names** | the scheduler's `register_budget.registers[tag]`, `bounded`, `rename_temporaries(limit)` - `limit = budget.registers["vreg"] - len(held)` | names a section may hold, reuse plus new | no: the scheduler counts its own |
| the **cap** | the emitter's `_register_caps` | registers a file may not hand out | it is the cap, applied after everything is decided |

The renamer's and the scheduler's budget is a *renaming policy* - how many names
a section may hold - and it stays theirs. The pool, the cap and the fewest-free
measurement are hardware facts, and all three belong to the allocator.

`max-offset-registers auto` is the worst of them because it is not a
measurement but an **input**: emit, measure `min_free_gregs`, re-run the flow
with `auto_offset_budget = spare`, specialise again. It is why (b) looked
broken. It goes, and with it the second run. What replaces it is a decision the
allocator makes once:

```python
# models/lsc/decision.py - a value, not a name: the payload is the key
@dataclass(frozen=True)
class decision:
    family : str             # "offset", "tail", "loop", "cap"
    subject : tuple           # (polynomial, component) | (index,) | (name,) | (tag,)
    branch : str = "taken"    # `alternative` is the other answer

#: the branch an operation's presence depends on; None - emitted always
decision : decision | None = None
```

Three things the value buys that the string could not: the payload is the key
(`program.offset_candidates: dict[decision, int]` - no side table to decode a
name from), the alternative is `d.alternative` rather than a `:plain` suffix
`decide` had to trust, and `decide` can now check the invariant the suffix was
faking - **every question asked has exactly one branch taken**, raising where
one has none (dropping both is a kernel that silently does less). A future
`all_of`/`any_of` wraps this leaf when something needs two things to hold; the
pruning and `op.decision` stay as they are.

- **Generation**: the specializer stops choosing. Where it picks one branch
  today, it emits **both**, the register-needing one tagged:
  `lsc_addr_compute(..., decision="offset:ga")` beside the untagged
  immediate-form access, `lsc_store(..., decision="tail:m:mask")` beside the
  vector-length form. Most operations carry no tag and are never pruned.
- **Deciding**: one pass, `decide(program, taken)`, drops what the allocator
  did not take and leaves the rest; the program records `decisions`. After it,
  codegen sees exactly one path - the speller has nothing left to re-fit, the
  emitter nothing to retry.
- **Who decides**: `allocate`. A decision is "is there a register for this?", so
  the same two passes answer it: the analysis counts what the tagged branch
  costs (the general registers of `greg_key`/`greg_peak`, per section), the
  allocation tries the decisions in priority order and returns `taken` beside
  the bindings.

What one tag replaces, all of which grew their own control flow:

| today | becomes |
|---|---|
| `max-offset-registers auto` and the flow's second run | `decision="offset:<comp>"`, the allocator's |
| `--loop-gregs`' hand-counted frame ("at least 2: a counter and a slice index") | `decision="loop:<name>:columns"` |
| `program.tail_vl` (the tail set by the vector length) against the mask route | `decision="tail:<index>:mask"` |
| `--max-{g,f,v}regs` reserving a file's tail in the emitter | a pool cap: `pools[tag] = min(pools[tag], cap)` in `resources` |

The cost: the IR doubles at the decision points between specialisation and the
allocation - few places (offsets per component, tails per index, one column
decision per loop), and pruning happens as early as the decisions are known,
inside the allocation stage.

The order:

| step | change | kernels |
|---|---|---|
| dt-1 | `op.decision`, `decide(program, taken)`, `program.decisions`; unit test with hand-built ops | same |
| dt-2 | the offset path emits both branches tagged - **done**, the budget's plan taken until the allocator decides; forcing the branch the emitter used to choose reproduces the kernels byte for byte | same, and that is the test |
| dt-3 | `allocate` returns `taken` - **done**, the offsets' decisions are its (`allocation.offsets`); the budget's *source* still the emitter's measurement, so the second run stays until the general registers are the analysis' (below) | same |
| dt-4 | `loop_gregs`, `tail_vl` and the `max-*regs` caps become decisions and a pool cap | change; recorded + qemu |

### dt-2, as it is: the two spellings of one move

The decision's substance is one function, `address_speller.spelled(op, planned)`
(`specializers/addresses.py`): a move with the offset's register
(`("offset", component, amount, fallback)`) or without it. So both paths come
from the *same operation*, in place, with no copy of the IR:

- `ranked(program)` - every offset that could take a register, best first;
  `plan(program)` - the best of them the budget reaches (the stopgap: what is
  taken until the allocator says, dt-3);
- `both(op)` - the plain spelling first, tagged `offset:<poly>@<comp>:plain`,
  the registered one second, tagged `offset:<poly>@<comp>`; exactly one of the
  pair is in `program.decisions`, so exactly one survives;
- `program.offset_candidates` - the names, their ranks and their keys; the ones
  taken become `program.offset_plan`, which is what the emitter reserves
  registers by (`decisions.plan`).

Two ordering facts, both found the hard way:

- **Prune before `merge`.** The two paths' moves are adjacent, so
  `merge_ops` would merge one path's steps into the other's. Blocking merges
  *across* decisions instead (`a.decision != b.decision`) is not enough: it
  also blocks the merges a pruned branch would have allowed, and NEON's lane
  kernels lost their tail loop to it. `decide` therefore runs between `spell`
  and `merge` (`flow/stages/irmods.py`).
- **No dead-value pass is needed**, because pruning comes *before*
  `value_setup`: a path taken away leaves no setup value behind. A
  `dead_values` pass over the operations' index slots was tried and is wrong -
  a value op's inputs are not always slots (a `step`'s values, a loop's frame),
  and it ate live values (the lane kernels' tail remainder).

The acceptance, both byte-exact: with the plan taken, the 21 golden kernels are
`same`; with the plain path forced (`plan` returning nothing), the output is
identical to the tree before the decisions for NEON's lane `vm`, RVV's `vn` and
SME's `opa` kernels - the branch the emitter had is the branch that comes back.

### dt-3: the allocator decides, and what it still cannot count

The decisions are the allocation's now: `allocation.offsets(program)` takes the
candidates' registers by rank as far as the budget reaches and gives every other
candidate (and every offset that isn't one) its plain name, so exactly one of
each pair reaches `decide`. The speller offers both paths and nothing else; the
IR pass that prunes runs between `spell` and `merge` (`flow/stages/irmods.py`).

What it cannot do yet is *count*. At the tightest point of a kernel, this is
what the general register file holds:

| kernel | fewest free | in use | of them reserved |
|---|---|---|---|
| NEON `fma_lane` `vm` 1x4 | 17 | 15 | 4 (sp, lr, fp, platform) |
| RVV `fma_vf` `vn` 4x1 | 10 | 22 | 4 |

The rest is the IR's pointers, walkers, counters, offsets' registers and the
values held across regions - and the hold is the part a liveness peak cannot
see: `greg_peak` (the most names live at once) came out at 5-16 where emission
uses 15-22, and agreed with the emitter's fewest-free on one kernel in
twenty-one. So `max-offset-registers auto` still measures by emitting and
re-runs the flow (`injectors/blis/families.py:54-61`); the budget has to come
from a `greg_free` that models what a region holds, which is the general
registers' half of step 6. Until then the decisions are made in one place and
the flow still runs twice - the *ordering* the second run was added for is gone,
which is what dt-2 and this step bought.

## What the loops over slices work around

Where the emitter's remaining allocation duties still show, and what removes
each:

| workaround | where | papers over | goes with |
|---|---|---|---|
| `w12-w15` as an `allowed` bound, the frame's registers taken before the columns' | `slice_frame`, `slice_frames` (`specializers/addresses.py:565`) | placement *order*: the index must have its four registers before a column takes them | (a), step 6 |
| `release_aregs`, `release_pointers`, `room`, `peak_registers`, `bounded` | `emitters/signature.py` | pressure guessed per section | step 4 |
| `moved_in_ir` (`"slice_moves"`, `"slice_registers"`, `"slice_walks"` in `op.info`) | `signature.py:448` | one loop emitted by two code paths | (b), step 3's sections |
| `properties["slice_reg"]` / `["slice_imm"]` written by the emitter | `signature.py:571,637` | the emitter's bookkeeping stored in the IR | (a), (b) |
| `--loop-gregs` ("at least 2: a counter and a slice index") | `flow/stages/emit.py:41` | a hand-counted frame budget | dt-4's decision, its `demand` |
| slice immediates in four bits, `immediates_take`, `MERGED_IMMEDIATE` | `irmod/lsc/unroll.py`, `addresses.py` | encoding limits read before `isa_specialize` trims the signatures | (a): read after binding |
| the mask as state plus `self.tails` | `irmod/lsc/tailmask.py`, `signature.py` | registers with no name of their own | (b), (c) |

## Steps

1. **One allocator in the emitter** - done (0327).
2. **The analysis pass**: live ranges per virtual register (back edges,
   partial writes: lanes, slices), classes and constraints from the
   signatures, fixed versus flexible - one function; the checks above
   answered by it, the kernels byte for byte the same. Done: one liveness
   (`models/lsc/liveness.py`: the emitter's, the scheduler's, `copyprop`'s,
   `slices()`' and `expand_copies`' local temporaries - 0333, 0334); a
   value's register class, its units and fit by the tracker's knowledge
   (`models/lsc/classes.py`, asmgen's tile types and `storage` - 0336, 0338,
   0341); a renamed value's data type its own (`owner`, `value()` - 0335).
   Open: a vector's bounds still the emitter's (`_register_bounds`); the
   general registers have their vocabulary (`greg_key`, `greg_peak`: the
   address, offset and value kinds), and their peak names live - which is not
   the emitter's fewest-free, which is a placement's number, not a liveness'
   (one kernel in twenty-one agreed; the measurement's conclusion is the
   decisions above).
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

7. **The signatures' operands in the IR** - `hw_operands` on every operation,
   `bind_operands` after specialization binding the accesses' masks, the
   `mask_slot` an operation remembers, `take`'s mask file (the lowest free
   `mreg`, or a vector register) - done, inert; the phases (c), (b), (d) above
   finish it. The mask payloads (`set_mask_alltrue`, `set_mask_tail`,
   `set_mask_avl`) and `lsc_set` are in, waiting for their first writer.
8. **Where the LSC pieces live** - `models/lsc/` holds the IR, its passes, the
   allocator and the operations; `offset_polynomial` (the offset/stride
   polynomial, imported as `offpoly`) and `operations` beside them; the
   register tags come from asmgen's `register_type.tag` and the tile counts
   from the tracker's `max_regs`, so `max_tregs` is no longer asked for. Not a
   step of the plan, the ground it stands on: done.

Each step's check: the golden kernels, the SME and SMESVE configurations
(`tools/sme_sweep.py`: 257 kernels, per-family instruction counts), the
qemu-run tests; from step 3 on, instruction counts and runs where kernels
change.

## Where the work stands

The state this was written at, so that a fresh reading of the code can check it
rather than trust it:

- **Done and in**: the analysis and the allocation over the data registers
  (`analyse`, `allocate`, `validate`, fixed rings, the tracker's files and
  storage, `resources.reserved` for the mask file); `lsc_set` and its three
  mask payloads; `bind_operands` and the bound mask slot; the register tags
  from asmgen; the tile counts from the tracker; the consolidation into
  `models/lsc/`; `offset_polynomial`; the general registers' vocabulary
  (`greg_key`, `greg_peak`); the decisions - the dataclass
  (`models/lsc/decision.py`), `decide`/`plan` (`models/lsc/decisions.py`), both
  paths for every offset (`ranked`/`both` in the speller) and the allocation
  answering them (`allocation.offsets`).
- **Inert, waiting**: `mask_slot` and `take`'s mask file (nothing reads a bound
  slot yet); `greg_key`/`greg_peak` (nothing allocates from them);
  `set_mask_alltrue`/`set_mask_avl` (nothing writes them); `resources.bounds`
  (filled by the emitter, not by the analysis).
- **Live, with one number still measured**: the offsets' decisions, against a
  budget the emitter measures for `max-offset-registers auto` - the flow still
  runs twice for that number, though no longer to re-specialise forms.

Gate at that state: 21 golden kernels `same`, the suite 513 passed (1 skipped,
321 subtests), the SME sweep 257 kernels / 107,109 instructions.

The order, approved, each item its own commit:

1. **The decisions' dataclass** - done. The queue's next items carry names of
   their own only as `decision(family, subject, branch)`.
2. **The masks, (c) then (b)** - the mask's `lsc_set` with a register numbered
   before specialisation, then `_predicate` reading the slot and the slots
   becoming reads; `self.masks`, `_all_true`'s alias and the mask's state op go
   with them. Independent of the general registers, and it finishes the work
   the whole line of steps started from.
3. **Step 6a: name the general registers** - first the cheap half: `new_reg`
   *publishes* what it creates (a name per component and number, and the region
   it lives in) so the analysis can see the frame without emission changing;
   then `aregs` becomes slots. 7 `new_reg` sites, 34 `aregs` uses.
4. **Step 6b: "held" as a range** - the renamer's notion in the problem, which
   `--loop-gregs` currently hand-counts ("at least 2: a counter and a slice
   index"). Without it the analysis frees a pointer the emitter keeps, and the
   frame's number stays wrong.
5. **The offsets' plan into `allocate`**, then `auto`'s re-run,
   `min_free_gregs`, `emit_program_measured`'s measurement and
   `auto_offset_budget` go - A/B against today's six `auto` kernels, re-record
   and qemu where they move.
6. **dt-4 last** - `--loop-gregs`, `program.tail_vl` and the `--max-*regs` caps
   as decisions and a pool cap, on top of a greg model that exists by then
   (writing them earlier means writing the same policy twice).
7. **(d)**, the slice loop's control flow into sections, spilling - the tail of
   the plan, unchanged.

The disciplines every one of them owes:

- the golden kernels must be `same` unless the step intends otherwise, and when
  they are not: qemu decides (SME at SVL 256 and 512, RISC-V at VLEN 128, 256
  and 1024), then re-record, then the instruction counts;
- `tools/sme_sweep.py` after every change - 257 kernels, 107,109 instructions
  at the state above;
- an attempt that does not converge is reverted and *the reason written down*:
  the (b) attempt's second flow run, dt-2's merge-across-paths, the `dead_values`
  pass that ate live values. The failures have been the most valuable output of
  this work.
