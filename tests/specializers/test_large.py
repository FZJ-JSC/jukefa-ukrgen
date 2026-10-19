"""
Microkernels at the architected register count, run against a reference:
vector FMAs taking every vector register (8x3v on RVV, 14vx2 and 15vx2 on
NEON, SVE and AVX-512 - 15vx2 all 32 where FP and vector registers share a
file), outer products taking every tile (2vx4v doubles: all 8, 2vx2v
singles: all 4). Data register counts are left to the model, which fits
them beside the accumulators
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from specializers.test_native import cpu_has

HERE = os.path.dirname(os.path.abspath(__file__))
FREE = {"A-data-regs": None, "B-data-regs": None}
FOPA = "fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"


class test_large(unittest.TestCase):

    def runs(self, isa, extra, cc, asflag, runners, tiles, fp32=False):
        if not shutil.which(cc[0]) or any(r and not shutil.which(r[0]) for r in runners):
            self.skipTest(f"needs {cc[0]}")
        params = dict(FREE)
        params.update(extra)
        ctx, res = t.mm(isa=isa, **params)
        self.assertTrue(res.completed, res.output)
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            r = subprocess.run(cc + ([asflag] if asflag else []) + ["-c", os.path.join(d, "ukr.s"),
                                                                    "-o", os.path.join(d, "ukr.o")],
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run(cc + ["-O1", "-DLDC=263"] + (["-DWT=float"] if fp32 else []) +
                               [os.path.join(HERE, "mm_harness.c"), os.path.join(d, "ukr.o"),
                                "-o", os.path.join(d, "run"), "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for runner, tile in zip(runners, tiles):
                r = subprocess.run(runner + [os.path.join(d, "run")], capture_output=True, text=True,
                                   timeout=120)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)

    def test_rvv_8x3v(self):
        self.runs("rvv", {"rvv-LMUL": "1", "m": "8", "n": "3", "store-tileop": ["C.VEC:strided"],
                          "mm-tileop": ["fma(A.VEC:bc_load, B.VEC:direct, C.VEC){m=1, i=n, k*=1}"]},
                  ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"], None,
                  [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                  ["tile 8 x 6", "tile 8 x 12"])

    def test_neon_14vx2(self):
        self.runs("neon", {"m": "14", "n": "2"}, ["aarch64-linux-gnu-gcc", "-static"], None,
                  [["qemu-aarch64-static", "-cpu", "max"]], ["tile 28 x 2"])

    def test_neon_15vx2(self):
        self.runs("neon", {"m": "15", "n": "2"}, ["aarch64-linux-gnu-gcc", "-static"], None,
                  [["qemu-aarch64-static", "-cpu", "max"]], ["tile 30 x 2"])

    def test_sve_14vx2(self):
        self.runs("sve", {"m": "14", "n": "2"}, ["aarch64-linux-gnu-gcc", "-static"],
                  "-Wa,-march=armv8-a+sve",
                  [["qemu-aarch64-static", "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                  ["tile 56 x 2", "tile 112 x 2"])

    def test_sve_15vx2(self):
        self.runs("sve", {"m": "15", "n": "2"}, ["aarch64-linux-gnu-gcc", "-static"],
                  "-Wa,-march=armv8-a+sve",
                  [["qemu-aarch64-static", "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                  ["tile 60 x 2", "tile 120 x 2"])

    @unittest.skipUnless(cpu_has("avx512f"), "needs an AVX-512 CPU")
    def test_avx512_14vx2(self):
        self.runs("avx512", {"m": "14", "n": "2"}, ["gcc"], None, [[]], ["tile 112 x 2"])

    def test_sme_2vx4v_fp64(self):
        # all eight double tiles
        self.runs("sme", {"sme-F64F64": "on", "mm-tileop": [FOPA], "store-tileop": ["C.TILE:slices_col"],
                          "m": "2", "n": "4"},
                  ["aarch64-linux-gnu-gcc", "-static"], "-Wa,-march=armv9-a+sme+sme-f64f64",
                  [["qemu-aarch64-static", "-cpu", f"max,sme=on,sme{v}=on"] for v in (256, 512)],
                  ["tile 8 x 16", "tile 16 x 32"])

    def test_sme_2vx2v_fp32(self):
        # all four single tiles
        self.runs("sme", {"A-data-type": "FP32", "B-data-type": "FP32", "C-data-type": "FP32",
                          "mm-tileop": [FOPA], "store-tileop": ["C.TILE:slices_col"], "m": "2", "n": "2"},
                  ["aarch64-linux-gnu-gcc", "-static"], "-Wa,-march=armv9-a+sme",
                  [["qemu-aarch64-static", "-cpu", f"max,sme=on,sme{v}=on"] for v in (256, 512)],
                  ["tile 16 x 16", "tile 32 x 32"], fp32=True)

    def test_too_many_given(self):
        # data registers given that can't fit beside the accumulators
        from ukrgen.flow.stages.stage import stage_error
        with self.assertRaisesRegex(stage_error, "35 of 32"):
            t.mm(isa="rvv", **{"rvv-LMUL": "1", "m": "8", "n": "3", "store-tileop": ["C.VEC:strided"],
                               "mm-tileop": ["fma(A.VEC:bc_load, B.VEC:direct, C.VEC){m=1, i=n, k*=1}"],
                               "A-data-regs": "8", "B-data-regs": "3"})


if __name__ == "__main__":
    unittest.main()
