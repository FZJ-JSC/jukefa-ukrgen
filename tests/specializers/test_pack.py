"""
Packing kernels (ukr pack): Y[m,n] = kappa X[m,n], a column per iteration of
the loop over n, Y packed - run against a reference: natively on x86, under
qemu for AArch64 and RISC-V where the tools are there
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
PARAMS = {"ukr": "pack", "X-data-type": "FP64", "Y-data-type": "FP64",
          "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:p"], "m": "2", "n": "1",
          "pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
          "store-tileop": ["Y.VEC:direct"], "X-data-regs": "4", "Y-data-regs": "4",
          "kappa-data-regs": "1"}


def pack(isa, **extra):
    # with the irmods before specialization, as the command line runs it
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa=isa, **PARAMS, **extra)
    finally:
        t.STAGES = saved


class test_pack(unittest.TestCase):

    def run_pack(self, isa, cc=("gcc",), run=(), **extra):
        ctx, res = pack(isa, **extra)
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        self.assertEqual(["n", "base(X)", "base(Y)", "base(kappa)", "stride(X,n)"], list(p.params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(p.function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([*cc, "-O1", os.path.join(HERE, "pack_harness.c"),
                                os.path.join(d, "ukr.s"), "-o", exe], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([*run, exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(", 0 wrong", r.stdout)
        return r.stdout

    def test_kappa_hoisted(self):
        # kappa's broadcast once, before the check skipping the loop (hoist)
        ctx, res = pack("neon")
        code = ctx.emitted[0].code
        loads = [i for i, l in enumerate(code) if l.startswith("ld1r")]
        self.assertEqual(1, len(loads))
        self.assertLess(loads[0], next(i for i, l in enumerate(code) if l.startswith("cbz")))

    @unittest.skipUnless(shutil.which("gcc") and cpu_has("avx2"), "needs gcc and AVX2")
    def test_avx2(self):
        self.assertIn("panel 8", self.run_pack("avx256"))

    def test_neon(self):
        if not (shutil.which("aarch64-linux-gnu-gcc") and shutil.which("qemu-aarch64-static")):
            self.skipTest("needs aarch64-linux-gnu-gcc and qemu-aarch64-static")
        self.assertIn("panel 4", self.run_pack("neon", cc=("aarch64-linux-gnu-gcc", "-static"),
                                               run=("qemu-aarch64-static", "-cpu", "max")))

    def test_rvv(self):
        if not (shutil.which("riscv64-linux-gnu-gcc") and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        out = self.run_pack("rvv", cc=("riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"),
                            run=("qemu-riscv64-static", "-cpu", "rv64,v=true,vlen=256,elen=64"),
                            **{"rvv-LMUL": "1"})
        self.assertIn("panel 8", out)


if __name__ == "__main__":
    unittest.main()
