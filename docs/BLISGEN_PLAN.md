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
| 2 | gemm wrappers (BLIS signature, edge-case macros) and the kernel table | done: `injectors/blis/cgen.py`, `tests/injectors/test_cgen.py` |
| 3 | Context initialization: run-time kernel choice from `BLIS_{MR,NR}_{S,D}`, default and fallback; cache blocksize defaults | done: `cgen.cntx_init`, `family_header`, `generate.py`; `--family-config`, `--stack-buf-size` |
| 3b | Epilogue STOs interleaved tile by tile, so C streams through a ring: the default 8x3v (24 AB accumulators) needs it | next |
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
- Step 2: a wrapper per kernel has BLIS's gemm microkernel signature, reads
  MR and NR (the vector length at run time where they're vectors), and
  brackets the assembly call with `GEMM_UKR_SETUP_CT`/`GEMM_UKR_FLUSH_CT`
  in the kernel's C orientation - partial tiles, the other orientation and
  general strides go through BLIS's temporary tile. BLIS's arguments map onto
  the kernel's parameters by name; C's stride in bytes. A table per data type
  lists the kernels as (count, vectors) for MR and NR and chooses by MR x NR
  in elements, falling back to the family's default size. Tested through a
  stub of blis.h (`tests/injectors/blis_stub.h`: BLIS's types and the
  edge-case macros as BLIS defines them): NEON and SVE wrappers exact on
  full and partial tiles in all three storages; the chooser exact and
  falling back.
- To do with step 3: the stack temporary tile is `BLIS_STACK_BUF_MAX_SIZE`
  bytes; long vectors need more (8x3v doubles at 2048-bit SVE: 6 KiB) - the
  configuration should set it from the largest kernel at the longest vector
  length it supports.
- asmgen's `get_simd_size()` on RVV measures one ungrouped register; with
  LMUL above 1 a kernel's vector is a group - the function should take the
  grouping into account (asmgen's state). Families use LMUL 1 until then.

## Step 3 design (next)

`config/<config>/bli_cntx_init_<config>.c`, generated:

```c
void bli_cntx_init_<config>( cntx_t* cntx )
{
	blksz_t blkszs[ BLIS_NUM_BLKSZS ];
	bli_cntx_init_<config>_ref( cntx );
	// BLIS_MR_<dt> x BLIS_NR_<dt> where such a kernel was made, else the default
	const ukrgen_gemm_entry* s = ukrgen_sgemm_choose( bli_env_get_var( "BLIS_MR_S", 0 ),
	                                                  bli_env_get_var( "BLIS_NR_S", 0 ) );
	const ukrgen_gemm_entry* d = ukrgen_dgemm_choose( ... "BLIS_MR_D", "BLIS_NR_D" ... );
	bli_cntx_set_ukrs( cntx, BLIS_GEMM_UKR, BLIS_FLOAT, s->ukr,
	                         BLIS_GEMM_UKR, BLIS_DOUBLE, d->ukr, BLIS_VA_END );
	bli_cntx_set_ukr_prefs( cntx, BLIS_GEMM_UKR_ROW_PREF, BLIS_FLOAT, s->row_pref,
	                              BLIS_GEMM_UKR_ROW_PREF, BLIS_DOUBLE, d->row_pref, BLIS_VA_END );
	// MR, NR from the kernels; MC, NC as multiples of them and KC: the
	// configuration's defaults - BLIS_MR_IN_MC_<dt>, BLIS_NR_IN_NC_<dt>,
	// BLIS_KC_<dt> override them after this (PR 960, frame/base/bli_gks.c)
	bli_blksz_init_easy( &blkszs[ BLIS_MR ], mr_s, mr_d, -1, -1 ); ...
	bli_cntx_set_blkszs( cntx, BLIS_NC, ..., BLIS_NR, BLIS_KC, ..., BLIS_KR, BLIS_MC, ..., BLIS_MR,
	                     BLIS_NR, ..., BLIS_NR, BLIS_MR, ..., BLIS_MR, BLIS_VA_END );
}
```

- The old `cntx_set_blocksizes` template reads `BLIS_MR_IN_MC_*`, `BLIS_NR_IN_NC_*` and
  `BLIS_KC_*` itself: gone, PR 960 does that for every configuration.
- MR x NR pairs like 8 x 24 break BLIS's MC-mod-NR / NC-mod-MR checks:
  `bli_family_<config>.h` defines `BLIS_RELAX_MCNR_NCMR_CONSTRAINTS`.
- `bli_family_<config>.h` sets `BLIS_STACK_BUF_MAX_SIZE` from the largest kernel
  (MR x NR x element size) at the longest vector length the ISA allows (SVE/SME
  2048 bits; RVV: a configuration parameter).
- Cache blocksize defaults (`mr-in-mc`, `nr-in-nc`, `kc` per data type) come from the
  configuration YAML, defaulting to the old templates' 16, 200, 256.
- Tested without BLIS first: the generated file compiled against a stub recording
  `bli_cntx_set_*` calls, with `BLIS_MR_*`/`BLIS_NR_*` set, unset and absent sizes.
- Step 3: `cgen.cntx_init` writes the context initialization - the reference's
  first, then per data type with kernels the one `BLIS_MR_<dt>` x
  `BLIS_NR_<dt>` names (default where unset or not made), registered with its
  orientation; MR/NR from it, MC/NC as multiples of them and KC from the
  configuration's `blocksizes` (defaults 16, 200, 256), PR 960 overriding
  them afterwards; a data type without kernels keeps the reference's kernel
  and blocksizes. Tested against a stub recording the `bli_cntx_set_*` calls
  (`tests/injectors/cntx_stub.h`) under qemu: unset (default), an existing
  size, an absent size (default). `bli_family_<config>.h` defines
  `BLIS_STACK_BUF_MAX_SIZE` and `BLIS_RELAX_MCNR_NCMR_CONSTRAINTS` (nearly
  every configuration does). The stack size is a parameter: `--stack-buf-size`
  (blisgen), `stack-buf-size` (YAML), else the largest kernel's tile at the
  ISA's longest vector (SVE/SME/RVV: 2048 bits), at least 2048.
- `generate.py` writes a configuration's files under `--out-dir`
  (`blisgen --family-config FILE --out-dir DIR --author NAME`): the kernels'
  `.S`, their wrappers, the context initialization, the family header, a
  report of the sizes skipped. The old path's imports (old patcher, old flow -
  broken with today's asmgen: `asmgen.asmblocks.operations` is gone) are
  loaded only on that path; its per-data-type configurations and BLIS source
  are required only there.
- Found: gemm's epilogue emits STO after STO over all tiles, so C is held in
  a register per tile beside AB's accumulators: 2vx8 (16 + 16 of 32) is
  skipped, and the default 8x3v (24 AB accumulators) can't build. Step 3b:
  the builder interleaves a block's STOs tile by tile where their tilings
  line up - scale, update and store one tile before the next - so C needs a
  ring of a few registers, as hand-written kernels do.
