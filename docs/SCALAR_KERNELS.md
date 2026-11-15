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
3. **The register type came from the untransformed operand.** `deduce_operand_rtype`
   is called with `solution_step.hw_ast`, so a `SCALAR_REDUCE`d operand is
   typed `VEC` - the shared hardware AST says `(i,)` whatever the instruction
   is - and every resolution then narrowed the compute signatures to `VEC`
   operands, so no scalar signature could ever be chosen.

## The decisions

1. **A scalar-reduced operand's register type is the transformed operand's**
   (`resolve_ast_solution` deduces from `logical_ast`). 0 dims -> `FP`/`GP`.
   The consequence is that `SCALAR_REDUCE` keys are looked up under `FP`, so
   the resolutions in `scalar_reduce.py` register for each rtype instead of
   `VEC` only. Measured on every ISA's candidate sets, before and after: gemm
   identical for neon, sve, sme, avx256 and avx512; rvv's gemm grows
   1120 -> 1336, additions only, no encoding removed.
2. **`scalar_direct`**, the VF-free twin of `use_scalar`: an IN step loading
   `orig_ref()` at `rgt.FP`, an OUT step storing from it, no operation
   modifiers. It is the resolution a scalar instruction needs and the one a
   vector instruction with a scalar form gains a duplicate of.
3. **A resident resolution for `SCALAR_REDUCE`**, in the registry's built-in
   loop beside the `{}`/`{NONE}` ones: a value already in a register moves
   nothing, and with the rtype rule above the key carries `FP`.
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

## Phases

| # | change | gated by | state |
|---|---|---|---|
| 1 | asmgen: drop `jvzero` (base, neon, sve, avx, rvv, the test table, `test_rvv071`) | asmgen suite, golden entries removed | done |
| 2 | asmgen: `riscv64` concrete (is_vla, sizes, constructors, cpuinfo, flags), the four members wired | asmgen suite, `test_asm_implemented`'s `riscv64` entry | done |
| 3 | asmgen: FP `fma`/`mul`/`add` in `riscv64/optransform/` + `tests/optransform/riscv64/` | asmgen suite | done |
| 4 | ukrgen: `scalar_direct` and the resident `SCALAR_REDUCE` resolution | full suite, goldens all `same` (should be inert) | todo |
| 5 | ukrgen: rtype from the transformed operand, `scalar_reduce.py` per-rtype | full suite, golden `diff`, qemu on the `fma_vf` kernels | todo |
| 6 | ukrgen: `isa_map` entry, `gemm_fma_scalar` preset, `ukrconfig/riscv64/{dgemm,sgemm}.yaml` | kernels build, qemu correctness against a reference | todo |

Steps 1-3 are in asmgen; 4-6 are ukrgen's and not started. With 1-3 in, the
real `riscv64()` generator drives the measured kernel end to end: the flow
emits it, it assembles with `-march=rv64gc`, and the five alpha/beta cases pass
under qemu - so nothing further is missing on the generator's side.

## The reference config

`blocksizes {mr-in-mc: 1, nr-in-nc: 1, kc: ...}`, one family, `m: 1`,
`n: 1`, `k: 1` (one element of k per operation, the k loop the count), no
addressing or schedule tuning, and `dtypes` FP64/FP32 only - F+D. The preset
names the candidates the flow already offers:

    mm:        fma(A.FP:scalar_direct, B.FP:scalar_direct, AB.FP){m=1, n=1, k*=1}
    betascale: mul(C.FP:scalar_direct, beta.FP:scalar_direct, C.FP){m=1, n=1}
    alphascale:fma(AB.FP, alpha.FP:scalar_direct, C.FP){m=1, n=1}
    store:     C.FP:direct
    alphamul:  mul(AB.FP, alpha.FP:scalar_direct, C.FP){m=1, n=1}
    add:       add(AB.FP, C.FP:scalar_direct, C.FP){m=1, n=1}
    alphaadd:  fma(AB.FP, alpha.FP:scalar_direct, C.FP:scalar_direct){m=1, n=1}
    betaadd:   fma(C.FP:scalar_direct, beta.FP:scalar_direct, AB.FP){m=1, n=1}
    store_ab:  AB.FP:direct

The preset's variants have no vector to orient around, so `gemm_fma_scalar`
is a single variant fixing every extent to 1 - it cannot use the `V`/`S`
operand axes the vector presets have.

## Open

- **packm**: the `pack` requirement is `MOVE(Y[m,n], X[m,n])` (kappa 1) or
  `MOVE(Y, MUL(X, kappa))`, so a scalar packm is `fld` -> (`fmul.d`) -> `fsd`
  one element at a time, `m` = the cdim extents (1..16 elements per
  microkernel), `n` = 1 with the panel the loop. The "stride or immediate
  offset" variants are the layout parameter (`X-layout: [m:c, n:s]` against
  `[m:s, n:c]`), which the specializer already turns into an immediate offset
  or a register bump. blisgen's packm families carry case kinds (vec, gather,
  trans) that index a dispatch, and a reference packm has no `vec` case: the
  config needs a case shape blisgen accepts, or packing stays BLIS's.
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
