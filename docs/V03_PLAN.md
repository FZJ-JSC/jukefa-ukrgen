# ukrgen v0.3: prefetches and non-temporal accesses - plan and progress

v0.2 (blisgen stage 1, `docs/BLISGEN_PLAN.md`) is feature-complete: kernel
families, presets, split kernels, packm, run-time kernel choice, BLIS
patching, parallel builds, example configurations. v0.3 adds control over the
memory hierarchy: prefetches and non-temporal accesses, parameterized like
everything else and measured on hardware. This document is the plan and is
updated as the work lands.

## v0.2 leftovers (carried over)

| item | status |
|------|--------|
| v0.2 step 8: retire the old patcher (`injectors/blis/patcher.py`, the old flow it drives); keep the templates still used (registration insertions, license, `make_defs.mk`, kernel definitions) in the new path's module | open |
| The five old-API test failures (generators/test_mm, models/test_loop, specializers/test_lsc_specializer): port or retire | open |
| The scheduler's register budget for straight-line code doesn't count registers a loop inside it holds (an unrolled slice loop's register sets) | open |
| Bugs found by colleagues testing v0.2 | as reported |

## Goals

- Prefetches as first-class operations: target cache level, read or write,
  keep or stream (ARM's KEEP/STRM), non-temporal - each ISA's own concepts
  where it has them (RISC-V Zihintntl's `ntl.p1`/`ntl.pall`/`ntl.s1`/`ntl.all`
  combined with Zicbop's `prefetch.r`/`prefetch.w`), the nearest equivalent
  or nothing where it doesn't.
- Streaming prefetches attached to a component's accesses - A and B in
  gemm, X and Y in packm - a distance ahead, one per cache line reached.
- C's prefetch parameterized: where (before the k loop; the k loop split to
  prefetch a given number of iterations before its end; after it), into which
  level, all of the tile or the first N lines per row or column.
- Non-temporal loads and stores where they help (packm's source; optionally C).
- VLA ISAs: a cache line relative to the vector length,
  `cl-size: {0.25, 0.5, 1, 2, 4} x VLEN` (or bytes), since a vector may span
  several lines or a line several vectors.
- Correctness unchanged (hints only); benefit measured natively.

## Design

### asmgen

- The `opmem` prefetches (x86, AArch64, RISC-V; 8554054 - their modifiers
  were never committed) gain modifiers with structural parameters:
  `CACHE_HINT` (cache_level: L1, L2, L3; LPL and LSF on RISC-V - Zihintntl's
  last private and first shared levels), `LOCALITY_HINT` (STRM, KEEP),
  `USAGE_HINT` (RD, WR) - on the shared `opmem` base, loads and stores taking
  those that apply to them (a non-temporal hint on an access). Offset domains
  constrained like loads' (`constraint_domain`):

  | ISA | instructions | offsets |
  |-----|--------------|---------|
  | x86 | `prefetcht0/t1/t2`, `prefetchnta`, `prefetchw` (PRFCHW) | disp32 |
  | AArch64 | `prfm {PLD,PST,PLI}{L1,L2,L3}{KEEP,STRM}`, `prfum` | uimm12 x 8; simm9 |
  | SVE | `prfb/prfh/prfw/prfd` (predicated, contiguous; gathers) | -32..31 MUL VL |
  | RISC-V | Zicbop `prefetch.r/.w/.i`; Zihintntl `ntl.*` before the access | 12-bit, low 5 bits zero |

  An ISA without a requested variant raises NotImplementedError with the
  reason (listed in `allowed_not_implemented`); the planner falls back to the
  nearest (a level it has, read for write, ...) where the family allows.
- Non-temporal accesses as load/store signature modifiers: x86 `vmovntps/pd`
  (aligned stores), SVE `ldnt1/stnt1`, AArch64 `ldnp/stnp`, RVV loads and
  stores preceded by an `ntl.*` hint. Alignment requirements as constraints.
- Open: which prefetches are legal in SME streaming mode (without FA64).

### IR and model

- `lsc_prefetch`: a component, an offset (elements, symbolic - VL terms
  included) and the attributes; reads its address register, writes nothing.
  The specializer adapts its address like a load's (immediates, VOFFSET,
  pointers); the emitter emits the ISA's form; the scheduler treats it as
  independent but for the address register, its placement spread.
- Cache lines: `--cl-size BYTES` or `--cl-size Fx` (F times the vector length
  in bytes) - the number of prefetches per vector or the vectors per line.
- Stream prefetches (an irmod): `--COMP-prefetch distance=D[it|B],level=L,
  intent=read|write,retention=keep|stream|nt` - for each loop iteration,
  each cache line the component's accesses reach D iterations (or bytes)
  ahead is prefetched once, next to the accesses it anticipates; lines
  shared between iterations counted once (a line every k-th iteration).
- C (gemm): `--C-prefetch where=before|split:N|after,level=L,
  lines=all|first:N,along=column|row`:
  - `before`: in the k loop's prologue;
  - `split:N`: the k loop split - its last N iterations a loop of their own
    carrying C's prefetches among its instructions (k = (k - N) + N, the tail
    mechanism alike);
  - `after`: between the k loop and the epilogue;
  - all of the tile, or the first N lines of each column (row).
- Non-temporal: `--COMP-nontemporal load|store|both` - the resolutions'
  accesses take the NT form or hint.

### Families and blisgen

- Family keys `prefetch:` (per component), `cl-size:`, `nontemporal:`; per
  ISA presets of prefetch settings once measured (`prefetch_stream_l1`, ...).
- Example configurations: prefetch off until measurements say otherwise; a
  `*_pf` variant per ISA with the measured settings.

### Measuring

- A native microbenchmark driver: a gemm microkernel's loop over packed
  panels of a given k (cycles, GFLOP/s), and BLIS level-3 gemm through the
  library; a sweep script over prefetch parameters (distance, level,
  `cl-size`, C's placement) writing a table. Runs on the hardware (AVX2,
  AVX-512, SVE, SME, RVV); qemu checks correctness only.

## Steps

| # | Step | Status |
|---|------|--------|
| 0 | v0.2 leftovers above | |
| 1 | asmgen: prefetch modifiers on the existing `opmem` prefetches (`x86/`, `aarch64/`, `riscv64/opmem/prefetch.py`, from 8554054; `dregs`/`dt` already optional) - `CACHE_HINT` (cache_level: L1 on all; L2, L3 on x86 and AArch64; LPL, last private, and LSF, first shared, on RISC-V), `LOCALITY_HINT` (locality: STRM, KEEP), `USAGE_HINT` (usage: RD, WR) as structural parameters, on the shared `opmem` base so loads and stores take those that apply to them; SVE `prf*`; offset domains; `test_asm_implemented` | redo: the modifiers were never committed (lost locally); the basic prefetches survive |
| 2 | asmgen: non-temporal load/store modifiers - x86, SVE, AArch64 pairs, RVV `ntl.*` | |
| 3 | ukrgen IR: `lsc_prefetch`, specializer and emitter support, scheduling | |
| 4 | Cache-line model, `cl-size` (bytes or a multiple of the vector length) | |
| 5 | Stream prefetch irmod for loop components (A/B, X/Y) | |
| 6 | C prefetch: before, split:N (k loop split), after; levels; all or first N lines | |
| 7 | Non-temporal accesses in the model: packm's source, optionally C | |
| 8 | Family keys, presets, example `*_pf` configurations, docs | |
| 9 | Native microbenchmark driver and parameter sweep | |
| 10 | Measurements on hardware; defaults per ISA from them | |

## Open questions

- Prefetch distance: iterations, bytes, or both (bytes for packm's panels,
  iterations for gemm's)?
- Should C's `split:N` reuse the k tail's machinery (a loop of its own) or
  peel N iterations into straight-line code (the scheduler interleaving
  prefetches freely)?
- Hardware prefetchers already cover contiguous packed panels on most cores:
  default A/B prefetching off and C prefetching on?
- SME streaming mode: prefetches allowed, and which?
