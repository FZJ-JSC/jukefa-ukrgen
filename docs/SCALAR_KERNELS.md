# Scalar microkernels: RISC-V with F+D

A microkernel whose every operand is a single element and whose microtile is
1x1: the reference kernel. `ukrconfig/riscv64` should build dgemm and sgemm
for rv64imafdc, so a scalar-only target gets a complete gemm, and the vector
families get a kernel to compare against that no vector choice can hide
behind.

Everything below was measured by driving the flow, not read off the code.
Where a claim rests on a probe, the probe is named.

## The flow already builds one

Driven with a stand-in generator that offers only FP-register `fma`/`mul`/`add`
(plus the `riscv64` members the emitter needs), the pipeline
`solve -> dimension -> sto -> model -> irmods -> isa_specialize -> loops ->
addresses -> schedule -> emit` produced a 102-instruction 1x1 dgemm kernel.
As a standalone `.S` it assembles with `-march=rv64gc`, and under
`qemu-riscv64` it computes `alpha*A.B + beta*C` in all five alpha/beta cases:

    .ukr1_loop%=:
        add a0,a0,-1
        fmadd.d f0,f1,f2,f0
        fld f1, 0(a1)                 # A's next element
        fld f2, 0(a2)                 # B's next element
        add a1,a1,8
        add a2,a2,8
        bne a0,zero,.ukr1_loop%=

seven instructions and 2 flops a k step, the loop preloaded as any vector
kernel's is. What carries a scalar, and the mechanism that does it:

| mechanism | where | what it does for a scalar |
|---|---|---|
| `SCALAR_REDUCE` | `matching/math.py:400` | one element of an operand, whatever its rank |
| decimated requirement | `generate_variants` (`math.py:644`) | drops the reduction index, `A[m,k] -> A[m]` |
| empty index binding | `bind_indices` (`math.py:217`) | a 0-dim hardware operand binds no index: every requirement index keeps extent 1 |
| rtype of a scalar | `deduce_operand_rtype` (`dm_solver.py:263`) | 0 dims -> `FP` for a float, `GP` for an integer |
| extents | `index_extents` (`tiles.py:90`) | skips scalar-reduced operands and non-`VEC`/`TILE` shapes: no extent, so `--m 1 --n 1 --k 1` |
| operand tile | `infer_hw_tile` (`support/op.py:79`) | `FP`/`GP`/`MASK` is the 1x1 tile |
| memory | `direct_provider` (`dm_resolutions/direct.py:40`) | a direct load/store for *every* `rgt`, `FP` included; `riscv64_opmem` has `fld`/`fsd` with a ±2048 immediate |
| registers | `emitters/allocation.py:92` | `FP` values from the tracker's `freg` file - its own file on RISC-V |
| liveness, copies | `liveness.DATA`, `copyprop` `renames` | `FP` already among the data register types |
| scheduling | `schedulers/issue.py:117` | classes `sl`, `ss`, `f` for scalar loads, stores, FP arithmetic |
| tails, masks, state | base `isa_setup` | `predication.NONE`, no setup: nothing to set up, no `vsetvli` |

Nothing in the address side needed changing: a scalar's accesses are one
element, its store has no axis (`vector_axis` -> `None` -> contiguous), and
the walker bumps by `adt_size` bytes.

## What was missing

### asmgen: `riscv64` was not a generator

    TypeError: Can't instantiate abstract class riscv64 without an
    implementation for abstract methods 'is_vla', 'jvzero', 'max_tregs',
    'max_vregs', 'simd_size', 'supportedby_cpuinfo', 'treg', 'vreg'

and `riscv64.__init__` wired only `load`, `store`, `prefetch`: `move`, `set`,
`sub` and `shift` existed as classes (`opmove/`, `opset/`, `optransform/`) but
were never assigned, so `asmops.mov`, `lsc_zero` and `kiterkleft` (which needs
`self.shift`) could not run. `fma`/`mul`/`add` for FP did not exist at all.

Both are done, in asmgen:

- `jvzero` is gone from `noarch.asmgen`, its four backends and the test table
  (decision 5 below) - it was the last abstract method in the way.
