# Example blisgen configurations (`ukrconfig/`)

`ukrconfig/<isa>/<config>/` holds a BLIS configuration's kernel families, one
file per data type and kernel type:

| file | blisgen option |
|------|----------------|
| `sgemm.yaml` | `--sgemm-config` |
| `dgemm.yaml` | `--dgemm-config` |
| `spackm.yaml` | `--spackm-config` |
| `dpackm.yaml` | `--dpackm-config` |

`ukrconfig/legacy/` keeps the old single-kernel files of the previous
generator; the current blisgen doesn't read them.

## The configurations

| config | ISA | gemm | default (doubles / singles) | packm |
|--------|-----|------|------------------------------|-------|
| `avx2/fma_bc_blocks` | AVX2 | FMA, broadcast operand (`gemm_fma_bc_blocks`); C across vectors by block insert/extract trees | 4x3v | vec |
| `avx512/fma_bc_blocks` | AVX-512 | as above, 32 registers | 8x3v | vec, trans (scatters) |
| `avx512/fma_bc_vindex` | AVX-512 | FMA, broadcast operand (`gemm_fma_bc_vindex`); C across vectors by gathers and scatters | 8x3v | vec, trans (scatters) |
| `neon/fma_bc_lanes` | NEON | FMA, broadcast operand (`gemm_fma_bc_lanes`); C across vectors by lane loads and stores | 8x3v | vec |
| `neon/fma_lane` | NEON | lane FMA, `fmla` by element (`gemm_fma_lane`): the broadcast operand loaded as whole vectors | 4vx4 | vec |
| `rvv/fma_vf` | RVV, LMUL 1 | vector-scalar FMA, `vfmacc.vf` (`gemm_fma_vf`): scalars in FP registers; C across vectors strided | 8x3v | vec, trans (strided) |
| `rvv/fma_vf_m2` | RVV, LMUL 2 | as above, 16 registers of two | 6x2v | vec, trans (strided) |
| `sve/fma_bc_vindex` | SVE | FMA, broadcast operand (`gemm_fma_bc_vindex`); C across vectors by gathers and scatters | 8x3v | vec, trans (scatters) |
| `sve/fma_blocklane` | SVE | block-lane FMA, scalars broadcast by 128-bit block (`gemm_fma_blocklane_vindex`) | 2vx8 | vec, trans (scatters) |
| `sme/fopa_bc_vindex` | SME | outer products into tiles (`gemm_fopa_bc_vindex`), the epilogue slice by slice | 2vx4v / 2vx2v | vec, trans (scatters) |
| `smesve/fopa_fma_split` | SME | the microtile split along m: outer products for the first part, streaming FMAs for the rest, sized by `split-ratios: 1..2:1..3` | 2vx4v+2x4v / 2vx2v+2x2v | vec, trans (scatters) |

