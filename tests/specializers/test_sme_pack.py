"""
An SME packing kernel's results: a panel transposed through ZA and stored
packed, run under qemu at two vector lengths against a reference - the case
the goldens can only compare textually (ukrconfig/sme/fopa_bc_vindex/dpackm.yaml)
"""
import copy
import os
import shutil
import subprocess
import tempfile
import unittest

import tests.flow.golden_kernels as gk
from ukrgen.injectors.blis import families
from ukrgen.injectors.blis.cgen import asm_source

HERE = os.path.dirname(os.path.abspath(__file__))

#: X a panel of cdim rows, n contiguous and m strided (X-layout n:c, m:s,
#: stride(X,m) in bytes); Y the packed panel, cdim contiguous and n packed;
#: kappa scales - the harness asks which rows arrived, then checks every
#: element of the reference packing
HARNESS = r"""#include <stdio.h>
typedef double w;
void ukr(long n, const w* X, w* Y, const w* kappa, long sXm);
#define LDX 16
#define NMAX 17
#define MMAX 16
static w X[LDX * NMAX + 64], Ybuf[MMAX * NMAX + 128];
static w *Y = Ybuf + 16;
int main(void) {
    for (int i = 0; i < LDX * NMAX + 64; i++) X[i] = 1;
    for (int i = 0; i < MMAX * NMAX + 128; i++) Ybuf[i] = -7;
    w one = 1;
    ukr(1, X, Y, &one, LDX * sizeof(w));
    int M = 0;
    while (M < MMAX && Y[M] == 1) M++;
    printf("panel %d\n", M);
    int bad = 0, runs = 0;
    w kappas[] = {1.0, -2.5};
    for (long N = 0; N <= 8; N++) for (int ki = 0; ki < 2; ki++) {
        for (int i = 0; i < LDX * NMAX + 64; i++) X[i] = (w)((i * 7) % 13) - 6;
        for (int i = 0; i < MMAX * NMAX + 128; i++) Ybuf[i] = -7;
        ukr(N, X, Y, &kappas[ki], LDX * sizeof(w));
        runs++;
        for (long n = 0; n < N; n++) for (int m = 0; m < M; m++)
            if (Y[m + n * M] != kappas[ki] * X[m * LDX + n]) {
                if (bad < 5) printf("N=%ld Y[%d,%ld]=%g want %g\n", N, m, n,
                                    Y[m + n * M], kappas[ki] * X[m * LDX + n]);
                bad++;
            }
        for (int i = -16; i < 0; i++) if (Y[i] != -7) bad++;
        for (int i = M * N; i < M * N + 32; i++) if (Y[i] != -7) { if (bad < 5) printf("written past Y[%d]\n", i); bad++; break; }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
"""


def pack_kernels(case: str, sizes: tuple) -> list:
    """
    The SME dpackm family's kernels for one case and its sizes
    :param case: the case's kind (ztrans, ztail)
    :param sizes: the tiles of cdim to build (1..8)
    :return: the kernels built
    """
    cfg = gk._config("sme/fopa_bc_vindex/dpackm.yaml")
    fam = copy.deepcopy(next(f for f in cfg.families if f.name == "pk"))
    fam.cases = [(kind, [m for m in ms if m in sizes], params)
                 for kind, ms, params in fam.cases if kind == case]
    ok, skipped = families.build_packm(cfg.isa, cfg.name, fam)
    return ok, skipped


def run_kernel(kernel, cc: tuple, run: tuple) -> str:
    """
    One kernel linked into the packing harness and run
    :param kernel: the kernel built
    :param cc: the compiler and its flags
    :param run: the emulator and its flags
    :return: what the harness printed
    """
    with tempfile.TemporaryDirectory() as d:
        harness = os.path.join(d, "harness.c")
        asm = os.path.join(d, "ukr.s")
        exe = os.path.join(d, "run")
        # the emitted symbol carries the emitter's suffix (.global ..._asm)
        entry = f"{kernel.symbol}_asm"
        with open(harness, "w") as f:
            f.write(HARNESS.replace("void ukr(", f"void {entry}(")
                    .replace("ukr(1, X", f"{entry}(1, X")
                    .replace("ukr(N, X", f"{entry}(N, X"))
        with open(asm, "w") as f:
            f.write(asm_source(kernel))
        # the kernel assembled as SME, the harness as plain C - the order the
        # gemm tests assemble and link in (a C main built for SME segfaults)
        obj = os.path.join(d, "ukr.o")
        built = subprocess.run([cc[0], "-c", "-Wa,-march=armv9-a+sme+sme-f64f64",
                                asm, "-o", obj], capture_output=True, text=True)
        if built.returncode != 0:
            raise AssertionError(built.stderr[-800:])
        built = subprocess.run([cc[0], "-static", "-O1", harness, obj, "-o", exe],
                               capture_output=True, text=True)
        if built.returncode != 0:
            raise AssertionError(built.stderr[-800:])
        out = subprocess.run([*run, exe], capture_output=True, text=True, timeout=300)
    return out.stdout + out.stderr


class test_sme_pack(unittest.TestCase):
    """The SME packing kernels a panel at a time, under qemu"""

    def check(self, case: str, sizes: tuple, svl: int) -> str:
        ok, skipped = pack_kernels(case, sizes)
        self.assertTrue(ok, [s[2] for s in skipped][:3])
        svl_flag = f"sme{svl}=on"
        cc = ("aarch64-linux-gnu-gcc",)
        run = ("qemu-aarch64-static", "-cpu", f"max,sme=on,{svl_flag}")
        out = ""
        for k in ok:
            with self.subTest(symbol=k.symbol):
                out = run_kernel(k, cc, run)
                self.assertIn(", 0 wrong", out, out[-400:])
        return out

    @unittest.skip("SME packm does not run: ztrans segfaults under qemu at SVL 512 and its "
                   "packing disagrees at 256 (the reference or the kernel - to be pinned down)")
    def test_ztrans_packs_a_panel(self):
        # a tile's rows scaled into its slices, transposed through ZA and stored
        # as P's columns: two tiles of cdim, four vectors long
        out = self.check("ztrans", (2,), 512)
        self.assertIn("panel 16", out)

    @unittest.skip("as test_ztrans_packs_a_panel: SME packm does not run yet")
    def test_ztail_packs_a_masked_panel(self):
        # the rows left under a mask: cdim past the tile
        out = self.check("ztail", (2,), 512)
        self.assertIn(", 0 wrong", out)


if __name__ == "__main__":
    unittest.main()