- `riscv64` is concrete in `asmblocks/riscv64/gen.py`: `is_vla` false,
  `simd_size` 1, `max_vregs`/`max_tregs` 0, `vreg`/`treg` raising,
  `supportedby_cpuinfo`, `compiler_flags` (`-march=rv64gc`, `_zba` with the
  feature), `FEATURES`/`MARCH_EXTENSIONS`, and `sub`, `shift`, `set`, `move`
  assigned beside `load`/`store`/`prefetch`.
- `asmblocks/riscv64/optransform/` gains the arithmetic: `riscv64_opd3_base`
  (`base.py`), `make_riscv64_opd3_signatures` (`signatures.py`),
  `riscv64_fadd`/`riscv64_fmul`/`riscv64_fma` (`fadd.py`, `fmul.py`,
  `fma.py`, all FP64/FP32, the FMA as `fmadd.d rd,rs1,rs2,rd` and `fnmsub` for
  NP), and the general-register operations moved out of the package's
  `__init__.py` into `scalar.py`, which each of them names as its
  `scalar_class`.

### ukrgen: three gaps in the solver

1. **No resolution says "the operation takes this operand as an FP scalar,
   entered directly."** The only one that does is `use_scalar`
   (`dm_resolutions/scalar_reduce.py:59`) and it requires the `VF` operand
   modifier, RVV's vector-scalar form. With FP-only compute signatures,
   `find_hw_implementations` returned **0 chains** for gemm's `mm`.
2. **A register-resident scalar-reduced operand has no resolution.** The
   registry's built-in "resident" entry (`data_move.py:279`) covers
   `tfs` `{}` and `{NONE}` only. The `mul;add` chain resolved one candidate at
   its first step and **0** at its second - the accumulator.
3. **The lookup considered one register type.** `deduce_operand_rtype` reads
   the hardware operand's shape, so a `SCALAR_REDUCE`d operand is typed `VEC`
   - which is right for the operand's shape and wrong as the *only* type the
   instruction might take it in: the key decided which resolutions were even
   seen, and only the `VEC` ones were.

## The decisions

1. **A scalar-reduced operand is looked up under every register type an
   element arrives in.** `SCALAR_REDUCE` says the requirement's operand is one
   element; it says nothing about the register the instruction takes it in - a
   scalar instruction takes an FP register, a vector-scalar form takes an FP
   register, a broadcast or a lane access takes a vector register and uses one
   element of it. So `deduce_operand_rtype` keeps reading the *untransformed*
   hardware operand (VEC for one index, TILE for two), the keys such an
   operand's resolutions are looked up under are `key_rtypes()`'s - its own,
   plus `ELEMENT_RTYPES`, VEC and FP - and every resolution is filed under the
   type its own *steps* take the operand in (`get_op_rtype_req`):
   `use_scalar` and `scalar_direct` under FP, the broadcasts and the lane
   accesses under VEC. Measured on every ISA: no encoding disappears anywhere,
   gemm unchanged on Neon, SVE, SME, AVX2 and AVX512; RVV's gemm +12 and
   `pack` +1 on every generator - the entries the previous step registered,
   now reachable.
2. **`scalar_direct`**, the VF-free twin of `use_scalar`: an IN step loading
   `orig_ref()` at `rgt.FP`, an OUT step storing from it, no operation
   modifiers, and it forbids what a plain register operand is not
   (`NOT_A_PLAIN_REGISTER`: `VF`, `BCAST`, the lane and block selections with
   their shifts and rotations, `ROW`, `COL`). Its steps take an FP register, so
   by the filing rule above it is an `FP`-keyed entry; the `VEC` key's entries
   for a one-element operand are the broadcasts and the lane accesses, which
   read one element out of a register they load whole, and this is neither.
3. **A resident resolution for `SCALAR_REDUCE` under `FP`**, beside the
   registry's built-in `{}`/`{NONE}` ones: a value already in a floating-point
   register moves nothing. It has no steps, so its key's type *is* the
   statement - and no `VEC`-keyed twin is registered: that would say a whole
   vector register is one element of the requirement, a family of 1-element
   microtiles built from vector instructions (Neon's gemm 704 -> 2332
   candidates; trap below).
