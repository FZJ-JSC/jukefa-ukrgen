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

HERE = os.path.dirname(os.path.abspath(__file__))
MIXED = {"A-data-type": "FP16", "B-data-type": "FP16", "C-data-type": "FP32"}
MIXED_FOR = {"neon": MIXED, "sve": MIXED,
             "rvv": {"A-data-type": "FP32", "B-data-type": "FP32", "C-data-type": "FP64"}}
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

    def candidate(self, isa, method, **extra):
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa=isa, **MIXED_FOR[isa], **extra,
                            **{"list-to-candidates": True, "mm-to": None})
        finally:
            t.STAGES = saved
        cands = [l.split('"')[1] for l in res.output.splitlines() if "--mm-to" in l]
        return next(c for c in cands if method in c and "A.VEC:direct" in c and "i=m" in c
                    and not any(x in c for x in ("ILANE", "BLOCKLANE", "VF", "NP")))

    def runs(self, isa, method, cc, march, qemu, cpu, defines=(), cand=None, **extra):
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        stages = list(t.STAGES)
        i = [s.__name__ for s in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            ctx, res = t.mm(isa=isa, **MIXED_FOR[isa], **extra,
                            **{"mm-to": [cand or self.candidate(isa, method, **extra)]})
        finally:
            t.STAGES = saved
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(C,n)"], list(p.params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(p.function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([cc, "-static", "-O1", march, *defines,
                                os.path.join(HERE, "widen_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([qemu, "-cpu", cpu, exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn(", 0 wrong", r.stdout)
        return p

    def test_neon_runs(self):
        # halves: fmlal/fmlal2, members stored one after the other
        self.runs("neon", "SPLIT_CONTIGUOUS", "aarch64-linux-gnu-gcc",
                  "-march=armv8.2-a+fp16+fp16fml", "qemu-aarch64-static", "max", cand=NEON_SPLIT)

    def test_sve_runs(self):
        # bottom and top: fmlalb/fmlalt into even and odd elements, stored
        # interleaved again (st2w)
        p = self.runs("sve", "SPLIT_INTERLEAVED", "aarch64-linux-gnu-gcc", "-march=armv8-a+sve2",
                      "qemu-aarch64-static", "max,sve256=on")
        self.assertTrue(any(l.startswith("st2w") for b in p.blocks for l in b.sections["body"]))

    def test_rvv_runs(self):
        # a register group: one vfwmacc and one vse64 per group; nothing computes
        # on the wide elements, so no vtype switch beyond the setup's
        p = self.runs("rvv", "VEC_GROUP", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                      "qemu-riscv64-static", "rv64,v=true,vlen=256,elen=64",
                      defines=("-DNT=float", "-DWT=double", "-DFMA=fma"), **{"rvv-LMUL": "1"})
        self.assertEqual(1, sum(l.startswith("vsetvli") for l in p.instructions()))


if __name__ == "__main__":
    unittest.main()
