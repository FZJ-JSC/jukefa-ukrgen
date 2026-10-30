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
last vector's load and store their masked twins (v0.t). AVX-512's done
(ukrgen 0210 on asmgen 0092, 0093): the k mask set once (movq, bzhiq,
kmovw from tail(m) - the 7th argument, on the stack, loaded at entry),
the last vector's vmovupd its masked twin. RVV's other route
done (ukrgen 0211): `tailmask-route: vl` - each last-vector load and
store between vsetvli zero, tail and vsetvli zero, full (the full length
set once in a register): nothing else runs short, so no schedule can
break it; v0 stays free, two vsetvli an access. Sweepable against the
default `mask` per case.

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

## SME: the ZA transpose - what exists, what's missing

Investigated (no code changed). The transpose needs no new asmgen forms
and is a tileop pair ukrgen's solver already generates:

```yaml
pack-tileop:  ['mul(X.VEC:direct, kappa.VEC:bc_load, Y.TILE:>slice_vec_row){m=1, i=n}']
store-tileop: ['Y.TILE:slices_col']
```

each row of A scaled and moved into a horizontal slice (`mova za0h.d[w12,
0]`), each vertical slice - one of P's columns - stored contiguously
(`st1d {za0v.d[w12, 0]}`): per chunk of VL columns, rows in and columns
out, no scatters.

- **asmgen**: ZA slice loads and stores (A5) are there - `ld1d
  {za0h.d[w12, imm]}`, `st1d {za0v.d[w12, imm]}`, index registers
  w12-w15, imm 0 to 16/element size - 1, base or base + register
  addressing - and `mova` between vectors and slices.
- **ukrgen**: tile resolutions are there - `slices_row`/`slices_col` (a
  tile to or from memory slice by slice, as many as it has at run time)
  and `slice_vec_row`/`slice_vec_col` (a slice through a vector) - SME
  gemm's epilogue's. With the chain check bypassed the kernel builds:
  `ld1d`, `fmul`, `mova za0h` per row, `st1d za0v` per column.

Two gaps the prototype found:

- **Z1 the solver's chain check** refuses the pair: "store stores Y
  contiguous, but as pack leaves it the store has to be strided" - it
  takes the access from the pack STO's vector axis (n), not seeing that a
  tile is stored by slices of its own direction: `slices_col` runs along
  m, P's contiguous index. io_of gives a tile store its slices' direction.
- **Z2 a tile stored inside a loop**: the slice loop advances P's address
  (`incb` a slice), then the n loop adds the chunk again and the last
  iteration takes it back - under qemu (SVL 256) two chunks came out right
  by accident, one wrote before P. gemm stores its tile once, after its
  loop. The slice loop leaves the address where the loop expects it.

### FA64: scatters in streaming mode

The SME configs' trans cases scatter (`st1d {z.d}, p0, [x2, z0.d]`)
between `smstart` and `smstop`. Streaming mode runs gathers and scatters
only with FEAT_SME_FA64: Apple's parts don't have it, LX2 does - LX2 also
being the SME + SVE (fmopa + fmla) kernels' target. qemu's `max` has it,
so the tests can't tell.

- **Z5** FA64 a capability a config declares, as AVX-512's DQ and BW: the
  SME generator's streaming gathers and scatters require it; ukrgen offers
  them only where the config says so (LX2's), the ZA transpose everywhere.
  SME tests of configs without it run qemu with `sme_fa64=off`. SME gemm's
  C "across vectors by gathers" (fopa_bc_vindex) is checked the same way.

### Steps

1. **Z1** the chain check - done (ukrgen 0217): a tile filled through
   slices of one direction and stored through the other is a transpose -
   its store's access along the tile's other index; gemm's C (filled and
   stored by columns) as before.
2. **Z2** tile stores inside loops (1, 2, 3 chunks under qemu, SVL 256
   and 512) - done (ukrgen 0218): the slice loops walked their address
   registers (A's a row a slice, P's a column) and left them there; the
   specializer planned from there, the n loop's back edge didn't - one
   chunk wrote before P. Each slice loop now steps its registers back by
   their walk, the specializer planning from home: one to five chunks
   right. Two and four tiles (ukrgen 0219): a loop's copies in its last
   iteration shared their operations with the body's - fusing renumbered
   their walks twice; copies own them now, the slice passes take a loop
   once wherever sections share it, the step back is the specializer's
   (an address computation after the loop). The tiles' loops fuse (one
   over every tile's rows, one over their columns).