4. **`simd_size` is 1 and `max_vregs`/`max_tregs` are 0, not raising.**
   Nothing in ukrgen reads `simd_size` as a VLA test - `is_vla` is a separate
   query - and every use is `// adt_size` (lanes) or `* simd_size` (bytes).
   Two places would be wrong rather than loud if a scalar kernel ever reached
   them: `asmops.add_vectors` (`offset * simd_size` bytes) and
   `irmod/lsc/ldinc` (a bump by `simd_size`). Both need a `VEC` value or a
   `VOFFSET` form, and `max_vregs() == 0` means no vector register can be
   allocated, so they are structurally unreachable. `lanefuse` is the one
   irmod whose guard is `is_vla` alone: on `riscv64` it stays applicable and
   is inert (no `ILANE` load can be built); a `if not ctx.gen.max_vregs():`
   in `unmet_requirements` would say so instead of relying on absence.
5. **`jvzero` is removed.** It was dead - no reference in ukrgen's `src`,
   `tests` or `legacy`, only its own unit test in asmgen and a
   required-method table entry - and it was the last abstract method blocking
   `riscv64`'s instantiation (it also needs `vreg(0)` to be called, which a
   scalar generator cannot do). If a compare over any register needs to exist
   later, it belongs as `cmp(regs) -> cb`, not as a per-type method.
6. **`supportedby_cpuinfo`** takes the string after `rv64` up to the first
   `_` and asks for `g` or `d` in it; FP16 would ask for `zfh` among the
   `_`-separated extensions. `rv64imac` and `rv64imaf` (no D) are rejected.

## Traps, each with the failure that proved it

- **An FP arithmetic op must also serve general registers.** `gen.fma`,
  `gen.mul` and `gen.add` are one object per generator, and ukrgen calls
  `gen.add` for *general register* immediates too (`asmops.add_imm_from`).
  An op offering only FP signatures dies with `Invalid configuration for
  <op> ... dts: adreg:UINT64, cdreg:UINT64, reg types: adreg:riscv64_greg`.
  The aarch64 base's shape is what works: `all_signatures()` returns the
  FP ones *and* `scalar_class`'s, and `implementation()` forwards to the
  scalar op when `cdreg` is a `greg_base`.
- **Forward the scalar call with `scalar_operands(kwargs)`, not `**kwargs`.**
  `execute()`'s bookkeeping keys are in the kwargs: passing them on gives
  `TypeError: execute() got multiple values for keyword argument 'dts'`.
- **`_gate_features()` belongs at the end of `__init__`.** Without it
  `enabled_features` stays `None` on the operations, and `set_features([])`
  - which `make_generator` always calls - hides the ZBA `shNadd` addressing
  forms from everything but the run that sets them.
- **A 0-capacity register type is fine, a missing constructor is not.** The
  tracker takes `('vreg', 0)`: `available('vreg') == 0`, `capacity == 0`,
  the pool `{'vreg'}` separate from `{'freg'}`, and
  `tests/test_reg_available.py`'s invariant iterates `range(0)`, so it never
  calls the constructor a scalar generator raises from.
- **The candidate sets, not the chosen encodings, are what a new resolution
  moves.** Presets pick by exact membership (`next(o for o in options if o in
  candidates[sto])`) and no ukrconfig passes a candidate by index, so an added
  resolution cannot change an existing kernel's choice - but
  `--list-tileop-candidates` output changes and any future "first candidate"
  rule would see it.
- **A resolution that requires nothing of the modifiers matches every form
  with a slot of its type.** `scalar_direct`'s step names an FP register, and
  with no requirement on the shape it matched RVV's `vf` signatures - whose
  scalar operand *is* an FP register, with `VF` on its shape - and offered 228
  candidates on RVV's gemm that are vector instructions, the VF forms reached
  without naming VF. Nothing false was said (the steps are the code) and no
  config chose one, but a candidate list is a claim about what an ISA can do.
  Forbidding `NOT_A_PLAIN_REGISTER` left +1 on every generator's `pack` copy
  and +12 on RVV, and nothing else changed anywhere.
