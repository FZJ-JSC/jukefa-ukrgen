# blisgen: plan and progress

Generating a BLIS configuration (`ukrgen_<isa>`) from kernel *families*
instead of one fixed-size kernel per YAML file. This document is the plan and
is updated as the work lands; each step names its status.

## Goals (stage 1)

- `{s,d}gemm` and `{s,d}packm` for one ISA per configuration.
- A **family** configures how kernels are built - the implementation choices
  (`--mm-tileop`, `--store-tileop`, ...), the register and preload limits, scheduling
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
# one file per data type and kernel type: --sgemm-config, --dgemm-config,
# --spackm-config, --dpackm-config (this one: --dgemm-config)
isa: sve
family: vn                     # a name for the kernels' symbols
m: [4, 8]                      # the sizes tried: m in elements here
n: 1..3                        # n in vectors
default: 8x3                   # the kernel when BLIS_MR_D/BLIS_NR_D name none made
blocksizes: {mr-in-mc: 16, nr-in-nc: 64, kc: 256}
params:                        # ukrgen parameters for every size
  mm-tileop: ["fma(A.VEC:bc_load, B.VEC:direct, AB.VEC){m=1, i=n, k*=1}"]
  ...                          # the epilogue's choices, layouts, preload, irmods
# several families: a list under families:
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
| 3b | Large tiles: C streamed through the epilogue (MRU renaming), register fitting by liveness | done: the default 8x3v builds |
| 4 | BLIS patching: configuration and kernel directories, registry, PR 960, `inherit` | done: `patch.py`, `clitools/blisgen.py` |
| 5 | BLIS build and testsuite: x86 natively, SVE/RVV under qemu | SVE done (gemm ukr + gemm, sd, rcg); x86, RVV (LMUL 1 and 2), NEON next |
| 6 | packm families: cases, generated dispatch tree, reference fallback | done: vec, trans (RVV strided stores, SVE scatters) |
| 7 | packm in the BLIS configuration; testsuite again | done for SVE (vec cases) |
| 8 | Old patcher and templates retired (`clitools/blisgen.py` on the new path) | |

## Notes from the work

- Step 1: a gemm family's `params` carry every gemm choice - `mm-tileop` into AB,
  `betascale-tileop`, `alphascale-tileop`, `store-tileop` and the special cases'
  (`alphamul-tileop`, `add-tileop`, `alphaadd-tileop`, `betaadd-tileop`, `store_ab-tileop`) - and
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
- Step 3b: 2vx8 and the default 8x3v were refused by the model's register
  fitting (0082), not by the hardware: it counted every written component as
  an accumulator, all tiles live - C in the epilogue too. The builder emits
  the epilogue STO after STO (C a model register per tile); MRU scheduling
  pulls each tile's dependent instructions together and renames C into the
  accumulators' registers as they are consumed - that works. The fitting now
  counts as all-live only what a loop accumulates (AB, in the loop and
  carried into the epilogue); a component written in straight-line code only
  (C) streams, with no registers kept for it; and since an input's physical
  registers stay its own to the end of the kernel, every block's inputs (A,
  B, alpha, beta) share what the most accumulators any block holds leave.
  Without --mru such a kernel runs out of registers in the emitter, which
  says to schedule. Families with large tiles set `mru: true`. SVE 8x3v (C
  row-major), NEON 8x3v, SVE 2vx8 exact through the wrapper harness.
- MRU scheduling is on by default (`--no-mru` turns it off): large tiles need
  it, the epilogue's C streamed into the accumulators' registers.
