"""
rvv071's FP64 and FP32 kernels build - RVV's configurations, every family -
and assemble as RVV 0.7.1: binutils' XTheadVector, the th.-prefixed
spelling asmgen prints by default (its XTheadVector feature).
"""
import copy
import os
import shutil
import subprocess
import tempfile
import unittest
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIGS = (("rvv/fma_vf/dgemm.yaml", "FP64"), ("rvv/fma_vf/sgemm.yaml", "FP32"))
AS = "riscv64-linux-gnu-as"
MARCH = "-march=rv64gc_zba_zfh_xtheadvector"


class test_rvv071_kernels(unittest.TestCase):
    def test_build_and_assemble(self):
        if not shutil.which(AS):
            self.skipTest(f"{AS} not found")
        from ukrgen.injectors.blis.families import configuration, build_gemm
        from ukrgen.injectors.blis.cgen import asm_source
        warnings.simplefilter("ignore", DeprecationWarning)
        built = 0
        for path, dt in CONFIGS:
            cfg = configuration.from_files({("gemm", dt): os.path.join(ROOT, "ukrconfig", path)})
            for fam in cfg.families:
                m, n = fam.sizes["m"][0], fam.sizes["n"][0]
                with self.subTest(config=path, family=fam.name, size=f"{m}x{n}"):
                    f = copy.deepcopy(fam)
                    f.sizes = {"m": [m], "n": [n]}
                    ok, skipped = build_gemm("rvv071", cfg.name, f)
                    self.assertTrue(ok, skipped[0][2] if skipped else "nothing built")
                    text = asm_source(ok[0])
                    with tempfile.TemporaryDirectory() as tmp:
                        src = os.path.join(tmp, "k.s")
                        with open(src, "w") as out:
                            out.write(text)
                        res = subprocess.run([AS, MARCH, src, "-o", os.path.join(tmp, "k.o")],
                                             capture_output=True, text=True)
                    if res.returncode and "xtheadvector" in res.stderr:
                        self.skipTest("the assembler has no XTheadVector")
                    self.assertEqual(0, res.returncode, res.stderr[-1500:])
                    built += 1
        self.assertGreater(built, 0)


if __name__ == "__main__":
    unittest.main()
