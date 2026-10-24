"""
blisgen's configuration files: every family's kernels, wrappers, the context
initialization, the family header and the report of sizes skipped
"""

import os
import tempfile
import unittest

from ukrgen.injectors.blis.families import family, configuration
from ukrgen.injectors.blis.generate import generate
from tests.injectors.test_families import VM


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

    def test_from_files(self):
        with tempfile.TemporaryDirectory() as d:
            for ch in ("s", "d"):
                with open(os.path.join(d, f"{ch}gemm.yaml"), "w") as f:
                    f.write("isa: sve\nfamily: vn\nm: [4, 8]\nn: 1..3\ndefault: 8x3\n"
                            "blocksizes: {kc: 128}\n")
            cfg = configuration.from_files({("gemm", "FP32"): os.path.join(d, "sgemm.yaml"),
                                            ("gemm", "FP64"): os.path.join(d, "dgemm.yaml"),
                                            ("packm", "FP64"): None})
            self.assertEqual(("sve", "ukrgen_sve"), (cfg.isa, cfg.name))
            self.assertEqual([["FP32"], ["FP64"]], [f.dtypes for f in cfg.families])
            self.assertEqual({"FP64": (8, 3)}, cfg.families[1].default)
            self.assertEqual({"kc": 128}, cfg.blocksizes["FP64"])
            with open(os.path.join(d, "other.yaml"), "w") as f:
                f.write("isa: neon\nfamily: x\n")
            with self.assertRaisesRegex(ValueError, "is for neon"):
                configuration.from_files({("gemm", "FP32"): os.path.join(d, "sgemm.yaml"),
                                          ("gemm", "FP64"): os.path.join(d, "other.yaml")})

    @unittest.skipUnless(os.environ.get("BLIS_SOURCE"), "BLIS_SOURCE names a BLIS tree")
    def test_patch(self):
        from ukrgen.injectors.blis.patch import patch_blis
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [1], "n": [2]})
        cfg = configuration(isa="neon", name="ukrgen_neon", families=[fam])
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "blis")
            patch_blis(os.environ["BLIS_SOURCE"], out, cfg, "test")
            with open(os.path.join(out, "config_registry")) as f:
                self.assertIn("ukrgen_neon: ukrgen_neon", f.read())
            with open(os.path.join(out, "frame/include/bli_gentconf_macro_defs.h")) as f:
                self.assertIn("INSERT_GENTCONF_UKRGEN_NEON", f.read())
            with open(os.path.join(out, "frame/base/bli_gks.c")) as f:
                self.assertIn("bli_gks_apply_env_blkszs", f.read())
            for rel in ("config/ukrgen_neon/make_defs.mk", "kernels/ukrgen_neon/bli_kernels_ukrgen_neon.h",
                        "config/ukrgen_neon/bli_kernel_defs_ukrgen_neon.h"):
                self.assertTrue(os.path.exists(os.path.join(out, rel)), rel)


if __name__ == "__main__":
    unittest.main()