- Family files are per data type and kernel type (`--sgemm-config`,
  `--dgemm-config`, `--spackm-config`, `--dpackm-config`; packm in step 6);
  `configuration.from_files` checks their ISAs agree. The configuration's
  settings stay on the command line: `--config-name`, `--parent-config-name`
  (inherit), `--stack-buf-size`. `clitools/blisgen.py` is the new path only;
  the old one (old flow, broken with today's asmgen) is gone from it.
- Step 4: `patch.py` copies the BLIS tree to `--out-dir`, registers the
  configuration (the old templates' insertions; INSERT_GENTCONF anchored on
  its definition, which doesn't change between BLIS versions), writes the
  generated files, the kernel definitions, `make_defs.mk` and the kernels'
  prototypes (`GEMM_UKR_PROT`), and applies PR 960 (stored as
  `injectors/blis/patches/pr960-dynamic-blocksizes.diff`, from the fork's
  `dynamic-blocksizes` branch; BLIS master a8037cf is its base). The
  wrappers' `data` is `const auxinfo_t*`, as BLIS declares it.
- Step 5, SVE: BLIS master patched with an SVE configuration (8 / 4 rows x
  1..3 vectors, singles and doubles, 8x3v default), cross-built, the
  testsuite reduced: `gemm` microkernel and level-3 `gemm` only (2 in
  `input.operations`), data types `sd`, storage `rcg`, sizes 43 and 96 (96 a
  multiple of every MR and NR at both vector lengths, 43 tails). Under qemu,
  all pass: default at 256 bits (1920), `BLIS_MR_D=4 BLIS_NR_D=8
  BLIS_MR_S=8 BLIS_NR_S=8` (768; the testsuite reports MR s 8, d 4), 512
  bits (3648), an absent size falling back to the default (1920). A run takes
  about three minutes.
- LMUL: asmgen's `get_simd_size()` reads the vector size with the
  generator's LMUL already; each kernel now carries its generator's
  function and blisgen writes one vector-length function per distinct one,
  each kernel and table entry using its own - families may differ. An RVV
  kernel with LMUL 2 exact through the wrapper harness at VLEN 128 and 256.
- For a detailed run later (the old generator's failures): RVV 12x2vx4,
  2vx12x8, 2vx14x2, 2vx14x4, 2vx4x1, 3vx8x4 and LMUL 2 2vx7x4, 6x2vx4 failed
  BLIS operations beyond gemm (trmm, trsm, syr2k, her2k, gemmt, symm, 1m
  methods) - the same kernels through the full testsuite.
- Parameters choosing an STO's implementation are `--<sto>-tileop` (were
  `--<sto>-to`); family files' `params` use the new names.
- The full testsuite is postponed: it runs on native hardware (AVX-512, SVE,
  SME, RVV); failing kernels come back here to be tested one by one.
- Step 6: a packm family file (`--spackm-config`, `--dpackm-config`) lists
  cases - `kind: vec` (cdim = m vectors, A contiguous along cdim) or
  `kind: trans` (cdim = m elements, A contiguous along the panel) - each with
  its sizes and parameters (the flow's `pack` microkernel: Y = kappa X).
  `build_packm` builds each; `packm_dispatch` writes `bli_<ch>packm_<config>`:
  a full panel (cdim = cdim_max, n = n_max, no broadcast, P's rows cdim
  apart) of a size a case packs goes to it - vec when inca is 1, trans when
  lda is 1 - everything else to the reference `bli_<ch><ch>packm_<config>_ref`
  (declared by the dispatch), which also fills the edges. The context
  registers it (`BLIS_PACKM_KER`). Tested through the stub (full panels by
  the cases, others by the reference, all exact, SVE at 256 and 512 bits),
  then in BLIS: SVE vec cases 1..8 vectors for singles and doubles beside the
  gemm families, the reduced testsuite passing (1920 at 256 bits, 3648 at
  512) - packing A's MR panels (inca 1) by the generated cases.
- trans cases don't build yet: on SVE a strided vector store isn't a
  candidate (it needs scatters); on RVV the loop along n stepping by the
  vector length isn't counted yet (strip-mining). B's NR panels (lda 1) are
  the reference's until then.
- Family keys (gemm and packm; packm cases may set them too, over the
  family's): `unroll` (along k for gemm, n for packm), `loop-order`,
  `resolve-order`, `schedule` (scheduler distance specs), and per component
  `max-data-regs`, `max-preload`, `max-addr-regs`, `addr-pattern` (block,
  interleave, phase). Explicit `params` win over the keys.
- Register fitting with limits: an input's ceiling is its tiles,
  `--COMP-max-data-regs` and - with `--COMP-max-preload` - its minimal ring
  plus that many iterations of its tiles. The minimal ring (the most of its
  tiles needed again later in an iteration at once: 8x3v's B 3, A 1) comes
  first where the registers allow, so a kernel doesn't load a tile twice an
  iteration; what's left goes up to the ceilings, the inputs with most
  tiles first. 8x3v on SVE: A's broadcasts in a ring of 3 fitted, 2 with
  `max-data-regs: {A: 2}`, 1 with `max-preload: {A: 0}`.
- packm trans cases: a loop whose step is vectors (c x VL elements) counts
  chunks of a vector length - its parameter is n / VL, the loop unrolled
  over c chunks with the k loop's tail mechanism for what's left of them;
  the dispatch passes the chunks and leaves the last n % VL columns to the
  reference (A and P from the first column it packs). RVV trans cases
  (cdim 3, unrolled 1 and 2) exact at VLEN 128 and 256 through the stub,
  with and without columns left over, panels shorter than a vector the
  reference's. SVE: the same case with `store-tileop: Y.VEC:scatter` (the
  matcher's scatter resolution; SVE has no strided store) - exact at 256 and
  512 bits, unrolled 1 and 2.
- RVV gemm: the broadcast operand as an FP scalar (`fma[bdreg:VF](B.VEC:direct,
  A.FP:use_scalar, AB.VEC)`, vfmacc.vf), alpha and beta too - `bc_scalar`
  loads a scalar and broadcasts it into a vector register (vfmv.v.f), which
  costs vector registers the old kernels never used. Register fitting per
  register file (vectors, FP scalars where they're a file of their own), the
  scalar's file by its resolution (use_scalar/bc_scalar: FP) where the
  signature group's representative says VEC; one vector register kept per
  streamed component where instructions take no memory operand (all but
  x86) - C is loaded before its accumulator is consumed. The specializer
  keeps four column pointers per component and base, one more walking the
  rest (C's 14 columns). 8x3v and 2vx14 unrolled 4 exact at VLEN 128 and
  256; the RVV configurations build every size of the old failures' list.
