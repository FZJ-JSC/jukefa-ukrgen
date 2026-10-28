# Packing across the grain: the plan

How packm's `trans` cases get the three strategies the research found
(docs/PACKING_TRANSPOSES.md): interleaving stores (`struct`), SME's ZA
tiles (`tile`), in-register networks (`shuffle`) - what asmgen and ukrgen
lack, in what order to build it, and how SME + SVE kernels' panels
(cdim = N·VL + M) pack.

## Where packm is

- A `trans` case packs a panel whose rows (cdim of them, m) are contiguous
  along its length (n, k for gemm): `mul(X.VEC:direct, kappa.VEC:bc_load,
  Y.VEC){m=1, i=n}` loads a row's vector along n, scales it, and
  `store-tileop: Y.VEC:scatter` (SVE, SME, AVX-512) or the `strided`
  resolution (RVV) stores it across P - element j of row i at P + j·MR + i.
  AVX2 has no scatter: its only cdim-strided case is `gather` (vectors
  along cdim gathered from X).
- So before the stores, the N rows of a step are N registers, row i in
  register i: every strategy replaces the N row stores that follow.
- What's there already:
  - register groups (`program.groups`): consecutive registers from a
    multiple of the group's size, allocated by the emitter at once;
  - the emitter's `members`: one `STRUCT` signature moving a whole group,
    interleaved; widen's `struct_sigs(gen, op, dt, ways)`: the signatures
    whose element e of register p is at `ways·e + p` - a packed panel when
    ways = cdim;
  - SME's slices: tile operands with `ROW`/`COL`, slice loops
    (`lsc_loop` kind `slices`) and their irmods (fuse_slices,
    forward_slices, hoist_slices), C in ZA for the outer products;
  - `transformation.TRANSPOSE` in the matcher, with no resolution;
  - and the design note in `support/data_move.py`: instructions moving
    several registers come from irmods fusing single-register ones, not
    from the solver. The three strategies are irmods over the trans case's
    IR: no matcher or solver change to begin with.

## asmgen

- **A1 `STRUCT` means interleaving only** - done (asmgen 0084: `MULTIVEC`). On SME, SME2's multi-vector
  contiguous loads and stores (`ldnt1d {z0.d, z8.d}, pn8/z, [x0]`) carry
  `STRUCT` and `nstructs` 2 or 4 as the interleaving `ld2d`-`ld4d` do:
  `struct_sigs` would take one for the other. They need a modifier of their
  own (`MULTIVEC`, say, with `nvectors`) - a correctness fix, first.
- **A2 SVE's structure addressing** - done (asmgen 0086). SVE's `ld2d`-`ld4d`, `st2d`-`st4d`
  have the plain form only: add `[x, #imm, MUL VL]` (`VOFFSET`, imm a
  multiple of nstructs) and `[x, x, lsl #3]` (`GOFFSET`, `SCALEOFFSET`),
  which a loop over a panel's steps uses. NEON's post-increment forms are
  there; RVV's segments are plain, and enough.
- **A3 A mask of the first M lanes** - done (asmgen 0085: `mask="first"`,
  `count`). `set` with `CONSTMASK` makes
  all-true and all-false only. Add `count=M`: SVE `ptrue p.d, vlM` where
  M is a pattern (1-8, 16, 32, ...), `whilelo` otherwise; AVX-512 a `kmov`
  of (1<<M)-1; RVV a vector length. ZA's partial tiles and k remainders
  need it.
- **A4 A permute operation** - done (asmgen 0087: `opmove` `PERMUTE`, `permuted()`). Two sources, one destination, a pattern at
  a granularity, one instruction each:
  - zip low and high halves (NEON and SVE `zip1`/`zip2`) - x86's
    `vunpcklpd`/`vunpckhpd` (`ps`) zip within each 128-bit lane, a pattern
    of its own;
  - unzip even and odd (`uzp1`/`uzp2`), transpose pairs (`trn1`/`trn2`);
  - 128-bit block selects with an immediate: `vshuff64x2`/`vshuff32x4`
    (AVX-512), `vperm2f128` (AVX2).
  On `opmove` with `MULTIPLE_IN` and pattern modifiers, or an operation of
  its own; forms on x86, NEON and SVE (RVV packs with segments). The
  network built of them is ukrgen's.
