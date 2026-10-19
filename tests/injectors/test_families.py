"""
blisgen's kernel families: every size a family's choices build, with what
BLIS needs of each kernel, and the sizes skipped with the flow's reason
"""

import os
import tempfile
import unittest

from ukrgen.injectors.blis.families import family, configuration, build_gemm, parse_sizes
from stages.test_sto import CASE_TOS

# vectors along m, B broadcast; A and B packed as BLIS packs them
VM = {"mm-to": ["fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"],
      "betascale-to": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"],
      "alphascale-to": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
      "store-to": ["C.VEC:direct"],
      "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"], "C-layout": ["m:c", "n:s"]}
VM.update(CASE_TOS)


class test_families(unittest.TestCase):

    def test_sizes(self):
        self.assertEqual([1, 2, 3], parse_sizes("1..3"))
        self.assertEqual([4], parse_sizes(4))
        self.assertEqual([2, 5], parse_sizes([2, 5]))

    def test_gemm_sizes(self):
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": "1..2", "n": "1..2", "default": {"FP64": "2x2"}})
        self.assertEqual({"FP64": (2, 2)}, fam.default)
        built, skipped = build_gemm("neon", "ukrgen_neon", fam)
        self.assertEqual(4, len(built), skipped)
        k = next(k for k in built if (2, 2) == k.size)
        # NEON's vectors hold two doubles: two of them along m
        self.assertEqual(("4", "2"), (k.mr, k.nr))
        self.assertEqual("bli_dgemm_ukrgen_neon_vm_4x2", k.symbol)
        self.assertEqual("col", k.c_layout)
        # packed A and B: no strides of theirs
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "base(alpha)", "base(beta)",
                          "stride(C,n)"], k.params)

    def test_vla_sizes(self):
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [2], "n": [3]})
        built, skipped = build_gemm("sve", "ukrgen_sve", fam)
        self.assertEqual(1, len(built), skipped)
        self.assertEqual(("2*VL", "3"), (built[0].mr, built[0].nr))
        self.assertEqual("bli_dgemm_ukrgen_sve_vm_2vx3", built[0].symbol)

    def test_skipped(self):
        # 16 vectors of accumulators, times 3: more than the register file
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [16], "n": [3]})
        built, skipped = build_gemm("neon", "ukrgen_neon", fam)
        self.assertEqual([], built)
        self.assertEqual(1, len(skipped))
        self.assertIn("registers", skipped[0][2])

    def test_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "fam.yaml")
            with open(path, "w") as f:
                f.write("isa: neon\ngemm:\n  - family: vm\n    dtypes: [FP32, FP64]\n"
                        "    m: 1..2\n    n: 1..4\n    default: {FP64: 2x4}\n")
            cfg = configuration.load(path)
        self.assertEqual(("neon", "ukrgen_neon"), (cfg.isa, cfg.name))
        self.assertEqual(["vm"], [f.name for f in cfg.families])
        self.assertEqual([1, 2, 3, 4], cfg.families[0].sizes["n"])


if __name__ == "__main__":
    unittest.main()
