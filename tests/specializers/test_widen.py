"""
Widening: FP16 inputs accumulating into FP32 - the model's wide registers as
groups, carried out by the widen irmod with the ISA's widening method
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage
from ukrgen.flow.stages.stage import stage_error

HERE = os.path.dirname(os.path.abspath(__file__))
MIXED = {"A-data-type": "FP16", "B-data-type": "FP16", "C-data-type": "FP32"}
NEON_SPLIT = "fma[PART+widening_method=SPLIT_CONTIGUOUS](A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"


def run(isa, **extra):
    stages = list(t.STAGES)
    i = [s.__name__ for s in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa=isa, **MIXED, **extra)
    finally:
        t.STAGES = saved


class test_widen(unittest.TestCase):

    def test_candidates(self):
        # a wide register counts as a group: the extents agree
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="neon", **MIXED, **{"list-to-candidates": True, "mm-to": None})
        finally:
            t.STAGES = saved
        self.assertIn(NEON_SPLIT, [l.split('"')[1] for l in res.output.splitlines() if "--mm-to" in l])

    def test_neon_halves(self):
        # fmlal and fmlal2 per register of A, into the members of a C group;
        # member 1 stored 4 elements after member 0
        ctx, res = run("neon", **{"mm-to": [NEON_SPLIT]})
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        body = p.blocks[0].sections["body"]
        lows = [l for l in body if l.startswith("fmlal ")]
        self.assertEqual(len(lows), sum(l.startswith("fmlal2 ") for l in body))
        self.assertTrue(any(l.endswith(", #16]") for l in p.blocks[1].sections["body"]))
        ok, err = t.assembles(p.function("ukr"), arch="armv8.2-a+fp16fml")
        self.assertTrue(ok, err)

    def test_unimplemented_methods(self):
        # SVE's bottom and top: required, but not carried out yet - says so
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="sve", **MIXED, **{"list-to-candidates": True, "mm-to": None})
        finally:
            t.STAGES = saved
        cands = [l.split('"')[1] for l in res.output.splitlines() if "--mm-to" in l]
        interleaved = next(c for c in cands if "SPLIT_INTERLEAVED" in c and "A.VEC:direct" in c
                           and "ILANE" not in c and "BLOCKLANE" not in c)
        with self.assertRaisesRegex(stage_error, "SPLIT_INTERLEAVED is not implemented"):
            run("sve", **{"mm-to": [interleaved]})

    def test_neon_runs(self):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        ctx, res = run("neon", **{"mm-to": [NEON_SPLIT]})
        p = ctx.emitted[0]
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(C,n)"], list(p.params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(p.function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([cc, "-static", "-O1", "-march=armv8.2-a+fp16+fp16fml",
                                os.path.join(HERE, "widen_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([qemu, "-cpu", "max", exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn(", 0 wrong", r.stdout)


if __name__ == "__main__":
    unittest.main()