3. **Z3** a `ztrans` case sized in tiles - done (ukrgen 0224): every SME
   packm config, m: 1..4 tiles (za0-za3), ahead of any scatter case. The
   Apple-safe config (sme/fopa_bc_vindex) declares sme-FA64 off and has no
   scatter case left; LX2's (smesve/fopa_fma_split) declares FA64 on - a
   feature set explicitly (sme-F64F64) had left it off, its scatter cases
   refused since the state check (0215). Panels not of whole tiles: Z4.
4. **Z5** FA64 declared; SME configs without it on the ZA transpose.
5. **Z4** partial tiles - tile + reference and tile + overlap done (ukrgen
   0226): a ZA case taking P's leading dimension (zblock) packs whole
   tiles in blocks; the rows left a one-tile kernel ending at cdim
   (vec-tail overlap) or the reference; below one tile the reference.
   Tile + mask done (ukrgen 0227): a ZA case with mask: true (P's leading
   dimension) - size N packs N whole tiles and a last one of the rows left,
   its row loop counted tail(m), its column stores under whilelo's mask -
   any cdim up to (N+1) tiles in one call, below a tile too (ztail in the
   SME configs, 0..7 tiles of doubles, 0..3 of singles; tried first).
6. **Z6** kappa 1: rows straight into horizontal slices (`ld1d
   {za0h.d[w12, i]}`), no vector, no `mova` - with the kappa copy cases.

## Processor state as dependencies

