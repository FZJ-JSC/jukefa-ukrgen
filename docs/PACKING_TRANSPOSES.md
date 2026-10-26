# Packing across the grain: shuffles, structures, ZA

How packm moves a panel whose elements lie apart along the packed dimension
(the `trans` cases: A contiguous along the panel, `lda` 1), what AMD's zen4
kernels do instead of gathers, and what each ISA offers for it. Research for
a plan, nothing built yet.

## Where ukrgen is

- The `pack` microkernel is `Y(m,n) = kappa X(m,n)`; X's strides decide the
  case. `kind: vec` (X contiguous along cdim) copies vectors; `kind: trans`
  (X contiguous along the panel) loads vectors along the panel and stores
  them across P - RVV with strided stores (`vsse`), SVE with scatters (the
  matcher's `scatter` resolution, `store-tileop: Y.VEC:scatter`); AVX2 and
  AVX-512 have `kind: gather` cases loading along cdim with gathers.
- The data-movement solver resolves one vector at a time: resolutions keyed
  by transformation, register type, direction and location - `direct`,
  `strided` (GSTRIDE), `gather`/`scatter` (VINDEX), `lanes` (one ILANE load or
  store per lane), block-lane inserts (`support/dm_resolutions/strided.py`).
- `matching.math.transformation.TRANSPOSE` exists - (i,j) -> (j,i) - but no
  resolution is registered for it.

## AMD zen4: an 8x8 transpose in registers

`kernels/zen4/1m/bli_packm_zen4_asm_d8xk.c` (and `d24xk`, three such blocks
plus kappa) packs MR = 8 doubles:

- A's columns contiguous (`inca` 1): a copy, `vmovupd` per k.
- A's rows contiguous (the trans case): per 8 k, 8 row loads (`vmovupd`,
  8 doubles along k each), a transpose in three rounds, 8 stores of 8
  m-elements - P's layout:
  1. `UNPACK_LO_HIGH`: `vunpcklpd`/`vunpckhpd` interleave pairs of rows within
     each 128-bit lane (2x2 blocks);
  2. `SHUFFLE_DATA`: `vshuff64x2` with `0x88`/`0xDD` takes the even and odd
     128-bit lanes of two registers (4x4 blocks);
  3. `SHUFFLE_DATA` again (8x8).
  24 permutes per 8x8 block - log2(8) = 3 a vector - beside 8 loads and 8
  stores, no gathers or scatters. The k remainder loads under a mask
  (`MASK_KZ`); `d24xk` adds `vmulpd` by a broadcast kappa where it isn't 1.

The network is fixed by the lane count: log2(lanes) rounds over a block of
lanes x lanes registers, each round's permutes chosen for its granularity.

## By ISA

| ISA | in-register transpose | interleaving stores | other |
|---|---|---|---|
| AVX-512 | 8x8 doubles: unpck + 2x `vshuff64x2` (AMD's); 16x16 singles: 4 rounds | none | gathers, scatters (slow) |
| AVX2 | 4x4 doubles: unpck + `vperm2f128`; 8x8 singles: `unpcklps`/`shufps`/`vperm2f128` | none | gathers |
| NEON | 2x2 doubles: `trn1`/`trn2` (.2d); 4x4 singles: `trn` .4s then .2d | `st2`/`st3`/`st4`: 2-4 rows | lane stores |
| SVE | rounds and block depend on VL: only with code per VL, chosen at run time | `st2d`-`st4d`: 2-4 rows, any VL | scatters (today's); SVE2.1 `zipq1/2`, `st2q`-`st4q` work within 128-bit segments |
| SME | through ZA instead | as SVE | rows into a tile's horizontal slices (`ld1d {za0h.d[w12, i]}`), columns out of its vertical ones (`st1d {za0v.d[w12, i]}`) - a transpose at any SVL, a tile of SVL/64 x SVL/64 doubles, 8 tiles; `mova` between slices and Z |
| RVV | `vrgather` with index vectors from VL - possible, but slow on most cores | `vsseg2`-`vsseg8`: 2-8 rows (EMUL x fields <= 8), any VL | strided stores (today's) |

So the AMD scheme carries to the fixed-size ISAs - AVX2, AVX-512, NEON - as
it is; on SVE and RVV it would need a network per vector length, chosen at
run time. The vector-length-agnostic ISAs have their own transposes:
interleaving stores of 2-4 rows (SVE, NEON) or 2-8 (RVV) - exactly a packed
panel when cdim is the number of rows, as B's NR panels are - and on SME
the ZA tiles, which transpose at any vector length. x86 has no interleaving
stores: shuffles or gathers.

## What asmgen has

Asked of asmgen 0.6's operations (`forms`):

- `STRUCT` loads and stores: NEON and SVE 2-4 registers, SME the same, RVV
  segments of 1-8 fields; none on x86.
- SME tile slices: loads, stores and moves with `ROW`/`COL` operands.
- No permute operation: `vshuff64x2`, `vperm2f128`, `vrgather` are used only
  inside broadcasts and lane moves; zips, unzips, transposes (`trn`) and
  unpacks are missing.

## What it would take

1. asmgen: a permute operation - interleave low and high halves (`zip1/2`,
   `vunpckl/hpd`), even and odd (`uzp1/2`), transpose pairs (`trn1/2`), and
   block selects (`vshuff64x2`, `vperm2f128`) - with forms on x86 and NEON
   (SVE's zips for completeness).
2. ukrgen's solver: steps over a group of vectors - one instruction for N
   operand vectors - which every option needs; today a step moves one
   vector (or a lane of it).
3. Resolutions for `TRANSPOSE`:
   - `struct`: N vectors along the panel stored interleaved where cdim is N
     (`STRUCT` stores); VLA, replaces scatters (SVE) and strided stores
     (RVV) for B's NR <= 4 (SVE, NEON) or <= 8 (RVV);
   - `tile` (SME): rows into ZA's horizontal slices, columns out of the
     vertical ones, over the slice repeat levels the solver has;
   - `shuffle` (fixed-size ISAs only - refused where `is_vla`): N
     contiguous loads, a log2(N)-round network from the permute forms, N
     contiguous stores - AMD's, for AVX and NEON.
4. packm: `trans` cases choose among them as today's choose `scatter`
   (`store-tileop: Y.VEC:struct`), `gather` cases on AVX get a `shuffle`
   alternative.
5. ukropt measures them against each other: scatters against `st4d` on SVE
   hardware, strided against segment stores on RVV cores (segment stores are
   microcoded on some, the X60 among them), gathers against shuffles on
   Zen 4.
