"""
blisgen's configuration files: every family's kernels, wrappers, the context
initialization, the family header and the report of sizes skipped
"""

import os
import tempfile
import unittest

from ukrgen.injectors.blis.families import family, configuration
from ukrgen.injectors.blis.generate import generate
from injectors.test_families import VM


class test_generate(unittest.TestCase):

    def test_files(self):
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [1, 16], "n": [2], "default": {"FP64": "1x2"}})
        cfg = configuration(isa="neon", name="ukrgen_neon", families=[fam])
        with tempfile.TemporaryDirectory() as d:
            made = generate(cfg, d)
            self.assertEqual(1, len(made["kernels"]))
            self.assertEqual(1, len(made["skipped"]))
            for rel in ("kernels/ukrgen_neon/3/bli_dgemm_ukrgen_neon_vm_2x2.S",
                        "kernels/ukrgen_neon/3/bli_gemm_ukrgen_neon.c",
                        "config/ukrgen_neon/bli_cntx_init_ukrgen_neon.c",
                        "config/ukrgen_neon/bli_family_ukrgen_neon.h",
                        "config/ukrgen_neon/blisgen_report.txt"):
                self.assertTrue(os.path.exists(os.path.join(d, rel)), rel)
            with open(os.path.join(d, "config/ukrgen_neon/blisgen_report.txt")) as f:
                report = f.read()
            self.assertIn("skipped vm FP64 16x2", report)
            self.assertEqual(2048, made["stack_buf_size"])
            # given: the configuration's, then the caller's
            cfg.stack_buf_size = 4096
            self.assertEqual(4096, generate(cfg, d)["stack_buf_size"])
            self.assertEqual(8192, generate(cfg, d, stack_size=8192)["stack_buf_size"])


if __name__ == "__main__":
    unittest.main()
