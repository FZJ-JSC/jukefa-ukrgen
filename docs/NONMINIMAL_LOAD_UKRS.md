# Microkernels that cannot load every tile once

When a component has fewer data registers than the microkernel has tiles of
it, some tiles have to be loaded more than once. How many times depends on
which register each load writes. The LSC model chooses so that it loads as
rarely as the registers allow. This page describes when that matters, how the
choice is made, and how it compares with the two simpler methods ukrgen has
used before.

## The minimum

Take gemm with an FMA that vectorizes along `m`. One loop iteration with
`--m m --n n --k k` uses `m·k` tiles of A (vectors, `A[m,k]`) and `n·k` tiles of
B (broadcast elements, `B[k,n]`). Tiles are counted in units of what one
operation of the chosen implementation covers. Loading each tile exactly once
gives the absolute minimum:

    m·k + n·k loads per iteration

Whether that minimum is reachable depends on the order of the operations
(`--order`) and on the data registers (`--A-data-regs`, `--B-data-regs`):

- **Order `kmn`.** For each step of `k`, each A tile is used `n` times in a
  row, while B's `n` tiles of that step are revisited for every `m`. One A
  register and `n` B registers load everything once.
- **Order `knm`.** The same with the roles swapped: `m` A registers and one B
  register.
- **Orders with `k` inside.** These keep tiles of several steps of `k` alive at
  once and need more registers: `mkn` needs all `n·k` tiles of B.

So the minimum is reachable exactly when **A has at least `m` registers or B
has at least `n`**, with the matching `k`-outermost order. Then all three
methods described below reach it. Checked on 298 configurations, every
combination of register counts for seven microtile sizes: the condition held
in all of them, and wherever the minimum is reachable the old counter method
reached it at some order (246 of 246).

Everything else is a *nonminimal-load* kernel, for one of two reasons:

- **No order can reach the minimum.** Both operands are short of registers:
  fewer than `m` for A and fewer than `n` for B.
- **The chosen order can't.** The minimum would be reachable, but `--order`
  makes the operand that is short of registers the one revisited in a cycle.

In both cases some tiles are loaded again, and the method decides how many.

## Three ways to pick a register

When a tile is needed that no register holds, it has to go somewhere:

- **Fixed register.** The previous assignment in this model: a tile's register
  is its rank in order of first use, modulo the number of registers.
- **Counter.** The old model: a counter advances on every load, and the load
  goes to the register it points to.
- **Now.** A tile that is still held keeps its register. New data goes:
  1. to a free register;
  2. else to a register whose data is not needed again in this section,
     taking the one accessed longest ago, so the reload lands far from that
     register's last reads;
  3. else to the register whose data is needed furthest ahead.

The third rule is Belady's optimal replacement. It needs the future access
sequence, which the model has: the operations of a section are fixed before
any register is chosen. A section is a loop iteration, a tail, a subtail or a
straight-line block. Operands streamed through a loop aren't reused from one
iteration to the next, so for them the per-iteration optimum is the overall
one.

## Examples

Each entry is one access to a tile `t` of B in register `r`; `*` marks a load.
Tiles are numbered in order of first use.

Three tiles cycling through two registers (`--m 4 --n 3 --k 2`, order `kmn`,
two B registers; the first 13 of 24 accesses):

    fixed     18 loads: *0r0 *1r1 *2r0 *0r0  1r1 *2r0 *0r0  1r1 *2r0 *0r0  1r1 *2r0 *3r1 ...
    counter   24 loads: *0r0 *1r1 *2r0 *0r1 *1r0 *2r1 *0r0 *1r1 *2r0 *0r1 *1r0 *2r1 *3r0 ...
    now       14 loads: *0r0 *1r1 *2r1  0r0 *1r0  2r1 *0r1  1r0 *2r0  0r1 *1r1  2r0 *3r1 ...

- **Fixed register:** tiles 0 and 2 share `r0` and evict each other on every
  pass, while `r1` keeps tile 1.
- **Counter:** always evicts exactly the tile needed next, so every access is a
  load.
- **Now:** rotates which tile is left out.

Six tiles in five registers (same sizes, order `mkn`, five B registers):

    fixed     12 loads: *0r0 *1r1 *2r2 *3r3 *4r4 *5r0 *0r0  1r1  2r2  3r3  4r4 *5r0 *0r0 ...
    counter   24 loads: *0r0 *1r1 *2r2 *3r3 *4r4 *5r0 *0r1 *1r2 *2r3 *3r4 *4r0 *5r1 *0r2 ...
    now        9 loads: *0r0 *1r1 *2r2 *3r3 *4r4 *5r4  0r0  1r1  2r2  3r3 *4r3  5r4  0r0 ...

- **Fixed register:** tiles 0 and 5 collide in `r0` on every pass, while four
  registers never change.
- **Counter:** moves every tile one register along each pass and hits nothing.
- **Now:** gives up one tile per pass, the one needed furthest ahead.

## The best order doesn't make up for it

Choosing `--order` well doesn't let the simpler methods catch up once the
minimum is out of reach. Loads of A and B per iteration, each method at its own
best order:

| sizes | A / B registers | fixed register | counter | now |
|---|---|---|---|---|
| m4 n3 k2 | 2 / 2 | 26 (`kmn`) | 30 | 22 |
| m3 n4 k2 | 2 / 3 | 22 (`kmn`) | 30 | 18 |
| m4 n4 k1 | 2 / 2 | 20 (any order) | 20 | 16 |
| m8 n3 k1 | 3 / 2 | 25 (`kmn`, `mkn`, `mnk`) | 27 | 21 (any order) |

Of the 52 configurations above where the minimum is unreachable, the new
method beats both others at their best orders in 45. The remaining seven have
a single register for A and a single one for B, which leaves nothing to
choose.

The reason is that one operand is always revisited in a cycle. A is reused
along `n` and B along `m`, and only one of them can be the inner index; the
order only decides which operand cycles. When the cycling operand has fewer
registers than the tiles it cycles through, a fixed mapping keeps colliding
the same tiles, and a counter evicts exactly the tile needed next. Choosing by
next use is the only one of the three that handles the cycle well.

## What it doesn't change

- **The order of operations.** That is fixed by the tiling and `--order`. The
  method chooses only which register each load writes, and so which accesses
  need a load at all. The computations come out in the same order.
- **Where loads go.** A load is emitted right before the operation that needs
  it; loads for the same operation follow `--resolve-order`. Preloading, which
  loads a loop iteration ahead, applies only to components with a register for
  every tile of the iteration. With fewer, their loads stay in place.
- **Accumulators and resident components.** Accumulators get one register per
  tile they accumulate. A component kept in registers between STOs, like C
  between `betascale` and the store, needs one per tile, and the model reports
  an error otherwise rather than reloading it.
- **Dependencies for scheduling.** These do change, in a good direction: a
  register reused for new data creates a write-after-read dependency on its
  last read. Taking the dead register that was accessed longest ago keeps
  reloads as far as possible from those reads, which leaves the schedulers
  room to move them up.

## Using it

The method applies whenever a component gets fewer data registers than it has
tiles. For example, A with fewer than `m·k` registers:

    --A-data-regs 3 --B-data-regs 6 --order k,n,m

`--print-ir` shows the loads and registers. The analysis above is in terms of
gemm with an FMA, but the method itself isn't: it chooses registers for any
component of any STO, with tiles in units of the chosen implementation's
extents.

`tests/lsc_model/test_builder.py` (`test_register_reuse`) checks that the
model's load counts equal the optimum and that every operation reads the tile
it needs.
