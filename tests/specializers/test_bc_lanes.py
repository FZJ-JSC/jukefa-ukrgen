"""
bc_lanes: a vector of a broadcast operand's elements loaded once, each
element broadcast out of its lane - beside bc_lane, one element loaded into a
lane and broadcast from there
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage

HERE = os.path.dirname(os.path.abspath(__file__))
CAND = "fma(A.VEC:direct, B.VEC:bc_lanes, C.VEC){i=m, n=1, k*=1}"


def run(isa, **extra):
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa=isa, **{"mm-tileop": [CAND], "n": "4"}, **extra)
    finally:
        t.STAGES = saved


class test_bc_lanes(unittest.TestCase):

    def test_shape(self):
        # one load per two of B's doubles, a dup per element
        ctx, res = run("neon")
        self.assertTrue(res.completed, res.output)
        body = ctx.emitted[0].blocks[0].sections["body"]
        dups = [l for l in body if l.startswith("dup ")]
        self.assertTrue(any(l.endswith(".d[0]") for l in dups))
        self.assertTrue(any(l.endswith(".d[1]") for l in dups))

    def test_not_on_vla(self):
        # a lane per element needs the number of lanes now: fixed width only
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="sve", **{"list-tileop-candidates": True, "mm-tileop": None})
        finally:
            t.STAGES = saved
        self.assertFalse(any("bc_lanes" in l for l in res.output.splitlines()))

    def test_neon_runs(self):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        ctx, res = run("neon")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([cc, "-static", "-O1", "-DNT=double", "-DWT=double", "-DFMA=fma",
                                os.path.join(HERE, "widen_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([qemu, "-cpu", "max", exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn(", 0 wrong", r.stdout)


if __name__ == "__main__":
    unittest.main()