Done so far: asmgen's signatures declare state (asmgen 0095:
state_requires - name -> condition, "vlen": "!=None", "sm": "==1" -
and state_writes - name -> value, "vlen": "avl" or "max", "sm": "1";
RVV's vector forms and vsetvli, SME's tiles, its gathers and scatters
without FA64; the setups' state). ukrgen's operations read and write the
state their signatures do (reads_state, writes_state: ukrgen 0214), and
both dependency analyses order them by it like registers; distance specs
`RAW:state::::N`. Then (ukrgen 0215): lsc_state, an operation setting
state, emitted through the signature writing it; every access's
requirements checked against the state the setup and lsc_states leave,
its signatures pruned to those they hold for, a kernel refused where none
does - FA64 enforced so (Z5's part: streaming scatters refused where a
config says `sme-FA64: 'off'`); the vector length route an IR of
lsc_states around each last-vector access, the schedulers keeping every
other vector operation out. Switches merged (ukrgen 0216): a column's
last-vector chain - load, multiply, store - one short region where its
registers are its own and its load not preloaded (tailmask); after
scheduling, adjacent regions one where nothing between reads the length
(merge_switches: a pipelined loop's last-vector store and the next
column's load). The state check runs at the end of ISA specialization
(ukrgen 0221), with the forms it decides; merge_switches at emission,
after scheduling. RVV's element type switches lsc_states from the
specializer (ukrgen 0222): each section beginning and ending in the
setup's type, a transformation whose signatures disagree left to the
emitter. The masked tails' mask an lsc_state (ukrgen 0223): set
first in the first block's prologue, read by the last-vector accesses as
state; the emitter writes it through the ISA's MASKAVL form. smstart and smstop
lsc_states (ukrgen 0238, asmgen 0098): the program's entry and exit - once
before every path, once after them - switch the ISA's engine (asmgen's
isa_setup().engine(): SME's streaming mode and ZA) on and off, written
through set's ENGINE forms, the setup's own switches left out; the state
checked from the setup's without its switch, every section beginning and
ending with the entry's. The same instructions in the same places.
--assume-state (ukrgen 0239, asmgen 0099): the state the caller guarantees
around the kernel - sm=1 za=1, BLIS switching streaming mode around its
loops: the check starts from it and the kernel leaves it as it found it; an
engine it covers switched nowhere (no entry or exit, the setup's own switch
left out), its clobbers not the kernel's (no saves of d8-d15). SME's
get_simd_size() reads the streaming vector length with rdsvl, in either
mode - no switch to undo the caller's (asmgen 0099). Where BLIS switches it
(*_ker_var2.c's loops, bli_family_<config>.h) is open.
The check inside loops (ukrgen 0242): a loop's block walked where the loop
is, ending in the state it began with (its iterations alike) - the tiles'
accesses in slice loops, a loop's scatters, checked at last; moves and
transformations checked too (a move's forms pruned as an access's). No
kernel refused or changed by it.

The suggestion as it stood:

The vector length route (tailmask route vl, 0211) brackets each access
with its own `vsetvli` pair because the schedulers can't see vl: nothing
else may run between. Modelled, the state would schedule like a register:

- **lsc_state**: an operation that reads and writes state named by a
  string ("vlen", ...) - a `vsetvli` a write of "vlen".
- **lsc_operation.reads_state, writes_state**: the states an operation
  reads and writes, filled in by ukrgen from what isaquirks says each ISA's
  state is and which operations use it implicitly (RVV: every vector
  operation reads "vlen"; SME: streaming mode, ZA).
- **The schedulers** treat states as registers - RAW, WAR, WAW between
  readers and writers - so a short-vl section can be scheduled, merged or
  hoisted rather than bracketed per access.
- **Distance specs** for state: `RAW:state::::N` (the register class field
  meaningless there - or an instruction type, "sta").

Checked (ukrgen 0246): every split kernel the config builds - 12 doubles
(MR VL+1 .. 2VL+6, NR 2VL, 4VL), 7 singles - right against the reference
at SVL 256 and 512; their A panels (cdim N·VL + M) packed by generated
cases either way round - column-major A by vec (the rows left by an
overlapping call), row-major by ztail1, ztail2 - only a k remainder's
partial chunk the reference's. The split mirrored, smesve/fopa_fma_split_n:
outer products for NR's first part (ZA tiles of columns), FMAs for the rest
with their vectors along m (tileop-vectorize: m) and C column-major - NR
N·VL + M, MR 2VL or 4VL; 12 doubles and 7 singles, right the same way. 
2,4,4 (4,2,4 mirrored) fits (ukrgen 0247): its FMA part's 16 accumulators
live through the ZA part's epilogue - one loop over every tile's slices
(fuse_slices), unrolled into copies sharing their registers (2 doubles, 4
singles). cluster pulls each tile's chains together inside the loop too -
copy after copy, a tile's before the next's (a copy's load waits on the one
before's reads); the scheduler spreads the loop's body within the registers
the block leaves it (its budget less what is live across the loop, the
accumulators: 14), apart as far as they allow; the emitter frees a
temporary after its last use in an iteration (one register set) - the next
tile renames into it. Built and right; only 2,6,4 (32 accumulators) left out.

## Related: the vector length the caller chooses (RVV)

On some hardware a vector length other than the most there is performs
best - a multiple of 40 elements: 240 doubles of 256 on a 16384-bit
machine. BLIS's context computes it (`bli_vlen_utils.c`), the kernel's
`vsetvli` takes it in a register. asmgen's RVV setup takes a caller's
aliased `avl` register (asmgen 0083). Still to come: a parameter for it
in the flow, the BLIS injector passing the context's length, and
`vsetvli` with the aliased avl instead of zero outside the microkernel
(not `csrr vlenb`) where the length is read.

## kappa == 1 as a branch; load, kappamul, store; packm presets

Every packm kernel multiplies by kappa, BLIS's packing mostly passes 1.
The plan, agreed: the copy a branch of the pack composition, and the
tileops from presets, as gemm's.

1. **A LOAD STO kind**, mirroring STORE through the solver, model and
   checks: a load names the components it fills and maps each from its
   memory (as a store maps a component to its memory - gemm's C), its
   forms the same data movement resolutions (X.VEC:direct, strided, a
   gather, Y.TILE:slices_row). Done before it (0228): a branch's cases may
   loop - the loop order each index once, each case's loop its counters.
2. **The pack composition**, branched:
   ```text
   case kappa == 1:  load (Y <- X's memory) ; store Y
   otherwise:        load (X <- X's memory) ; kappamul (Y = kappa*X) ; store Y
   ```
   The copy loads into Y's registers, so the store is the same in both;
   a ZA case's copy loads A's rows straight into its horizontal slices
   (ld1d {za0h.d[...]}) - no vectors, no mova (Z6).
3. **packm presets** (flow/presets/packm_*.yaml), as gemm's:
   - `variants` by the case's vectorization - `m` (vectors along cdim:
     {i=m, n=1}) or `n` (along the panel: {m=1, i=n});
   - `alternatives` the solver tries where the layouts decide - X's load
     (`$XL`: direct, strided), Y's store (`$YS`: direct, strided);
   - **the trans store method a variant key** - `store: strided`,
     `shuffle`, `scatter`, `slices_col` (ZA) - griddable: a family's or a
     case's key, a sweep grid's key (`store: [shuffle, scatter]`);
   - tileops `load` (X.VEC:$XL), `copyload` (Y.VEC:$XL - the kappa == 1
     case), `kappamul` (fmul(X.VEC, kappa.VEC:bc_load, Y.VEC){$K}),
     `store` (Y.VEC:$YS or the method); siblings by the ISA's kappa form:
     packm_bc (broadcast), packm_vf (RVV's vector-scalar:
     kappa.FP:use_scalar), packm_za (Y.TILE:slices_row, slices_col).
   A case: `preset: packm_bc`, `vectorize: n`, `store: shuffle`; explicit
   tileops still override.
   Done (ukrgen 0230), for today's tileops (pack, store): packm_bc, packm_vf,
   packm_za; their alternatives mapped to components (components: {XL: X,
   YS: Y}) - direct only where that memory is contiguous along the
   vectors; a forced option names an explicit resolution (shuffle).
4. **Migrate every ukrconfig packm file** - done (0230): 80 cases, every
   case's kernel byte-identical before and after. When the load STO comes,
   the presets change, not the files. To the presets (scripted: each
   case's pack-tileop, store-tileop to preset, vectorize, store), the
   config test proving each still loads and builds its kernels.
5. **Tests**: every packm dispatch test with kappa 1 and 2 (the harness's
   KAPPA), both paths, every ISA; ZA's copy path.

The load carries its own tiling (decided): `load: X.VEC:$XL{$K}` - a
data movement STO with a tiling, as a compute STO's operand; the copy's
store takes its shape from the load as any store from its producer.

**An identity (copy) STO - in reserve.** A third way: a tileop that is
only the tiling, load and store deriving from it. For a plain copy it
restates the load's tiling (vec, gather; trans, whose transpose is its
store resolution's - strided, shuffle, scatter; ZA, rows loaded into
slices, columns stored). It pays where the copy changes how data sits in
registers between load and store: an in-register transpose as a step of
its own - vectors along n in, along m out - the solver weighing it
against the store methods (today shufflenet rewrites a store into its
network); a type conversion packing (mixed precision) is a computation,
a compute STO. Worth adding if transposes move from the store
resolutions into the STO graph.

**Decided: the copy is an identity compute STO, not a LOAD kind.** A
compute STO's candidates, tilings, resolutions and IR come from the
operation search matching its expression (osb.find_hw_implementations) and
the builder; a LOAD kind would duplicate both. The kappa == 1 path is
`copy (Y = X) ; store`, the copy's input resolution its load
(X.VEC:direct; X.TILE:slices_row on ZA - rows straight into slices).
Needed: a hardware AST for a plain move, MOVE(dst, src) (support/op.py's
ast_op_map has add, mul, fma, fdota, fopa, mma - MOVE(Y, X) matched none);
its IR a register move (lsc_move) a vector; a pass renaming Y's registers
to X's (copy propagation) so the copy emits nothing but its load - a move
a vector until then.

Done (ukrgen 0233), the matching: two plain move shapes, each a step of its
own, never of a chain (inside one a move only copied a temporary - gemm's mm
had 12 such chains). MOVE(bdreg[i], adreg[i]) is asmgen's move, its plain
copies only - not its permutes, lane moves, broadcasts, rotations, shifts
(a shape's signatures selected from its operation's: ast_sigs).
MOVE(bdreg[i,j], adreg[i,j]) is a tile's identity: no instruction does it
(SME has none from a tile to another), its signatures ukrgen's - the copy's
tile is to be renamed to its source's, as a tile's load is a virtual one
expanded into slices. The slice resolutions also for a tile operand's
tf.NONE. MOVE(Y, X)'s candidates, named for asmgen's operation:
`move(X.VEC:direct, Y.VEC){i=m, n=1}` and `{m=1, i=n}` on every ISA; on SME
also `move(X.TILE:slices_row, Y.TILE){i=m, j=n}` - rows straight into a
tile's slices (Z6) - and `slices_col`, and the vector copies into slices.

Done (ukrgen 0235), the copy in the kernels: its IR an lsc_move through the
move's plain copies, tagged copy_sto (for copy propagation; unroll_loops' copy property is its unrolled copies); a tile's copy
refused until then. The composition: copy, then the branch -
case(when={"kappa": 1}) copy and store, the default multiply and store.
packm_bc, packm_vf: copy: move(X.VEC:$XL, Y.VEC){$K}; packm_za the vector
copy into slices, move(X.VEC:direct, Y.TILE:>slice_vec_row){$K} - a mova -
until copy propagation gives a tile its source's (X.TILE:slices_row then).
The branch the whole kernel needed: the masks set at each path's start, the
state check alike (first_blocks); loop_unit and the subtiling listing over
every block (all_blocks); the emitter's once-allocated registers (a
clobbered mask - AVX2's gathers -, a tail's mask) each case's own. Every
packm dispatch test runs kappa 1 and 2; SVE's singles' and halves' copies
need asmgen 0097.

Done (ukrgen 0236), copy propagation: irmod copyprop (vectors; default on, after
shufflenet and structfuse) renames a copy's destination's reads to its
source and drops the move - the builder's lsc_moves tagged copy only, no
other move (lane moves, broadcasts, slices' extracts and inserts, permutes);
renamed only while the reads read the same values (its source not written
before the destination's last read, the destination not read before the
copy - an earlier iteration's - a loop not both, no group's register),
kept otherwise. Tiles' copies copyprop_tiles' - required, no list of
modifications leaving it out - a tile's kept an error. After shufflenet: it knows a
transpose's rows by the copy's registers. A loop's block taken as one of its
iterations (ZA's slice loops: load, copy, insert a row), its destination
not read after the loop. kappa 1 is a load and a store; packm_za's a load
and a mova a row (the vector copy into slices, renamed).
Z6's tile identity, move(X.TILE:slices_row, Y.TILE){i=m, j=n} - rows
straight into slices, no mova - waits on streamed tiles: X loaded into
tiles in a preloaded loop over n walks wrong (its tail rewinds X's pointer
a vector length and advances it one an iteration - no net advance - P's
alike; the main loop advances X 16 vector lengths for its 8 tiles).
copyprop_tiles is ready for it.

Done (ukrgen 0237), Z6: a slice loop's move to its home (the first slice
of its first walk) walked like an access's - the section moves the register
back at its end, a loop's next iteration and its tail starting where it did.
A streamed tile's pointer drifted without it: X's, loaded into tiles in the
preloaded loop over n, 16 vector lengths an iteration of 8 tiles, its tail
rewinding one a tile (no gemm kernel changed). packm_za's copy the tile
identity - kappa 1 loads A's rows straight into the tiles' horizontal
slices, stores their vertical ones: no vector, no mova.

Done (ukrgen 0240), copies elided: a copy whose source is loaded for it
alone (a plain load, not held, not read again) loads it straight into the
destination's register - no move, nothing for copyprop. copyprop renamed
neither structfuse's groups (RVV's trans: segment stores need the rows in
the group) nor copies whose rotating source registers were rewritten before
the store (vec3v-7v) - the tuner's count, k3-x100's FP64: 1158 and 52
moves; now none on k1, k3-a100, k3-x100. NEON's trans (shufflenet's
networks) lost theirs too. copyprop, copyprop_tiles keep the rest: a
source held or read again, loaded lane by lane, a tile's.

