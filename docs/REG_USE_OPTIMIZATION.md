# Register use - what's there, plan and progress

Kernels run out of registers in two ways: general registers on x86 (16, two
of them rsp and rbp), and vector registers in large tiles everywhere. This
document lists what ukrgen already does about register use, records what
was found when it fell short, and tracks the plan - to come back to when a
feature runs into register limits again.

## What's there

Data registers (vector, FP, tile):

- Fitting by liveness (`lsc_model/builder.py: fit_registers`): accumulators
  live through the loop; streamed components (C in the epilogue) take no
  registers but one where vector instructions can't take memory operands;
  inputs share what a block's accumulators leave, a minimal ring first (no
  tile loaded twice an iteration), then up to `--COMP-max-data-regs` and
  `--COMP-max-preload`; per register file (RVV's FP scalars apart).
- Registers freed after the last block using them (emitter): the loop's A
  and B registers serve the epilogue.
- MRU (straight-line code): the cluster irmod pulls each chain together
  before addresses are fixed, scratch registers per data movement, the
  scheduler spreads within a window under a register budget, the emitter
  renames virtual registers onto free physical ones.
- Register groups (widening) count as one register for dependencies, as
  their members for the budget.

Address and general registers:

- `--COMP-max-addr-regs`, `--COMP-addr-pattern` (`rotate`, `blocked:N`,
  `phase`): a component's pointers.
- Column pointers for strided components: 4 kept per base and pointer,
  2 where there are 16 general registers (x86), one more walking the rest;
  `--loop-gregs` for slice loops' walks.
- Offsets in registers (emitter, computed once at the kernel's start):
  the vector length in bytes (`vl_bytes`), k vector lengths (`vl_multiple`
  - one add moves an address by k vectors), VL squared, VL-scaled and
  constant strides; shifted adds (`add_scaled`: AArch64 LSL, x86 `lea`
  scales) for stride multiples.
- Parameters released after the last region using them; C's storage
  branches' aliases share C's parameters.

## Found

The AVX2 gemm of `test_native` (A and B at run-time strides along k), the
k loop preloading with a ring of registers - its 16 general registers when
the allocation failed:

| holds | registers |
|-------|-----------|
| rsp, rbp | 2 |
| parameters held the whole kernel: base(A), base(B), base(C), base(alpha), base(beta), k, stride(A,k), stride(B,k), stride(C,n) | 9 |
| address, offset and counter registers (unnamed) | 5 |

- Loads an iteration ahead at a run-time stride take an offset register
  each distinct multiple of the stride; packed A and B (BLIS) have constant
  offsets - immediates - so this hits strided layouts.
- alpha's and beta's addresses, C's and its strides are held through the k
  loop though only the epilogue uses them; on x86 several of them come on
  the stack (the 7th argument on).

## Plan

| # | Step | Status |
|---|------|--------|
| 1 | Parameters passed on the stack loaded where first used, not at entry: none held through a loop that doesn't use them (one load a call, outside loops) | done: those no block before the cases uses load at the dispatch (asmgen's fngen records the save area's shift, `sp_shift`). x86 SysV passes alpha's, beta's and C's addresses in registers - held through the loop still: the strided AVX2 gemm with ring preloads still runs out; it needs step 3 (spilling register-passed parameters at entry) or step 2 |
| 2 | An offset optimizer: per component the distinct symbolic offsets; constants as immediates; an offset a multiple of another derived from it (shifted add, `lea` scales 1/2/4/8) - a register per stride and multiple class, not per offset; freed when dead | found: in the strided AVX2 gemm (A, B at run-time strides along k) the general registers go to pointers, not offsets - A's base and 3 more pointers, B's base and 2 more (column pointers, 2 kept on x86 plus one walking, one per stride multiple the unrolled and preloaded loads reach), beside 8 parameters; no offset registers. Plan: indexed addressing - `[base + index x scale]` on x86 (0, s, 2s, 4s, 8s from one pointer and the stride register already live; 3s one `lea`), `[x0, x1, lsl #n]` on AArch64 (asmgen support to check); the column-pointer cap from the general registers the live parameters leave, not a fixed 2, pointers walking beyond it; packed panels (BLIS) unaffected - immediates |
| 2a | asmgen `SCALEOFFSET` (scale_factor a structural parameter): x86 scales 1, 2, 4, 8 for scalar and vector loads and stores | done (asmgen 0032); AArch64 and SVE to add: scale 1 or the element size (`lsl #log2(size)`) - a stride in elements used directly |
| 2b | An `offset_planner` owning every decision on how an offset is formed - today spread over the emitter (`add_bytes`, `add_scaled`, `vl_bytes`, `vl_multiple`, `vl_squared`, `vl_stride`, `constant_stride`) and the specializer (column pointers and their caps, slice loops' walk plans): per access the cheapest form the ISA offers - an immediate within its limits (x86's 255 bytes, `MUL VL` ranges), a scaled index (probing `SCALEOFFSET`), a register already holding the offset or a multiple of it (shift, shifted add, `lea`), a pointer move - with the distinct offsets in registers tracked, freed when dead, against the general registers' budget. First moved as it is (the suite unchanged), then extended | in progress: the emitter's part moved (`emitters/signature.py: offset_planner` - the vector length's and strides' registers, `add_bytes`, `add_scaled`; the emitter delegating) - every example configuration's kernels byte-identical; next the column-pointer caps with 2c, the slice loops' walk plans as a step of their own |
| 2c | The planner using scaled indices for strided components: an access j strides away as base + stride x j (j in the ISA's scales), the column pointers only for other multiples; the strided AVX2 gemm's pointers measured | first part: an access a stride times 1, 2, 4 or 8 from its base (x86 with asmgen 0032) takes the base and the stride's register as a scaled index, no column pointer (specializer: `scaled_index`; emitter: GOFFSET + SCALEOFFSET, IOFFSET for a constant). The AVX-512 any-storage 8x3v: 226 of C's accesses so, its 14 general registers unchanged - C's other multiples (3, 5, 6, 7 strides) still need column pointers. The strided AVX2 gemm with ring preloads: none of the loop's 10 accesses qualify yet (A's broadcasts have no SCALEOFFSET signatures, B's offsets may carry a second stride term) - still out of general registers. Next: broadcasts' signatures, offsets of several terms, odd multiples from a derived register |
| 3 | `--allow-spilling {greg,freg,vreg,treg,address,data}`: values live across a loop but unused in it (alpha's and beta's addresses, rs_c) saved to the stack around it - a per-call cost, off by default; a trade for e.g. more offset registers for block-insert strides | |
| 4 | Preloads as v1 placed them, finished (work in progress: the first n loads per component hoisted, the next iteration's appended to the body, the last iteration without them; n stops before a register's second occupancy, counts lanes whole): decided per loop from its registers in use and free, `lsc_operation` reads and writes for any register reasoning (nested loops included), loops with virtual registers (MRU-renamed) capped by the physical budget probed first; the x86 exception removed; open failures `test_neon_runs`, `test_neon_15vx2`, `test_sve_15vx2` | in progress |
| 5 | Revisit with gemmsup (strided A and B in the main loop, v0.4): offset registers for strides in the loop | |

## Open questions

- Which parameters to load late: all stack-passed ones, or any parameter
  not used before a loop (register-passed ones would need a spill)?
- Spill slots: in the red zone (x86 SysV, leaf functions) or a frame of
  their own?
- Should the fitter know the general registers' budget (parameters,
  pointers, offsets) and trade it against preload depth, unrolling and
  column pointers - one register budget per file decided up front?