- **A key's register type is what the instruction takes, not what the
  requirement has.** The first attempt at this step deduced the type from the
  transformed operand, which makes every `SCALAR_REDUCE` key `FP` - and 8 of
  the provider's 11 entries take a *vector* register (`bc_load`, `bc_lane`,
  `bc_lanes`, `bc_scalar`, `bc_block`, `use_lane`, `scalar_to_lane`,
  `lane_to_scalar`), so they were silently relabelled. It worked: a
  resolution's key type is never consulted when the resolution has steps, so
  only the no-step (resident) entry showed a difference, and the truth came
  out of the registry rather than the tests. The rule that holds is
  `get_op_rtype_req(steps)`, per resolution, with a one-element operand looked
  up under every type it can arrive in - and deducing the type from the
  transformations *without* the matching re-keying empties the registry for
  vector kernels outright (Neon's gemm 704 -> 8 candidates, RVV's `pack`
  92 -> 27). `tests/support/test_scalar_resolutions.py` asserts the filing
  rule resolution by resolution.
- **The type rule and the key it looks up are one change.** Taking the
  register type from the transformed operand without moving the provider's
  keys with it does not change what is chosen, it empties the registry for
  every vector kernel: Neon's gemm 704 -> 8 candidates, RVV's `pack` 92 -> 27,
  because the keys became `FP` and every resolution was still filed under
  `VEC`. Landing the two together is what makes the change a re-keying -
  five of the six generators' gemm sets come out identical.
- **A candidate's index is not a name.** `tests/stages/test_sto.py` picked its
  pack chain by `"0"`, the first candidate in sorted order; the scalar copy
  sorts before the vector one (`X.FP` < `X.VEC`), so the test began building a
  store from an FP register for a pack that left its result in a vector - and
  `check_part_chain` said so: "store reads Y from FP, but pack leaves it in
  VEC". Tests name an encoding; only a person reading
  `--list-tileop-candidates` should use the numbers.
- **The register type a key carries is the whole statement.** Registering the
  two new resolutions under `VEC` as well as `FP` does not add a duplicate of
  a vector resolution, it adds a *different claim*: that a vector register
  holding several elements is one element of the requirement. Measured, with
  them under both types: Neon's gemm 704 -> 2332 candidates, RVV's 1120 ->
  1540, SVE's 842 -> 1258, SME's 19454 -> 19870, the AVX2/512 ones +104 each,
  and every `pack` case +1 - a family of kernels whose accumulator is one
  element and whose store writes the whole register. Under `FP` alone every
  candidate set is **identical** (six generators, gemm and pack), because a
  scalar-reduced operand is still typed `VEC` today and nothing looks up an
  `FP` key. `tests/support/test_scalar_resolutions.py` pins both facts.
- **The emitted kernel is C-string fragments until something joins them.**
  `asmwrap` in file mode produces quoted, escaped lines; a probe that writes
  them straight into a `.S` gets `.text\n\t"` as a pseudo-op. `literal_eval`
  each line first.
- **A package's `__init__.py` is a module, and an operation module importing
  it is a circular import.** `riscv64_fadd` needs `riscv64_add`, which lived
  in `optransform/__init__.py`; `from ..optransform import riscv64_add` in
  `fadd.py` fails with `partially initialized module ... most likely due to a
  circular import` the moment `__init__` imports `fadd` back. The
  general-register operations moved to `optransform/scalar.py` (SVE's layout
  for the same reason) and each FP operation imports them from there.
- **`optransform`'s operands are annotated `data_reg`, and general registers
  are not one** (`freg_base`/`vreg_base`/`treg_base` derive from it,
  `greg_base` does not). Every scalar arithmetic call in the tree - asmops',
  and now `riscv64_opd3_base`'s - passes a `greg`, so the annotation is
  narrower than the API; widening it to `data_reg | greg_base` is a separate
  one-line change, not part of this one.