- **A3b A mask, a vector length from a register.** Any M, not only a
  pattern's: SVE's `whilelo p.T, xzr, x<avl>` as `set` with `MASKAVL` and
  `avlreg` (the first avl elements, at most the vector's); RVV's
  `vsetvli rd, avl` as `set(VLEN, avlreg=)` - the vector length for avl
  elements, `VLEN` reading and setting it. The setup makes them one feature,
  the vector length the caller chooses: RVV's `set(VLEN, avlreg)`, SVE's
  default predicate by `MASKAVL` (`isa_setup.setup(vl=)`, the aliased
  avl). AVX-512 needs a scratch register for it: later.
- **A5 ZA**: slice loads and stores (`ld1d {za0h.d[w12, i]}`,
  `st1d {za0v.d[w12, i]}`, predicated) and `mova` (SME2: four slices at
  once) are there - check the tile numbering for `.d` (za0-za7) and the
  predicated slice store.
- **A6 later**: SVE2.1's quadword forms (`zipq1/2`, `st2q`-`st4q`) for
  more than 4 rows at a time on SVE.

## ukrgen

- **U1 Rows as a group.** For a structure store the N row registers are
  consecutive: the irmod sets `program.groups` for Y's component (N) and
  the store's `group` property; the emitter's allocation and `members` do
  the rest.
- **U2 Three irmods** recognizing a step's N row stores to Y at stride N
  from consecutive rows, each refusing what it can't do:
  - `structfuse` - done (ukrgen 0184): cdim N up to the ISA's structures
    (NEON and SVE 4, RVV 8): a step's N strided row stores - consecutive
    registers, rows a row apart in the model's offset records - one store
    of the group (`struct_sigs`), the rows' registers one group; opt-in
    (`pre-specialize-irmods`), the cases choosing it after ukropt's
    measurements (U5, U8).
  - `za_transpose` (SME, streaming) - ⌈cdim/v⌉ tiles (v = SVL / element
    bits): row i into horizontal slice i mod v of tile ⌊i/v⌋ (straight from
    X with `ld1d za{t}h` where kappa is 1; else loaded, scaled, `mova`d),
    columns out of the vertical slices to P + k·cdim + t·v, the last tile's
    under a first-M-lanes predicate (A3); k in steps of v, the remainder
    predicated; the slice loops and their irmods as for C.
  - `shufflenet` (AVX2, AVX-512, NEON - refused where `is_vla`) - its
    networks found (ukrgen 0189: `support/transpose.py`, the fewest rounds
    of the ISA's permutes by a search checked with `permuted()`: NEON
    doubles 1, singles 2; AVX2 2 and 3; AVX-512 3 - AMD's - and 4); done
    (ukrgen 0192): `lsc_permute` and the emitter writing it, the irmod
    rewriting a step's row stores (in place, one spare register), the
    `shuffle` store resolution for ISAs without scatters (named only, refused
    without the irmod) - AVX-512 8 and 16 rows, AVX2 4 and 8, NEON 2 and 4
    against the reference; the configs' cases (ukrgen 0194): dpackm's AVX2 4 and 8 rows, NEON 2-16 in pairs, AVX-512 8 and 16 (its scatters for the others); spackm's (ukrgen 0195): AVX2 8 rows, NEON 4-16, AVX-512 16; shufflenet runs wherever a shuffle store is - no irmods listed. N = the
    lanes' count (or blocks of it: AMD's 24 = 3 x 8 doubles), log2(lanes)
    rounds of permutes (A4) by a recipe per ISA (x86: in-lane unpacks, then
    block selects; NEON: `trn` per element, then per 64 bits), then N
    contiguous stores; lanes more registers for the rounds (8x8 doubles:
    16 zmm).
- **U3 IR and emission**: an op for a permute (two inputs, one output, the
  pattern) or `lsc_transformation` with a modifier, which the signature
  emitter writes through A4; ZA's slice ops as SME's gemm has them.
- **U4 Matching (later)**: resolutions for `TRANSPOSE` - (VEC, OUT, MEMORY)
  - so a tileop names the strategy (`Y.VEC:struct`, `:tile`, `:shuffle`)
  instead of a case listing an irmod; once the irmods have proved out.
- **U5 Cases**: a case's irmods name its strategy, its sizes what the
  strategy takes - struct: m 1..4 (SVE, NEON), 1..8 (RVV); shuffle: m a
  multiple of the lanes; tile: any m. New cases: AVX2 `trans` (no scatter:
  the network makes it possible), NEON `trans` (`st2`-`st4`, `trn`
  networks). The kernels' symbols stay (`bli_?packm_<cfg>_<fam>_trans<m>`).
- **U6 Split kernels' panels**: a packm case whose cdim is a split
  kernel's MR - N·VL + M, an expression of VL - rather than fixed 1..16.
- **U7 Tests**: test_pack natively (AVX2, AVX-512) and under qemu (NEON,
  SVE, SME, RVV): each strategy's panels against the reference - cdim at its
  edges (M 1 and v-1), k remainders, kappa other than 1.
- **U8 ukropt**: scatters against `st4d` (SVE hardware), strided against
  segment stores (RVV cores - microcoded on some), gathers against networks
  (Zen 4, 5), scatters against ZA (SME parts).

## Any cdim by structures: splits

A structure store writes its structures back to back - nstructs elements
each - so st4d of rows 0-3 puts k=1's rows where k=0's rows 4-6 belong
when cdim is 7. A split - 7 = 4 + 3, 5 = 4 + 1 or 2 + 3 - needs the
structures cdim apart:

- RVV: strided segment stores (`vssseg<nf>e64.v vs, (rs), stride`):
  rows 0-3 at P, rows 4-6 at P + 4, both stride cdim·8 bytes - any cdim,
  each part's fields within EMUL·NF ≤ 8. asmgen has the plain segment
  forms only: **A7** RVV's strided segment loads and stores (`STRUCT` with
  `GSTRIDE`: vlsseg, vssseg).
