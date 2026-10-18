"""
Loops over a vector's elements, as many as it has at run time: a strided
operand filled element by element (vla_lanes) on RVV - a scalar load,
vfslide1down into the top lane - run against a reference at two VLENs
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage
from ukrgen.models.load_store_operations import lsc_repeat

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = {"rvv-LMUL": "1", "A-layout": ["m:s", "k:c"],
          "mm-to": ["fma(A.VEC:vla_lanes, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]}


def run(**extra):
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa="rvv", **PARAMS, **extra)
    finally:
        t.STAGES = saved


class test_vla_repeat(unittest.TestCase):

    def test_only_on_vla(self):
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="neon", **{"A-layout": ["m:s", "k:c"], "list-to-candidates": True,
                                           "mm-to": None})
        finally:
            t.STAGES = saved
        self.assertFalse(any("vla_lanes" in l for l in res.output.splitlines()))

    def test_ir(self):
        # one lsc_repeat per vector: its body, divisor and fill information
        ctx, res = run()
        repeats = [op for b in ctx.programs[0].blocks for s in ("prologue", "body", "epilogue", "tail")
                   for op in getattr(b, s) if isinstance(op, lsc_repeat)]
        self.assertTrue(repeats)
        r = repeats[0]
        self.assertEqual(2, len(r.body))
        self.assertEqual(2, r.divisor)                     # 16 bytes of doubles
        self.assertEqual({"component": "A", "index": "m", "direction": "load"},
                         {k: v for k, v in r.fill.items() if k != "stride"})

    def test_loop(self):
        ctx, res = run()
        body = ctx.emitted[0].blocks[0].sections["body"]
        self.assertTrue(any(l.startswith("fld ") for l in body))
        self.assertTrue(any(l.startswith("vfslide1down.vf") for l in body))
        self.assertTrue(any(l.endswith("_elements:") for l in body))

    def test_runs(self):
        cc, qemu = "riscv64-linux-gnu-gcc", "qemu-riscv64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        ctx, res = run()
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(A,m)", "stride(C,n)"],
                         list(ctx.emitted[0].params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([cc, "-static", "-O1", "-march=rv64gcv",
                                os.path.join(HERE, "strided_mm_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for vlen, tile in ((128, "tile 4 x 2"), (256, "tile 8 x 2")):
                r = subprocess.run([qemu, "-cpu", f"rv64,v=true,vlen={vlen},elen=64", exe],
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(0, r.returncode, r.stdout)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)


if __name__ == "__main__":
    unittest.main()