- **A family's `schedule:` is a key, not a parameter.** `key_params` maps the
  family's and each case's `schedule` to the `distances` stage parameter, so
  `schedule:` belongs at the family's or the case's level. Written inside
  `params:` it is a stage parameter no stage takes, and that is a *warning*, not
  an error ("no stage takes schedule"): the build succeeds, the kernels look
  scheduled, and no distance was ever applied. `sched-cycle-slots` is the other
  way round - it is already the stage parameter's name, so it goes inside
  `params:` where k1 puts it.

## Phases

| # | change | gated by | state |
|---|---|---|---|
| 1 | asmgen: drop `jvzero` (base, neon, sve, avx, rvv, the test table, `test_rvv071`) | asmgen suite, golden entries removed | done |
| 2 | asmgen: `riscv64` concrete (is_vla, sizes, constructors, cpuinfo, flags), the four members wired | asmgen suite, `test_asm_implemented`'s `riscv64` entry | done |
| 3 | asmgen: FP `fma`/`mul`/`add` in `riscv64/optransform/` + `tests/optransform/riscv64/` | asmgen suite | done |
| 4 | ukrgen: `scalar_direct` and the resident `SCALAR_REDUCE` resolution, both under `FP` | full suite, goldens all `same` (should be inert) - candidate sets identical on six generators, 21/21 goldens, 519 tests | done |
| 5 | ukrgen: a one-element operand looked up under every register type it arrives in, and the provider filed by its steps' type | full suite, golden `diff` - 21/21 `same`, 522 tests, no encoding removed anywhere, RVV +12, `pack` +1 | done |
| 6 | ukrgen: `isa_map` entry, `gemm_fma_scalar` preset, `ukrconfig/riscv64/{dgemm,sgemm}.yaml` | kernels build, qemu correctness - 8x3 and 3x8, FP32 and FP64, 16 emulated runs all correct; goldens gain four files, the other 21 `same` | done |
| 7 | ukrgen: `packm_scalar` preset, `ukrconfig/riscv64/{dpackm,spackm}.yaml`, one `kind: scalar` case, `min-inflight: 8` | cdim 1..8 built each, the panel loop unrolled to 8, 9, 10, 12 or 14 elements in flight; 80 emulated runs correct over n = 1, 3, 7, 8, 11 and both kappa branches; goldens gain two files | done |
| 8 | ukrgen: a dual-issue model and three distances on the reference configs | the scheduler reports its distances met in the k loop (27 cycles for 37 instructions) and the expected shortfall in the epilogue; a reordering with every count unchanged, and the emulated runs still correct | done |

Steps 1-8 are in. The reference configurations build, assemble and compute
correctly under qemu, gemm and packing, with a dual-issue model and distances;
what is left is the fallback question below and the BLIS-side check.

## The reference config

`ukrconfig/riscv64/{dgemm,sgemm}.yaml`, both data types only (F and D), one
preset and two families:

    blocksizes: {mr-in-mc: 8, nr-in-nc: 3, kc: 256}
    - family: mn   m: [8]  n: [3]   order: kmn   default: 8x3
    - family: nm   m: [3]  n: [8]   order: knm

One operation is one element, so `--m 8 --n 3` is an 8x3 microtile - 24 scalar
FMAs a k step, A's element loaded once and reused across the three columns
(`kmn`), 3 B elements beside it. Twenty-four accumulators and the rings fit the
32 FP registers, which is what makes 8x3 the largest tile this shape holds -
the same arithmetic that sizes the vector configurations' 8x3v. The `nm`
family is the transpose (3x8), the shape BLIS's other blocksize needs.

The golden set records each family at its **first** sizes, so `mn` lands as
`riscv64-{d,s}gemm-mn-8x3` and `nm` as `...-nm-3x8` without either being
nominated: nothing in the config decides what is recorded, and the two families
are what give the pair.

