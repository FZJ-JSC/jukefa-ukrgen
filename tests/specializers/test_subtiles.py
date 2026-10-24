"""
Steps repeating over a register's subtiles - lanes, 128-bit blocks, 256-bit
chunks - built by one loop nest, run against a reference: NEON lanes under
qemu, AVX block lanes (loads, 256-bit inserts, stores) natively
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import tests.specializers.test_signature as t
from tests.specializers.test_native import cpu_has
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage

HERE = os.path.dirname(os.path.abspath(__file__))
STRIDED_A = {"A-layout": ["m:s", "k:c"]}
STRIDED_C = {"C-layout": ["m:s", "n:s"]}


def mm_to(rsln):
    return {"mm-tileop": [f"fma(A.VEC:{rsln}, B.VEC:bc_load, C.VEC){{i=m, n=1, k*=1}}"]}


class test_subtiles(unittest.TestCase):

    def runs(self, isa, params, harness, tile, cc=("gcc",), run=()):
        if not shutil.which(cc[0]) or (run and not shutil.which(run[0])):
            self.skipTest(f"needs {cc[0]}" + (f" and {run[0]}" if run else ""))
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            ctx, res = t.mm(isa=isa, **params)
        finally:
            t.STAGES = saved
        self.assertTrue(res.completed, res.output)
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([*cc, "-O1", os.path.join(HERE, harness), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([*run, exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn(tile, r.stdout)
        self.assertIn(", 0 wrong", r.stdout)
        return ctx

    def test_neon_lanes(self):
        self.runs("neon", {**STRIDED_A, **mm_to("lanes")}, "strided_mm_harness.c", "tile 4 x 2",
                  cc=("aarch64-linux-gnu-gcc", "-static"), run=("qemu-aarch64-static", "-cpu", "max"))

    @unittest.skipUnless(cpu_has("avx2"), "needs an AVX2 CPU")
    def test_avx2_block_lanes(self):
        self.runs("avx256", {**STRIDED_A, **mm_to("block_lanes")}, "strided_mm_harness.c", "tile 8 x 2")
        self.runs("avx256", {**STRIDED_C, "store-tileop": ["C.VEC:block_lanes"]}, "strided_c_harness.c",
                  "tile 8 x 2")

    @unittest.skipUnless(cpu_has("avx512f"), "needs an AVX-512 CPU")
    def test_avx512_block_lanes(self):
        self.runs("avx512", {**STRIDED_A, **mm_to("block_lanes")}, "strided_mm_harness.c", "tile 16 x 2")
        self.runs("avx512", {**STRIDED_A, **mm_to("block_lanes_256")}, "strided_mm_harness.c",
                  "tile 16 x 2")
        self.runs("avx512", {**STRIDED_C, "store-tileop": ["C.VEC:block_lanes"]}, "strided_c_harness.c",
                  "tile 16 x 2")


if __name__ == "__main__":
    unittest.main()