Fixed (ukrgen 0245), tile + mask's last tiles: tailmask took the tail tile
for the highest tile register - right while an iteration holds one chunk of
columns. ztail's loops over n hold several (ztail0 eight, ztail1 four,
ztail2 three, ztail3 two), each but the last packing a whole tile past cdim
and storing its columns unmasked, spilling into the next column of P; a
remainder section found no tile to mask. Every chunk's last tile now, by
its place along m. And the masks set in the program's entry, not the first
block's prologue - a loop running no iteration skipped it, its remainder
storing under an unset mask: the engine's switch, the setup's all-true
predicate, then the masks. Every ztail kernel at 2, 8 and 9 chunks, tails
of 1 and VL - 1 rows, SVL 256 and 512: right (test_packm_ztail_chunks).

**Later: a transpose operation**, not the identity: input vectors along n,
output along m - its implementation the permute network shufflenet
computes (transpose_network), its scratch registers the emitter's. Load,
transpose, (kappa)mul, a direct store: the solver weighing it against the
store methods, the network scheduled as operations. Fixed-length ISAs only
(a run-time vector length transposes through ZA).

## Order

1. asmgen A1 (STRUCT is interleaving), A3 (first-M masks), A2 (SVE
   structure addressing) - done (asmgen 0084-0086).
2. ukrgen `structfuse` - done (ukrgen 0184); its splits (RVV's strided
   segments: A7, the `struct-split` key), the family keys (splits, the
   dispatch's implementations, masks) and cases; the `vec` route under a
   predicate (cdim = n·VL + M) beside it.
3. asmgen A4 (permutes); ukrgen `shufflenet` (AVX-512 8x8 and 24, AVX2
   4x4, NEON) and AVX2's trans case.
4. kappa == 1 branch, load/kappamul/store, packm presets (above), the configs
   migrated; then ukrgen `za_transpose` - its steps above (Z1-Z6), FA64 declared - then the
   split kernels' cdim (U6).
5. ukropt's measurements; strategies named by tileops (U4).