`gemm_fma_scalar` is one variant fixing both extents - there is no index for
vectors to run along, so it cannot use the `V`/`S` operand axes the vector
presets have - and its templates are the candidates the flow offers:

    mm:        fma(A.FP:scalar_direct, B.FP:scalar_direct, AB.FP){m=1, n=1, k*=1}
    betascale: mul(C.FP:scalar_direct, beta.FP:scalar_direct, C.FP){m=1, n=1}
    alphascale:fma(AB.FP, alpha.FP:scalar_direct, C.FP){m=1, n=1}
    store:     C.FP:direct
    alphamul:  mul(AB.FP, alpha.FP:scalar_direct, C.FP){m=1, n=1}
    add:       add(AB.FP, C.FP:scalar_direct, C.FP){m=1, n=1}
    alphaadd:  fma(AB.FP, alpha.FP:scalar_direct, C.FP:scalar_direct){m=1, n=1}
    betaadd:   fma(C.FP:scalar_direct, beta.FP:scalar_direct, AB.FP){m=1, n=1}
    store_ab:  AB.FP:direct

Measured: 875 instructions for 8x3 and 687 for 3x8, the same counts for FP32
and FP64 (the suffixes differ); both assemble with `-march=rv64gc` and are
correct under `qemu-riscv64` for k = 37 and four (alpha, beta) combinations
each - alpha=1/beta=0 (store AB), 1/1, 0/1 and 3/2, the last two exercising
`betascale` and the rest of the epilogue. They are in the golden set as
`riscv64-{d,s}gemm-{mn-8x3,nm-3x8}`; the other 21 kernels are unchanged by
their addition.

**A kernel of these configurations takes C's stride in bytes.** `cgen`'s
argument table multiplies: `"stride(C,n)" -> cs_c * (inc_t)sizeof(ctype)`, which
is why the emitted `add t0,t0,a6` has no shift. A driver that passes BLIS's
element count gets the columns packed `sizeof(ctype)` times too close and every
element past the first column wrong - the 1x1 probe kernel of step 5 hid this
because its C is one element.

## The reference packing config

`ukrconfig/riscv64/{dpackm,spackm}.yaml`, the `packm_scalar` preset, one case
and every cdim a reference `mr` or `nr` can be: `m: 1..8` - element counts, one
`fld` and one `fsd` (and an `fmul.d` for the scaled branch) per element. The
whole range rather than powers of two, because BLIS asks a packm for exactly
`cdim` rows and anything a case doesn't cover is the reference's: with a kernel
per cdim from 1 to 8, every panel a reference gemm of either orientation packs
goes in one pass. The
composition's own branch gives the two kernels BLIS needs from one program:
`kappa == 1` is the copy (`fld`/`fsd`), anything else the scaled pack
(`fld`/`fmul.d`/`fsd`), selected at run time by `feq.d` against 1.0.

        min-inflight: 8
        kind: scalar   m: 1..8
        X-layout: ['m:c', 'n:s']   Y-layout: ['m:c', 'n:s']
        sched-cycle-slots: "2:sl,f|i"
        dispatch: [scalar]

There is one case, not the vec/gather/trans three: with one element per operand
the source's layout decides only the *address form* (an immediate offset per
row inside the panel, or a stride bump between columns), never which form the
access takes - measured, the candidate encodings for `X-layout [m:c, n:s]` and
`[m:s, n:c]` are identical. No `mask` (cdim elements are cdim operations, so
there is no partial vector), no `lmul`, no `min-inflight` (nothing to keep in
flight).

`kind: scalar` is what makes it usable in a vector configuration too: cgen's
default dispatch ranks `vec`, `gather`, `trans` and then anything else, so the
same case drops in last as the fallback for the cdim the vector cases leave to
the reference. It sorts last because `rank.get(kind, 4)` has no entry for it,
and it is treated as an ordinary case - unmasked, not blockwise, no `stride(Y,n)`
requirement - because those are all keyed on the kind. Its `mr` is a fixed
element count, which `split_size`/`c_expr` already handle (AVX-512's fixed 16 is
the precedent).

`min-inflight: 8` unrolls the panel loop: `packm_one` sets `n` to
`ceil(8 / cdim)`, so the elements in flight - columns times rows - are at least
eight in every kernel, and the measured floating-point registers the copy loop
holds are 8, 8, 9, 8, 10, 12, 14 and 8 for cdim 1 to 8 (a whole-column unroll
can only overshoot: `ceil(8/5)` is 2 columns, ten elements). The loop splits
`n` by the unroll - `andi`/`srli` where it is a power of two, `remu`/`divu`
against a `li` constant where it isn't (cdim 3, unroll 3) - runs the whole
iterations, then the last one, then the remainder a column at a time: `.ukr1_loop`,
`.ukr1_last`, `.ukr1_tail`, and the same three again in the kappa-scaled case.