- NEON: one structure from a lane (`st4 {v0.d-v3.d}[i], [x]`) - a split
  per k element, two a vector of doubles; check asmgen's lane forms.
- SVE: neither - its structure stores are back to back: cdim 2-4 only.

## A family's choices (YAML)

What the plan's sketches became - each a packm family's to choose, and
ukropt's `--blis` grid to sweep:

- **Which cases, in which order** (sketched as `packm-dispatch: [vec,
  maskvec, shuffle, struct, tile, masktile]`): the family's `dispatch:
  [names]` (ukrgen 0197) - the cases its dispatch tries, in that order, the
  others not built. A strategy is a case: its `kind` (vec, gather, trans)
  says what it packs, its `name` which of a kind it is - `name:
  trans_shuffle` with `store-tileop: ['Y.VEC:shuffle']`, `name: vtail` with
  `mask: true`. Default: masked vec cases, vec, gather, trans.
- **Splits** (sketched as `struct-split: {7: [4, 3]}`): structfuse's
  `fields` (ukrgen 0202) - the most rows one structure store takes, a
  step's rows beyond it parted greedily (12 = 8 + 4; `fields` 3: 5 = 3 +
  2), each part a strided segment store on RVV (asmgen 0090); a flow
  parameter, `structfuse-fields`, under a case's `params:`. Parts by hand
  (ukrgen 0206): `structfuse-split: "12=4+8,5=2+3"` - by row count, in
  order, over fields' greedy ones (a part of 1 row its strided store).
- **Masks** (sketched as `masks: on`): a vec case's `mask: true` (ukrgen
  0203) - size N packs N vectors and a last one masked to the rows left,
  cdim from N*VL to (N+1)*VL in one pass. SVE's; AVX-512's and RVV's to
  come.
- And: `vec-rest` (0200), the rows a vec case packs beyond its own; `lmul`
  (0201), RVV's LMUL by size; passes toggled against the defaults,
  `pre-specialize-irmods: [+structfuse, -cluster]` (0200) - a flow
  parameter, so under `params:`; a string in a grid (`+structfuse`). Keys a
  family's YAML doesn't know are refused (0204) - a flow parameter beside
  `m:` used to vanish.

Where each goes: `dispatch`, `vec-rest`, `lmul` (a default) on the family;
`kind`, `name`, `m`, `mask`, `lmul` on a case; flow parameters - irmods,
`structfuse-fields`, layouts, tileops - under a case's (or the family's)
`params:`. Possible: copy cases for kappa 1 - gemm's alpha and beta cases'
mechanism (a branch in the kernel) or the dispatch trying them where
`*kappa == 1`; today every case multiplies.

## The rows a vec case leaves: an overlapping kernel

cdim = N*VL + M with A's columns contiguous - the K1's A panels of 14
and 6 rows - went to a vec case and the reference for the M rows; BLIS's
reference cost ~660 cycles a column for 2 rows there (pack A 24-54x
slower than an exact panel). Done (ukrgen 0208): the rows left packed by
a kernel of the case ending at cdim - the smallest covering them that
fits in cdim - its first rows packed again with the same values (14 =
vec3v + vec1v from row 10); the reference only below a vector and for
the padding. A family's `vec-tail: reference` keeps the reference.
Masks (SVE's done, RVV's to come) pack it in one pass.

## Across the grain on large vectors: blocks of rows

A trans case's kernel packs its rows, 1 to 16, a full panel of them -
but large vectors' cdims are 2*VL rows and more (VLEN 1024: 32 doubles;
16384: 512), past any one kernel's: the reference packed them. Done
(ukrgen 0207): a trans case taking P's leading dimension (`Y-layout
['m:c', 'n:s']`) is a block case - the dispatch, for A's rows contiguous
(lda 1) and any cdim, calls its kernels on blocks of rows, each as many
times as fit, the widest first, at A's and P's rows done, P's rows ldp
apart; the reference only for a block's last columns (n past whole
chunks), rows no kernel fits and the padding. Its structfuse stores are
strided (vssseg, the stride ldp): plain segments only where P's rows are
the fused rows apart. Tried after full-panel trans cases by default.

```yaml
- kind: trans
  name: tblock
  m: [16, 8, 4, 2, 1]
  params: {..., Y-layout: ['m:c', 'n:s'], X-data-regs: '4', pre-specialize-irmods: ['+structfuse']}
