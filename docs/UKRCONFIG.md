# Example blisgen configurations (`ukrconfig/`)

`ukrconfig/<isa>/<config>/` holds a BLIS configuration's kernel families, one
file per data type and kernel type:

| file | blisgen option |
|------|----------------|
| `sgemm.yaml` | `--sgemm-config` |
| `dgemm.yaml` | `--dgemm-config` |
| `spackm.yaml` | `--spackm-config` |
| `dpackm.yaml` | `--dpackm-config` |

`ukrconfig/legacy/` keeps the old single-kernel files of the previous
generator; the current blisgen doesn't read them.

## The configurations

| config | ISA | gemm | default (doubles / singles) | packm |
|--------|-----|------|------------------------------|-------|
| `avx2/fma_bc_blocks` | AVX2 | FMA, broadcast operand (`gemm_fma_bc_blocks`); C across vectors by block insert/extract trees | 4x3v | vec |
| `avx512/fma_bc_blocks` | AVX-512 | as above, 32 registers | 8x3v | vec, trans (scatters) |
| `avx512/fma_bc_vindex` | AVX-512 | FMA, broadcast operand (`gemm_fma_bc_vindex`); C across vectors by gathers and scatters | 8x3v | vec, trans (scatters) |
| `neon/fma_bc_lanes` | NEON | FMA, broadcast operand (`gemm_fma_bc_lanes`); C across vectors by lane loads and stores | 8x3v | vec |
| `neon/fma_lane` | NEON | lane FMA, `fmla` by element (`gemm_fma_lane`): the broadcast operand loaded as whole vectors | 4vx4 | vec |
| `rvv/fma_vf` | RVV, LMUL 1 | vector-scalar FMA, `vfmacc.vf` (`gemm_fma_vf`): scalars in FP registers; C across vectors strided | 8x3v | vec, trans (strided) |
| `rvv/fma_vf_m2` | RVV, LMUL 2 | as above, 16 registers of two | 6x2v | vec, trans (strided) |
| `sve/fma_bc_vindex` | SVE | FMA, broadcast operand (`gemm_fma_bc_vindex`); C across vectors by gathers and scatters | 8x3v | vec, trans (scatters) |
| `sve/fma_blocklane` | SVE | block-lane FMA, scalars broadcast by 128-bit block (`gemm_fma_blocklane_vindex`) | 2vx8 | vec, trans (scatters) |
| `sme/fopa_bc_vindex` | SME | outer products into tiles (`gemm_fopa_bc_vindex`), the epilogue slice by slice | 2vx4v / 2vx2v | vec, trans (scatters) |
| `smesve/fopa_fma_split` | SME | the microtile split along m: outer products for the first part, streaming FMAs for the rest, sized by `split-ratios: 1..2:1..3` | 2vx4v+2x4v / 2vx2v+2x2v | vec, trans (scatters) |

Every gemm file has two families where the ISA has two orientations: `vn`
(vectors along n, A broadcast) and `vm` (vectors along m, B broadcast), both
with column-major C - `vn` reaches C across its vectors, the stride paths
the configuration is named for. Sizes are in the family's units: `8x3v` is
8 rows by 3 vectors, `2vx8` 2 vectors by 8 columns. Every size of a family
the registers hold is built; the others are reported in
`config/<name>/blisgen_report.txt`.

## Building BLIS

```sh
blisgen --sgemm-config ukrconfig/sve/fma_bc_vindex/sgemm.yaml \
        --dgemm-config ukrconfig/sve/fma_bc_vindex/dgemm.yaml \
        --spackm-config ukrconfig/sve/fma_bc_vindex/spackm.yaml \
        --dpackm-config ukrconfig/sve/fma_bc_vindex/dpackm.yaml \
        --from-dir <blis> --out-dir <blis-out> --author "<name>" \
        [--config-name ukrgen_sve] [--stack-buf-size BYTES] [--parent-config-name <config>]
cd <blis-out> && ./configure -t none ukrgen_sve && make -j && make testsuite-bin
```

Without `--from-dir`/`--from-git` blisgen writes the configuration's files
alone under `--out-dir`. The patched tree registers the configuration and
carries [PR 960](https://github.com/flame/blis/pull/960).

## At run time

- `BLIS_MR_D`, `BLIS_NR_D` (and `_S`), in elements, choose the gemm
  microkernel among those built - the vector length read at run time where
  sizes are in vectors. Unset, or a size not built: the family's default.
- `BLIS_MR_IN_MC_D`, `BLIS_NR_IN_NC_D`, `BLIS_KC_D` (PR 960) override the
  cache blocksizes, relative to the chosen kernel's MR and NR.
- A quick check: the testsuite with `input.general` reduced to data types
  `sd`, storage `rcg` and two sizes - one a multiple of the kernels' MR and
  NR, one not - and `input.operations` with `2` for the gemm microkernel and
  level-3 gemm.

## Writing a family

A gemm family names a tile operation preset (`preset:`, a shorthand from
`src/ukrgen/flow/presets/` or a YAML file of the same form) and the index
its vectors run along (`vectorize:`), or gives every `--<sto>-tileop` in
`params:`. Keys: `m`, `n` (sizes: `1..4`, lists), `default`, `unroll` (along
k), `loop-order`, `resolve-order`, `schedule`, and per component
`max-data-regs`, `max-preload`, `max-addr-regs`, `addr-pattern`. A split
family has `split:`, `parts:` (each with its preset and sizes along the
split index) and optionally `split-ratios:`. A packm family lists `cases:`
of `kind: vec` (cdim in vectors, A contiguous along it) and `kind: trans`
(cdim in elements, A contiguous along the panel), each with its sizes and
parameters. `docs/BLISGEN_PLAN.md` has the details of each.