Measured: 212, 185, 194, 179, 212, 253, 294 and 129 instructions for cdim 1 to 8
(the same in FP32 and FP64) - up from 53..123 flat, because the body is the
unrolled one; the *iteration* is what got shorter. Assembled with
`-march=rv64gc` and correct under `qemu-riscv64` at lda 11 and ldp 19 for 1, 3,
7, 8 and 11 columns - every unroll from 8 down to 1 has a main loop, a last
iteration and a tail path exercised, and Y past both cdim and `n` stays
untouched: **80 runs**, both kappa branches. In the golden set as
`riscv64-{d,s}packm-pk-scalar`, all eight sizes in each file.

## Scheduling

The issue model's classes are decided from the operand shapes already:
`classify()` (`schedulers/issue.py`) reads `op.rtypes` and returns `vf` for a
transformation whose operands hold a VEC, `f` for one whose operands are FP,
`t` for a TILE, `i` otherwise, `vl`/`sl` for a load by the same test. So no
class is missing for a scalar kernel - `CLASSES` has had `f` ("scalar FP")
all along - and no new mechanism is needed: what was missing is a
configuration naming it. Measured on the 8x3 kernel with the model on:
`{f: 312, addr: 291, sl: 178, ss: 144, i: 25}`, against RVV's
`{vf: 6102, vl: 2288, vs: 2712, sl: 1890, addr: 5636, i: 349}` - the same
classification puts each in its own class.

The reference configurations carry a dual-issue model and three distances:

        sched-cycle-slots: "2:sl,f|i"      one memory port, one ALU/FP port
        schedule: [RAW:data:freg:ld:fma:3,   a load's value three later
                   RAW:data:freg:fma:fma:4,  an accumulator four later
                   RAW:address:greg:::2]     an address step before its access

`ss` falls back to `sl` and `addr` to `i` (`FALLBACK`), so stores share the
memory port and address arithmetic the ALU's - which is the model's point.

What the scheduler reports (`--print-schedule` prints it into the kernel, or
`list_scheduler.report`): the k loop, 37 operations, takes **27 cycles** with
`ld->fma` asked for 3 and **reached 5, none short**, `fma->fma` asked for 4 and
reached 37, `address` asked for 2 and reached 6. The epilogue's 47-operation
block asks 2 of an address dependence and reaches 1, 23 short - straight-line
code with a register budget, which is the documented expected shortfall rather
than an error. The emitted text is a **reordering**: 820 instructions either
way for 8x3 and 632 for 3x8, the loads hoisted so their values arrive before
their first use, 742 of the 820 lines in another position. Correctness after
the reorder: the same 16 emulated runs pass.


- **The scalar packing case as a vector configuration's fallback**: adding
  `kind: scalar` to e.g. `rvv/k1/dpackm.yaml` promises ukrgen code for the cdim
  ranges its vector cases leave to BLIS's reference (below the smallest case's
  `mr`, past a case's 16-row window, and where the `inca == 1`/`lda == 1` guards
  fail). Unmeasured - and the remainder *inside* a vector case's window stays
  the reference either way, because `overlap()`'s peers are that case's own
  kernels and not another case's.
- `--k` unroll > 1 and `subtail` are untested for scalars (the measured
  kernel is unroll 1).
- FP16 needs Zfh (`fadd.h`, `flh`), and `riscv64_opmem` already offers FP16
  loads ungated: gate both together if a `zfh` variant is wanted.
- BLIS injection: `c_simd_size_function` on a non-VLA generator returns
  `get_simd_size() { return 1; }` - the driver's vector-length arithmetic then
  measures in bytes, which is right for a scalar kernel but should be checked
  against blisgen's loop bounds.
- The flow probe that produced the numbers above lives in the scratch
  directory, not the tree. Once the generator is in, it belongs in `tools/`
  beside `sme_sweep.py`, with `--compare`.
