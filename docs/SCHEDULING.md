# Instruction scheduling

The scheduling stage reorders each block's instructions in the IR, after the
ISA specializer and before emission. It never changes what a kernel
computes: an order is valid when every dependency keeps its direction. What
it changes is how far apart dependent instructions are - and, with an issue
model, which instructions a core can issue together.

## Dependencies

The scheduler (`schedulers/list_scheduler.py`) finds dependencies through
registers between the instructions of a block:

- RAW: an instruction reads a register an earlier one wrote,
- WAR: it writes a register an earlier one read,
- WAW: it writes a register an earlier one wrote.

Registers are the model's (component, number, type); a register group (a
widening accumulator's pair) counts as one register, so what touches a
member touches the group. In a loop's body a dependency may also be
carried: from an instruction in one iteration to one in the next (a load at
the end feeding a use at the start).

## Distances

A distance specification asks dependent instructions to be at least so far
apart:

    dependency:register type:register tag:op:op:distance

- dependency `RAW`, `WAR` or `WAW`,
- register type `data`, `address`, `offset` or `value` (the model's),
- register tag `vreg`, `freg`, `greg` or `treg` (asmgen's), empty for any,
- the two operations' types, empty for any.

`RAW:data:vreg:::13` keeps a vector register's value 13 from its use;
`RAW:data::::13` does so for every data register, vector or FP scalar;
`RAW:address:greg:::3` keeps an address bump 3 from the access using it.
Without an issue model a distance counts instructions, with one cycles.

Options: `--distances SPEC...`; in a blisgen family `schedule: [SPEC, ...]`.

## Placement

The list scheduler places the instructions of a block one at a time: of
those whose predecessors are placed, the most critical - the longest chain
of distances to the block's end - that meets its distances, else the one
falling shortest.

- Loops: a loop's body is placed in rounds; after each, carried
  dependencies falling short of their distances move their producers
  earlier and their consumers later, and the best round is kept.
- Straight-line code (MRU, on by default): the cluster irmod first pulls
  each chain of dependent instructions together before addresses are fixed
  - a C tile's load, scaling, FMA and store - so a few tiles' values are
  live at a time; the scheduler then spreads the chains within a window
  (`--mru-window`, default 12) and a register budget, an instruction taking
  the last free register only where its consumers free one. `--no-mru`
  turns it off; `--mru-reserve N` keeps registers out of the budget.
- Inner loops (slice loops, element loops) inside a block are scheduled as
  loops of their own.

## Issue model

`--sched-cycle-slots "[N:]slot,slot,..."` describes what a core issues in a
cycle (`schedulers/issue.py`); blisgen families: `cycle-slots: "..."`.

- Each slot is a class or classes joined by `|` - one instruction of them a
  cycle; `N` caps the instructions a cycle (default: the slots).
- Classes: `vl vs` vector loads and stores (gathers, scatters, strided),
  `sl ss` scalar ones, `vf vi` vector FP and integer arithmetic, `vp`
  permutes, `t` tile operations, `f i` scalar FP and integer arithmetic,
  `addr` address arithmetic, `br` branches. Where no slot names them,
  `addr` is taken for `i`, `vs` for `vl`, `ss` for `sl`; a class no slot
  takes goes in any free one.

With a model the scheduler fills cycles: an instruction is ready in the
cycle its predecessors' cycles plus the distances allow (a RAW one the next
cycle at the earliest), and each cycle's slots go to the most critical ready
instructions - each into the free slot accepting its class with the fewest
classes, so a flexible slot stays free for what only it takes. The register
budget and the window hold as before. The instructions are emitted cycle
after cycle; the distances are cycles; carried dependencies are measured
across the loop's cycles.

A slot ending in `/n` is taken at most once every n cycles - a port's
rate: `sl/2`, a scalar load every other cycle at most. A class in a slot
marked `*n` holds the slot n cycles: `vl*2|vs|vf`, a vector load keeps
anything else from the vector slot the next cycle. The K1, from its
measured rates: `"2:vl*2|vs|vf,sl/2,addr|i"`.

Forbidden pairs follow a `;`: `"2:vl|vs|vf,sl,i;vf-sl"` - a vector FP
operation and a scalar load never in the same cycle, though each has a slot.

Buckets (`--sched-buckets "vf:5"`, family key `buckets`) model a back end's
queue: a cycle issuing an instruction of the class fills its bucket by one,
a cycle without drains it by one; the class goes first while its bucket
isn't full and waits while it is (unless nothing else issues).

Classes come from the registers' machine types (`rtypes`: VEC, FP, GP,
TILE) - a `vfmacc.vf` is `vf`, a `vle` `vl`, an `fld` `sl`.

Examples:

    "2:vl|vs|vf,sl,i"        SpacemiT K1 (X60): a vector load, store or FP
                             operation, a scalar load beside it, two a cycle
    "vl,vl,sl,vf,vf,vi,i"    two vector loads, a scalar load, two vector FP,
                             one vector integer and one integer operation

## Reports

`--print-schedule` prints, per block: each distance specification's
requested and reached distance and how many dependencies fall short, how
far the register budget was exceeded, and with an issue model the cycles
the block takes as the model issues it - for a loop's body its cycles per
iteration, to compare with what the core measures.

## Using it

    families:
    - family: vm
      ...
      schedule: ['RAW:data::::13', 'WAW:data::::13', 'WAR:data::::13',
                 'RAW:address:greg:::3']
      cycle-slots: "2:vl|vs|vf,sl,i"

An in-order core wants both: distances for its latencies and hazards, the
issue model for what pairs. An out-of-order core needs little - a short
`RAW:data:vreg:::4` - its hardware reorders the rest.

## Limits

- The model is static: no pipeline beyond the slots, no memory latency.
  The cycles it reports are a lower bound for the order emitted.
- The scheduler places IR operations; an operation the emitter writes as
  several instructions counts as one. Address operations are one
  instruction each - on RVV a pointer moving by k vector lengths is one add
  of a register holding k vector lengths, computed at the kernel's start.
  Slice loops' pointer walks and the case dispatch are written by the
  emitter around the scheduled operations.
- Straight-line blocks under a tight register budget may not reach every
  distance; the report says which.