Every gemm file has two families where the ISA has two orientations: `vn`
(vectors along n, A broadcast) and `vm` (vectors along m, B broadcast). `vm`
takes column-major C (its vectors run down C's columns). `vn` branches on
C's storage inside the kernel (`c-storage: [row, any]`): one k loop, an
epilogue per storage and alpha/beta case, the branch picked by C's strides
- row-major C (`cs_c == 1`) with plain vector loads and stores, any other
through C's accesses across vectors (gathers, strided, lanes) - so BLIS
copies C through a temporary tile only for edge cases
(`GEMM_UKR_SETUP_CT_ANY`). The block-tree configurations branch on row- and
column-major C (`[row, col]`, `GEMM_UKR_SETUP_CT_AMBI`): an any-storage
branch's strided rows would exceed x86's general registers. `c-storage`
takes `row`, `col` and `any`, the last the default branch
(`docs/CSTORAGE_PLAN.md`). Sizes are in the family's units: `8x3v` is
8 rows by 3 vectors, `2vx8` 2 vectors by 8 columns. Every size of a family
the registers hold is built; the others are reported in
`config/<name>/blisgen_report.txt`.

## Building BLIS

```sh
blisgen --sgemm-config ukrconfig/sve/fma_bc_vindex/sgemm.yaml \
        --dgemm-config ukrconfig/sve/fma_bc_vindex/dgemm.yaml \
        --spackm-config ukrconfig/sve/fma_bc_vindex/spackm.yaml \
        --dpackm-config ukrconfig/sve/fma_bc_vindex/dpackm.yaml \
        --from-dir <blis> --out-dir <blis-out> --author "<name>" \
        [--config-name ukrgen_sve] [--stack-buf-size BYTES] [--parent-config-name <config>] \
        [-j JOBS]   # kernels built at once, each in its own process (default: the CPUs)
cd <blis-out> && ./configure -t none ukrgen_sve && make -j && make testsuite-bin
```

Without `--from-dir`/`--from-git` blisgen writes the configuration's files
alone under `--out-dir`. The patched tree registers the configuration and
carries [PR 960](https://github.com/flame/blis/pull/960).

## At run time

- `BLIS_MR_D`, `BLIS_NR_D` (and `_S`), in elements, choose the gemm
  microkernel among those built - the vector length read at run time where
  sizes are in vectors. Unset, or a size not built: the family's default.
- `BLIS_MR_IN_MC_D`, `BLIS_NR_IN_NC_D`, `BLIS_KC_D` (PR 960) override the
  cache blocksizes, relative to the chosen kernel's MR and NR.
- A quick check: the testsuite with `input.general` reduced to data types
  `sd`, storage `rcg` and two sizes - one a multiple of the kernels' MR and
  NR, one not - and `input.operations` with `2` for the gemm microkernel and
  level-3 gemm.

## Writing a family

A gemm family names a tile operation preset (`preset:`, a shorthand from
`src/ukrgen/flow/presets/` or a YAML file of the same form) and the index
its vectors run along (`vectorize:`), or gives every `--<sto>-tileop` in
`params:`. Keys: `m`, `n` (sizes: `1..4`, lists), `default`, `unroll` (along
k), `loop-order`, `resolve-order`, `schedule`, and per component
`max-data-regs`, `max-preload`, `max-addr-regs`, `addr-pattern`. A split
family has `split:`, `parts:` (each with its preset and sizes along the
split index) and optionally `split-ratios:`. A packm family lists `cases:`
of `kind: vec` (cdim in vectors, A contiguous along it) and `kind: trans`
(cdim in elements, A contiguous along the panel), each with its sizes and
parameters. The examples' vec cases take P's leading dimension (`Y-layout:
[m:c, n:s]`): a kernel of a vectors then packs the vectors of any cdim from
a x VL to a x VL + 16 - a split's `2*VL + 2` - and the reference the rows
left (and a narrower panel's edge), so the gemms' MR and NR need no packm
case of their own. `docs/BLISGEN_PLAN.md` has the details of each.

## Tuning in the examples

- Unroll along k: 4 (the tail takes what's left of k, one at a time). An
  unroll is a ceiling: a size the registers can't hold so is built at half
  of it, down to 1, before it's skipped. Preload: on - an input's ring holds
  its tiles for the next iteration where the registers allow (`max-preload`
  limits it).
- SME: the epilogue's slice loops unrolled (the `unroll_loops` irmod) - 2 for
  doubles on one register set (all 8 tiles fused), 4 for singles on two.
- packm: `min-inflight: 8` - a case of m vectors (rows, for trans) is
  unrolled along the panel to keep at least 8 in flight: 2*VL four times,
  4*VL twice; the tail packs a column at a time.
- Scheduling: MRU on - straight-line chains pulled together (the cluster
  irmod), spread within a window of 12 under a register budget.
- RVV (in-order cores): `schedule` keeps a vector register's value 13
  instructions from what writes, reads or overwrites it
  (`RAW/WAW/WAR:data:vreg:::13`) and an address bump 3 from its uses
  (`RAW:address:greg:::3`); A and B each on two address registers taken in
  turn (`max-addr-regs: {A: 2, B: 2}`, `addr-pattern: rotate`), so the
  bumps spread. A count may be an expression of the kernel's sizes and
  element size (`max-addr-regs: {A: "m/4", B: "2n-2"}`) where the shape
  varies within one family - the same names as `addr-pattern`'s
  `blocked:` and `max-imm-offset`, except `R`, which a count itself
  decides. Specs are `dependency:register type:register tag:op:op:distance`,
  an empty field matching any.
- Out-of-order cores (AVX, NEON, SVE): `RAW:data:vreg:::4`.
- An issue model, for in-order cores: `--sched-cycle-slots "[N:]slot,..."`
  (family key `sched-cycle-slots` in `params`) - each slot a class or
  classes joined by `|`, one of them a cycle, N the most issued a cycle.
  Classes: `vl vs` vector loads and stores, `sl ss` scalar ones, `vf vi`
  vector FP and integer arithmetic, `vp` permutes, `t` tile operations,
  `f i` scalar FP and integer arithmetic, `addr` address arithmetic (else
  `i`), `br` branches. The SpacemiT K1 (X60): `"2:vl|vs|vf,sl,i"` - a vector
  load, store or FP operation, a scalar load beside it, two a cycle. The
  scheduler then places instructions cycle by cycle, the distances in
  cycles, and reports the cycles a block takes (`--print-schedule`).
- Address registers by default: one each for A and B (`rotate`), two for C
  (`phase`: loads on one, stores on the other); the specializer keeps up to
  four column pointers per base, one more walking the rest - a multiplier on
  the address registers. `column-pointers: {C: 0}` keeps none: the pattern's
  registers walk to C's columns, from the one nearest - by the column stride,
  and by a strided access's next vector (C at a general stride: VL times its
  row stride, an add of a register holding it), and lane by lane (NEON's vn
  C, across vectors), the registers rotating through the lanes - `phase+rotate` and
  `phase+blocked:N` split a component's registers between its phases (C's
  loads and stores, counted per case) and rotate within each share;
  `phase+blocked:n` gives each of C's vectors its own register.
- Strided A and B (gemmsup's shapes - `k:s`, a general stride `k:s, n:s`):
  their address registers walk forward along k by the stride, a register
  computed from whichever is fewest strides away (`blocked` registers, taken
  by k step, leapfrog: one add each); a general stride's row change one move,
  rs - (n - R) cs. Moves taking more than one instruction spelled out get a
  register of their own, computed once (`max-offset-registers`, a flow
  parameter - under `params:`: off by
  default - each takes a general register from address registers and column
  pointers, large microtiles then don't build; `auto` 4, 1 on x86): the most
  used, saving the most instructions, first - but none from a stride passed on the stack and loaded
  where the cases first need it (C's), which setup would have to load early.
- A family's `unroll` is a ceiling: a size that doesn't build at it is built
  at half of it, down to 1. A kernel records the unroll it got (`unroll`), and
  blisgen lists the kernels built below their family's (`unroll 2 of 4: vm
  bli_dgemm_..._4x4`, on the console and in `blisgen_report.txt`) - often a
  loop's register rings, which aren't renamed (NEON's lane kernels).
- AVX2 and AVX-512 packm: `kind: gather` cases - A row-major (lda 1), its
  rows gathered into vectors along cdim - beside the vec cases.

## Where kernels start: `align`

A family key, `align: "64:8"`, places each of the family's kernels 8 bytes
past a 64-byte boundary (`"64"` alone: on one) - blisgen writes `.balign`
and `.space` before the kernel, so the placement survives linking.
`blisgen --align 64:8` does it for every family without its own key. On a
core sensitive to where code lies (the K1), `ukropt-sweep --align` measures
which placement a kernel prefers.

`loop-align: 8` (a flow parameter, under `params`) puts each loop's head on
an 8-byte boundary: `.balign` before the loop's label, its padding nops run
once by the code falling into the loop (RISC-V's linker settles the padding
when it relaxes, so the boundary holds in the linked library).
`blisgen --loop-align 8` sets it for every family without its own;
`--ukr-align` is the kernels' placement above (`--align` its old name).

## What an instruction costs: hooks

A family's `params` can name hooks (docs/GENERATOR.md): scripts run around
the flow's stages. `examples/hooks/ablate.py` takes a kind of instruction
out of the kernel's k loop - the kernel computes nonsense then, but its
cycles show what that kind costs:

```yaml
params:
  hooks: ["after schedule examples/hooks/ablate.py drop what=vload"]
```

As a key of an `ukropt-sweep` grid (`hooks: [null, [...], [...]]`), one
sweep measures a kernel as is and without each kind - ukropt's
`examples/grid-ablate.yaml`, run from this checkout (the scripts' paths are
relative to it).