```

## Vectors along cdim under a predicate: cdim = n·VL + M

Done for SVE (ukrgen 0203): a vec case with `mask: true` - size N packs N
vectors and a last one under a mask of its first M rows, M = cdim - N*VL a
run-time parameter (`tail(m)`), the mask set once after the ISA's setup
(whilelo) - cdim from N*VL to (N+1)*VL in one pass, below VL with N = 0.
The dispatch tries masked cases first; the reference only zeroes rows past
cdim. RVV's v0 route done (ukrgen 0209 on asmgen 0091): the mask set
once in v0 (vid.v into a scratch vector, vmsltu.vx from tail(m)), the
last vector's load and store their masked twins (v0.t). Still to come:
AVX-512 (asmgen 0092 sets its k mask from a register; it needs masked
plain loads and stores, and tail(m) - the 7th argument - loaded from the
stack before the setup); RVV's other route, the vector length switched
for the last vector (vl a dependency every vector operation reads).

With masks of the first M lanes (A3) the `vec` route - vectors along
cdim, X contiguous along it - packs what isn't whole vectors too, where
today the reference does: cdim = n·VL + M, n whole vectors and a last one
of M < VL elements, cdim < VL the case n = 0.

- SVE: the last vector's loads and stores under `ptrue p.d, vlM` - M a
  pattern, and no more than the vector has: a pattern past the vector's
  elements makes the predicate all false, so M is bounded by the smallest
  vector the kernel runs on (doubles: 2 at 128 bits, 8 at 512), or `whilelo`
  from a register where it isn't (a scratch register: the kernel's).
- AVX-512: under `kxnorw`, `kshiftrw` by 16 - M (FP64 and FP32 lanes).
- RVV: no mask - the vector length: the last vector's `vsetvli` with avl M
  (the setup's vl), the caller's avl register where BLIS's context chooses
  the length.
- ukrgen: a `vec` case sized n·VL + M - the last vector's accesses taking
  the mask (a tileop's operand, the mask a resolution's setup) - and,
  together with the trans strategies, the panels of split kernels (U6) by
  the vec route where X is contiguous along cdim.

## SME + SVE: cdim = N·VL + M

The split gemm (`smesve/fopa_fma_split`) computes MR = N·VL rows by outer
products (ZA) and the rest by FMAs (SVE); its A panel is packed as any:
MR contiguous elements per k. Its packm today scatters 1..16 rows.

- **ZA packs all of it.** ⌈cdim/v⌉ tiles - N full, one partial (M < v):
  rows into horizontal slices, columns out of the vertical slices at P +
  k·MR + t·v, the partial tile's columns stored under a predicate for its
  first M lanes (A3). No SVE store path. Eight tiles for doubles (za0.d
  -za7.d): cdim up to 8v = SVL/8 doubles a pass. v is the machine's, but N
  and M are the case's: the tiles' number and the predicate are static.
- **ZA and SVE mixed** - ZA for N·v rows, SVE for M - is worse: `st{M}d`
  would interleave the M rows contiguously, M per k, not at MR; the M part
  would need scatters or a store per k. The predicated tile is simpler and
  avoids the scatters, which streaming mode runs slowly on current parts.
- **kappa**: ZA's slice loads and stores don't compute. kappa 1 (BLIS's
  common case) goes straight between memory and slices; other kappa
  through Z - a row loaded, `fmul`, `mova` into its slice (or a column
  `mova`d out, scaled, stored) - SME2's four-slice `mova` halving the
  moves.
- **k** in steps of v per pass, the remainder under `ld1d`'s predicate:
  the slice loops' iterations.

## Related: the vector length the caller chooses (RVV)

On some hardware a vector length other than the most there is performs
best - a multiple of 40 elements: 240 doubles of 256 on a 16384-bit
machine. BLIS's context computes it (`bli_vlen_utils.c`), the kernel's
`vsetvli` takes it in a register. asmgen's RVV setup takes a caller's
aliased `avl` register (asmgen 0083). Still to come: a parameter for it
in the flow, the BLIS injector passing the context's length, and
`vsetvli` with the aliased avl instead of zero outside the microkernel
(not `csrr vlenb`) where the length is read.

## Order

1. asmgen A1 (STRUCT is interleaving), A3 (first-M masks), A2 (SVE
   structure addressing) - done (asmgen 0084-0086).
2. ukrgen `structfuse` - done (ukrgen 0184); its splits (RVV's strided
   segments: A7, the `struct-split` key), the family keys (splits, the
   dispatch's implementations, masks) and cases; the `vec` route under a
   predicate (cdim = n·VL + M) beside it.
3. asmgen A4 (permutes); ukrgen `shufflenet` (AVX-512 8x8 and 24, AVX2
   4x4, NEON) and AVX2's trans case.
4. ukrgen `za_transpose`, then the split kernels' cdim (U6).
5. ukropt's measurements; strategies named by tileops (U4).
