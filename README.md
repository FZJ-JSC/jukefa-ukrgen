# ukrgen - compute kernel generators based on asmgen

ukrgen generates BLAS microkernels - `{s,d}gemm` and `{s,d}packm` - for
AVX2, AVX-512, NEON, SVE, SME (and SME with SVE, the microtile split between
them) and RVV, from tile operations and a few parameters, and schedules
them. `blisgen` builds a complete BLIS configuration from families of such
kernels, the microkernel chosen at run time; `ukrgen` generates a single
kernel, to inspect its code or debug the generator.

## Installation

```
git clone https://github.com/FZJ-JSC/jukefa-ukrgen
cd jukefa-ukrgen
pip install . "asmgen @ git+https://github.com/FZJ-JSC/jukefa-asmgen"
```

Python 3.10 or newer, asmgen 0.6 or newer. Cross-compilers and qemu are
needed only to build and test kernels for another ISA.

## blisgen

Generates a BLIS configuration from kernel families: one YAML file per data
type and kernel type. `ukrconfig/<isa>/<config>/` has configurations for
every ISA - [docs/UKRCONFIG.md](docs/UKRCONFIG.md) lists them and describes
their keys and tuning.

```bash
# patch a BLIS tree with SVE kernels
blisgen --sgemm-config ukrconfig/sve/fma_bc_vindex/sgemm.yaml \
        --dgemm-config ukrconfig/sve/fma_bc_vindex/dgemm.yaml \
        --spackm-config ukrconfig/sve/fma_bc_vindex/spackm.yaml \
        --dpackm-config ukrconfig/sve/fma_bc_vindex/dpackm.yaml \
        --from-dir /path/to/blis --out-dir /path/to/blis-ukrgen-sve \
        --author "Your Name"

# configure and build it (here cross-compiling on an x86 machine)
cd /path/to/blis-ukrgen-sve
CC=aarch64-linux-gnu-gcc ./configure -t none ukrgen_sve
make -j$(nproc) && make testsuite-bin

# run BLIS's testsuite under qemu
cd testsuite
qemu-aarch64 -cpu max,sve512=on -L /usr/aarch64-linux-gnu ../test_libblis.x
```

`--from-git` clones BLIS from github.com/flame/blis instead of
`--from-dir`; with neither, blisgen writes the configuration's files alone.
`--config-name` names the configuration (default `ukrgen_<isa>`), `-j`
builds that many kernels at once. Every size of a family the registers hold
is built, and `BLIS_MR_D`, `BLIS_NR_D` (`_S` for singles) choose among them
at run time - see [docs/UKRCONFIG.md](docs/UKRCONFIG.md#at-run-time).

## ukrgen

Generates one kernel from the command line. Its options come in stages,
each appearing once the ones before it are given:
`ukrgen --isa rvv --rvv-LMUL 1 --ukr gemm --help` lists what follows.
Without `--print-asm` ukrgen prints the tile operation chosen for each of
the kernel's steps; `--print-stos`, `--print-ir` and `--print-schedule` show
the stages' work, `--list-tileop-candidates` every tile operation a step
could take, and `--<step>-tileop` overrides a preset's choice.

### Example: a gemm kernel

  - RVV, LMUL 1, FP32 (sgemm)
  - vector-scalar FMA, `vfmacc.vf`: the `gemm_fma_vf` preset, vectors along m
  - 2 vectors by 12 columns, k unrolled 8 times
  - A and B packed (`k:p`), C column-major at a column stride (`n:s`)
  - two address registers each for A and B, taken in turn
  - 13 instructions between a vector register's dependent uses, 3 between
    an address bump and the accesses using it

```
$ ukrgen --isa rvv --rvv-LMUL 1 --ukr gemm \
         --A-data-type FP32 --B-data-type FP32 --AB-data-type FP32 --C-data-type FP32 \
         --A-layout m:c k:p --B-layout n:c k:p --C-layout m:c n:s \
         --tileop-preset gemm_fma_vf --tileop-vectorize m \
         --m 2 --n 12 --k 8 \
         --A-addr-regs 2 --B-addr-regs 2 --A-addr-pattern rotate --B-addr-pattern rotate \
         --distances "RAW:data::::13" "WAW:data::::13" "WAR:data::::13" "RAW:address:greg:::3" \
         --print-asm
// bases: A in a1, B in a2, C in a3, alpha in a4, beta in a5
vsetvli t0, zero, e32, m1, ta, ma
[...]
// block mm, loop over k
// init
vmv.v.i v1,0
[...]
// body
vfmacc.vf v1,f0,v25
vfmacc.vf v2,f1,v25
vfmacc.vf v3,f2,v25
[...]
// case beta==0 and alpha==1
  // block store_ab
[...]
```

Without `--print-asm`, the tile operations the preset chose:

```
--mm-tileop "fma[bdreg:VF](A.VEC:direct, B.FP:use_scalar, AB.VEC){i=m, n=1, k*=1}"
--store_ab-tileop "AB.VEC:direct"
--alphamul-tileop "mul[bdreg:VF](AB.VEC, alpha.FP:use_scalar, C.VEC){i=m, n=1}"
[...]
```

### Example: a packm kernel

  - RVV, LMUL 1, FP64 (dpackm)
  - vectors along cdim: the `packm_vf` preset - a plain copy for kappa 1,
    `vfmul.vf` by kappa otherwise
  - 2 vectors a column (cdim 2 x VL), 4 columns an iteration
  - A (`X`) and the packed panel (`Y`) column-major at a column stride

```
$ ukrgen --isa rvv --rvv-LMUL 1 --ukr pack \
         --X-data-type FP64 --Y-data-type FP64 \
         --X-layout m:c n:s --Y-layout m:c n:s \
         --tileop-preset packm_vf --tileop-vectorize m \
         --m 2 --n 4 --print-asm
// bases: X in a1, Y in a2, kappa in a3
vsetvli t0, zero, e64, m1, ta, ma
[...]
// case kappa==1
  // block copy+store, loop over n
  // prologue
[...]
  vle64.v v1, (a1)
[...]
  vse64.v v1, (a2)
[...]
// case otherwise
  // block pack+store, loop over n
  // init
  fld f0, 0(a3)
[...]
  vfmul.vf v3,v2,f0
[...]
```

## Documentation

  - [docs/UKRCONFIG.md](docs/UKRCONFIG.md): the example configurations,
    building BLIS with them, choosing kernels at run time, tuning
  - [docs/GENERATOR.md](docs/GENERATOR.md): the generator's systems
  - [docs/SCHEDULING.md](docs/SCHEDULING.md): scheduling
  - [docs/BLISGEN_PLAN.md](docs/BLISGEN_PLAN.md),
    [docs/PACKING_PLAN.md](docs/PACKING_PLAN.md): plans and progress


# License

ukrgen is distributed under the terms of both the MIT license and the GNU General Public License v3.0. Users may choose either license, at their option.

All new contributions must be made under both the MIT and GNU General Public License v3.0.

See LICENSE-GPL-3.0, LICENSE-MIT for details.

SPDX-License-Identifier: MIT OR GPL-3.0-or-later
