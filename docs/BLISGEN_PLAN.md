# blisgen: plan and progress

Generating a BLIS configuration (`ukrgen_<isa>`) from kernel *families*
instead of one fixed-size kernel per YAML file. This document is the plan and
is updated as the work lands; each step names its status.

## Goals (stage 1)

- `{s,d}gemm` and `{s,d}packm` for one ISA per configuration.
- A **family** configures how kernels are built - the implementation choices
  (`--mm-to`, `--store-to`, ...), the register and preload limits, scheduling
  - and blisgen generates **every microtile size** (mr x nr) those choices
  can build on the ISA. Sizes that don't fit are skipped, with the reason.
- The microkernel is chosen **at run time**: `BLIS_MR_S`, `BLIS_NR_S`,
  `BLIS_MR_D`, `BLIS_NR_D` (in elements, as BLIS's MR/NR are) select the
  kernel whose register blocksizes match. Unset, or no kernel of that size:
  the family's default (8x3v for FMA ISAs, 2vx2v for outer products).
- Cache blocksizes (MC, NC, KC) come from the configuration's defaults and
  [PR 960](https://github.com/flame/blis/pull/960)'s environment overrides
  (`BLIS_MR_IN_MC_<dt>`, `BLIS_NR_IN_NC_<dt>`, `BLIS_KC_<dt>` and `_MAX`),
  which blisgen patches into BLIS. The blocksize selection in the old
  templates' context initialization goes. PR 960 applies its overrides after
  the context is initialized, so they are relative to the selected kernel's
  MR and NR.
- `packm` families name the implementation choices and the cases to
  accelerate - `cdim = n*VL` for n in 1..8 (vectorized along cdim),
  `cdim = 1..16` (transposed: vectorized along the panel's length) - and
  blisgen generates a C dispatch tree over them, falling back to the
  reference packm, as `kernels/rviv/1m/dpackm_rviv.c` on the x60 branch does
  by hand.

## Design

### Family configuration (YAML)

```yaml
isa: sve
config-name: ukrgen_sve        # the BLIS configuration made
gemm:
  - family: fma_bcast_b        # a name for the kernels' symbols
    dtypes: [FP32, FP64]
    params:                    # ukrgen parameters for every size
      mm-to: ["fma(A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]
      store-to: ["C.VEC:direct"]
      ...                      # preload, data registers, irmods, schedule
    m: 1..4                    # the sizes tried: m in vectors here
    n: 1..16
    default: {FP32: 2vx8, FP64: 2vx8}
packm:
  - family: vec_cdim
    dtypes: [FP32, FP64]
    params: {...}
    cases: [{cdim: "n*VL", n: 1..8}, {cdim: "1..16", transposed: true}]
```

### Generation

1. For each family, data type and size: one run of the full ukrgen flow
   (setup ... emit, pre-specialization irmods, scheduling), as the command
   line runs it. A size the ISA can't build (registers, tiles) is recorded as
   skipped with the flow's reason.
2. Each kernel's metadata: its symbol, mr and nr as `count` or `count*VL`
   (from the microtile's extents), its parameters in order (k, A, B, C,
   alpha, beta, C's stride, ...), the C layout it stores (column- or
   row-major).
3. Output per configuration:
   - `kernels/ukrgen_<isa>/3/*.S`: the assembly kernels;
   - `kernels/ukrgen_<isa>/3/bli_gemm_ukrgen_<isa>.c`: a BLIS-signature
     wrapper per kernel - BLIS's edge-case macros (`GEMM_UKR_SETUP_CT`,
     `GEMM_UKR_FLUSH_CT`) handling partial tiles and storage the kernel
     doesn't take, mapping BLIS's arguments onto the kernel's parameters;
   - a kernel table: per data type, (mr, nr) as functions of the vector
     length, the wrapper, the row/column preference;
   - `config/ukrgen_<isa>/bli_cntx_init_ukrgen_<isa>.c`: reads the vector
     length, `BLIS_MR_<dt>`/`BLIS_NR_<dt>`, picks the kernel (default when
     unset or absent), registers it with its MR/NR and the cache blocksize
     defaults;
   - packm: assembly per case and the C dispatch tree.
4. BLIS patching: configuration directories, registry (`config_registry`,
   `bli_arch`), PR 960 into `frame/base/bli_gks.c`, `inherit` of kernels
   from an existing configuration kept.

### Validation

- Each family's kernels against a reference (the existing harnesses).
- BLIS built with the generated configuration - natively for AVX2/AVX-512,
  cross-compiled and under qemu for SVE, SME and RVV - and BLIS's testsuite
  (gemm, packm through gemm), with several `BLIS_MR_*`/`BLIS_NR_*` choices
  and with absent sizes (fallback).

## Steps

| # | Step | Status |
|---|------|--------|
| 1 | Family configuration: loading, size enumeration, a flow run per size; kernel metadata (symbol, mr/nr, parameters, C layout) | done for gemm: `injectors/blis/families.py`, `tests/injectors/test_families.py` |
| 2 | gemm wrappers (BLIS signature, edge-case macros) and the kernel table | next |
| 3 | Context initialization: run-time kernel choice from `BLIS_{MR,NR}_{S,D}`, default and fallback; cache blocksize defaults | |
| 4 | BLIS patching: configuration and kernel directories, registry, PR 960, `inherit` | |
| 5 | BLIS build and testsuite: x86 natively, SVE/RVV under qemu | |
| 6 | packm families: cases, generated dispatch tree, reference fallback | |
| 7 | packm in the BLIS configuration; testsuite again | |
| 8 | Old patcher and templates retired (`clitools/blisgen.py` on the new path) | |

## Notes from the work

- Step 1: a gemm family's `params` carry every gemm choice - `mm-to` into AB,
  `betascale-to`, `alphascale-to`, `store-to` and the special cases'
  (`alphamul-to`, `add-to`, `alphaadd-to`, `betaadd-to`, `store_ab-to`) - and
  BLIS's packed panels as layouts (`A: m:c k:p`, `B: n:c k:p`), so a kernel's
  parameters are `k, A, B, C, alpha, beta` and C's stride. `k` (the unroll
  along k) defaults to 1. On fixed-width ISAs mr/nr come out as numbers (NEON
  doubles: 2 per vector), on VLA ISAs as multiples of VL (`2*VL`, symbol
  `2v`). A size that doesn't fit is skipped with the flow's first line of
  reason ("... vector registers ...").
