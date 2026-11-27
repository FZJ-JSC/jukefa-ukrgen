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
#: kappa scales. n counts vector-length blocks of columns, as the gemm's k
#: counts vector-length blocks of elements - the harness calibrates the panel
#: from X's first column, then checks every element, the extent and the tail
HARNESS = r"""#include <stdio.h>
typedef double w;
void ukr(long n, const w* X, w* Y, const w* kappa, long sXm);
#define LDX 64
#define MMAX 64
static w X[LDX * 512], Yb[MMAX * 512];
int main(void) {
    w *Y = Yb + 16;
    /* the panel's rows, from X's first column: the first -1 is where one
       column's panel ends (mr); n counts vector-length blocks of columns, so
       VL = mr / TILES */
    for (int i = 0; i < LDX * 512; i++) X[i] = -1;
    for (int m = 0; m < MMAX; m++) X[m * LDX] = m + 1;
    for (int i = 0; i < MMAX * 512; i++) Yb[i] = -7;
    w one = 1;
    ukr(1, X, Y, &one, LDX * sizeof(w));
    int mr = 0;
    while (mr < MMAX && Y[mr] == mr + 1) mr++;
    long VL = mr / TILES;
    printf("panel %d, VL %ld\n", mr, VL);
    if (mr == 0 || VL == 0) { printf("no panel\n"); return 1; }
    int bad = 0, runs = 0;
    w kappas[] = {1.0, -2.5};
    for (long blocks = 0; blocks <= 5; blocks++) for (int ki = 0; ki < 2; ki++) {
        long cols = blocks * VL;
        for (int i = 0; i < LDX * 512; i++) X[i] = (w)((i * 7) % 13) - 6;
        for (int i = 0; i < MMAX * 512; i++) Yb[i] = -7;
        ukr(blocks, X, Y, &kappas[ki], LDX * sizeof(w));
        runs++;
        for (long c = 0; c < cols; c++) for (int m = 0; m < mr; m++)
            if (Y[m + c * mr] != kappas[ki] * X[m * LDX + c]) {
                if (bad < 5) printf("blocks=%ld Y[%d,%ld]=%g want %g\n", blocks, m, c,
                                    Y[m + c * mr], kappas[ki] * X[m * LDX + c]);
                bad++;
            }
        for (int i = -16; i < 0; i++) if (Y[i] != -7) bad++;
        /* the panel exactly as long as the columns packed, no further */
        long extent = cols * mr;
        for (long i = extent; i < extent + 32; i++)
            if (Y[i] != -7) { if (bad < 5) printf("written past Y[%ld]\n", i); bad++; break; }
        for (long i = extent - 1; i >= 0 && i > extent - 32; i--)
            if (Y[i] == -7) { if (bad < 5) printf("short of Y[%ld]\n", i); bad++; break; }
    }
    printf("%d runs, %d bad\n", runs, bad);
    return bad != 0;
}
"""


def pack_kernels(case: str, sizes: tuple) -> tuple:
    """
    The SME dpackm family's kernels for one case and its sizes
    :param case: the case's kind (ztrans, ztail)
    :param sizes: the tiles of cdim to build (1..8)
    :return: (the kernels built, (data type, (case, size), reason) for each it
             can't build)
    """
    cfg = gk._config("sme/fopa_bc_vindex/dpackm.yaml")
    fam = copy.deepcopy(next(f for f in cfg.families if f.name == "pk"))
    fam.cases = [(kind, [m for m in ms if m in sizes], params)
                 for kind, ms, params in fam.cases if kind == case]
    return families.build_packm(cfg.isa, cfg.name, fam)


def run_kernel(kernel, run: tuple, tiles: int) -> str:
    """
    One kernel assembled as SME, linked with the packing harness and run
    :param kernel: the kernel built
    :param run: the emulator and its flags
    :param tiles: the tiles of cdim the kernel packs (its case's m)
    :return: what the harness printed
    """
    cc = "aarch64-linux-gnu-gcc"
    # the emitted symbol carries the emitter's suffix (.global ..._asm)
    entry = f"{kernel.symbol}_asm"
    with tempfile.TemporaryDirectory() as d:
        harness = os.path.join(d, "harness.c")
        asm = os.path.join(d, "ukr.s")
        obj = os.path.join(d, "ukr.o")
        exe = os.path.join(d, "run")
        with open(harness, "w") as f:
            f.write(HARNESS.replace("ukr(", f"{entry}(").replace("TILES", str(tiles)))
        with open(asm, "w") as f:
            f.write(asm_source(kernel))
        # the kernel assembled as SME, the harness as plain C - the order the
        # gemm tests assemble and link in (a C main built for SME segfaults)
        built = subprocess.run([cc, "-c", "-Wa,-march=armv9-a+sme+sme-f64f64",
                                asm, "-o", obj], capture_output=True, text=True)
        if built.returncode != 0:
            raise AssertionError(built.stderr[-800:])
        built = subprocess.run([cc, "-static", "-O1", harness, obj, "-o", exe],
                               capture_output=True, text=True)
        if built.returncode != 0:
            raise AssertionError(built.stderr[-800:])
        out = subprocess.run([*run, exe], capture_output=True, text=True, timeout=300)
    return out.stdout + out.stderr


class test_sme_pack(unittest.TestCase):
    """The SME packing kernels a panel at a time, under qemu"""

    def check(self, case: str, sizes: tuple, tiles: int, svl: int) -> str:
        """
        One case's kernels under qemu at one streaming vector length
        :param case: the case's kind
        :param sizes: the tiles of cdim to build
        :param tiles: the tiles of cdim the kernel packs (its case's m)
        :param svl: the streaming vector length, in bits
        :return: what the harness printed
        """
        ok, skipped = pack_kernels(case, sizes)
        self.assertTrue(ok, [s[2] for s in skipped][:3])
        run = ("qemu-aarch64-static", "-cpu", f"max,sme=on,sme{svl}=on")
        out = ""
        for k in ok:
            with self.subTest(symbol=k.symbol):
                out = run_kernel(k, run, tiles=tiles)
                self.assertIn(", 0 bad", out, out[-400:])
        return out

    @unittest.skipUnless(shutil.which("aarch64-linux-gnu-gcc") and shutil.which("qemu-aarch64-static"),
                         "needs aarch64-linux-gnu-gcc and qemu-aarch64-static")
    def test_ztrans_packs_a_panel(self):
        # a panel's rows scaled into a tile's slices, transposed through ZA and
        # stored as P's columns: two tiles of cdim, n counting vector-length
        # blocks of columns - the packed panel exactly as long as the columns
        # packed, every element scaled by kappa, nothing past it
        for svl, panel in ((256, 8), (512, 16)):
            with self.subTest(svl=svl):
                out = self.check("ztrans", (2,), tiles=2, svl=svl)
                self.assertIn(f"panel {panel}", out)
                self.assertIn(", 0 bad", out)

    @unittest.skip("ztail: the masked rows, and the columns left of a vector-length "
                   "block (n = k*VL + j, the combined SME+SVE kernels' cdim) - its "
                   "own reference and the n-lane mask, next")
    def test_ztail_packs_a_masked_panel(self):
        # the rows left under a mask: cdim past the tile
        self.check("ztail", (2,), tiles=2, svl=512)


if __name__ == "__main__":
    unittest.main()
