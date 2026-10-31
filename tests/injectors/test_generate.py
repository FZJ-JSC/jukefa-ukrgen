"""
blisgen's configuration files: every family's kernels, wrappers, the context
initialization, the family header and the report of sizes skipped
"""

import contextlib
import io
import os
import tempfile
import unittest

from ukrgen.injectors.blis.families import family, configuration, resolve_blocksizes
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
            self.assertEqual([], made["reduced"])
            self.assertEqual(2048, made["stack_buf_size"])
            # given: the configuration's, then the caller's
            cfg.stack_buf_size = 4096
            self.assertEqual(4096, generate(cfg, d)["stack_buf_size"])
            self.assertEqual(8192, generate(cfg, d, stack_size=8192)["stack_buf_size"])

    def test_reduced_unroll_reported(self):
        # an unroll the registers can't hold: built at half of it (or less),
        # and the report says so - not silently another kernel than asked.
        # NEON's lane FMA, 2 vectors by 4, unroll 4: the k loop's rings (B's
        # double-buffered for preloading) aren't renamed and take more than 32
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "preset": "gemm_fma_lane",
                                        "vectorize": "m", "unroll": 4, "m": [2], "n": [4],
                                        "params": {"A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
                                                   "C-layout": ["m:c", "n:s"]},
                                        "schedule": ["RAW:data:vreg:::4"], "default": {"FP64": "4x4"}})
        cfg = configuration(isa="neon", name="ukrgen_neon", families=[fam])
        with tempfile.TemporaryDirectory() as d:
            made = generate(cfg, d)
            self.assertEqual(1, len(made["kernels"]))
            (name, symbol, asked, got), = made["reduced"]
            self.assertEqual((4, made["kernels"][0].unroll), (asked, got))
            self.assertLess(got, asked)
            with open(os.path.join(d, "config/ukrgen_neon/blisgen_report.txt")) as f:
                report = f.read()
            self.assertIn(f"unroll {got} of 4: vm {symbol}", report)

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
            # a maximum left out: the default's own
            self.assertEqual({"mr-in-mc": 16, "mr-in-mc-max": 16, "nr-in-nc": 200, "nr-in-nc-max": 200,
                              "kc": 128, "kc-max": 128}, cfg.blocksizes["FP64"])
            with open(os.path.join(d, "other.yaml"), "w") as f:
                f.write("isa: neon\nfamily: x\n")
            with self.assertRaisesRegex(ValueError, "is for neon"):
                configuration.from_files({("gemm", "FP32"): os.path.join(d, "sgemm.yaml"),
                                          ("gemm", "FP64"): os.path.join(d, "other.yaml")})

    def test_blocksizes(self):
        """mr-in-mc, nr-in-nc and kc, and the -max forms BLIS keeps beside them"""
        with tempfile.TemporaryDirectory() as d:
            def write(name, spec):
                path = os.path.join(d, name)
                with open(path, "w") as f:
                    f.write("isa: rvv\nfamily: vn\nm: [2]\nn: [2]\nblocksizes: " + spec + "\n")
                return path
            cfg = configuration.from_files({
                ("gemm", "FP32"): write("sgemm.yaml", "{mr-in-mc: 16, nr-in-nc: 64, kc: 256}"),
                ("gemm", "FP64"): write("dgemm.yaml", "{mr-in-mc: 36, kc: 308, nr-in-nc-max: 424, "
                                                      "kc-max: 512}")})
            # the maxima the configuration gives, and its defaults' ones else
            self.assertEqual({"mr-in-mc": 36, "mr-in-mc-max": 36, "nr-in-nc": 200,
                              "nr-in-nc-max": 424, "kc": 308, "kc-max": 512}, cfg.blocksizes["FP64"])
            self.assertEqual({"mr-in-mc": 16, "mr-in-mc-max": 16, "nr-in-nc": 64,
                              "nr-in-nc-max": 64, "kc": 256, "kc-max": 256}, cfg.blocksizes["FP32"])
            for spec, why in (("{kc: 256, kc-max: 128}", "kc-max 128 below kc 256"),
                              ("{mc: 128}", "no blocksize mc there"),
                              ("{kc: 0}", "1 or more"),
                              ("{kc: two}", "a number")):
                with self.assertRaisesRegex(ValueError, why):
                    configuration.from_files({("gemm", "FP64"): write("x.yaml", spec)})
            # one data type's blocksizes in two files: said, not one the other's
            with self.assertRaisesRegex(ValueError, "given in .*sgemm.yaml too"):
                configuration.from_files({("gemm", "FP32"): write("sgemm.yaml", "{kc: 256}"),
                                          ("packm", "FP32"): write("spackm.yaml", "{kc: 128}")})
            # alike: no complaint
            cfg = configuration.from_files({("gemm", "FP32"): write("sgemm.yaml", "{kc: 256}"),
                                            ("packm", "FP32"): write("spackm.yaml", "{kc: 256}")})
            self.assertEqual(256, cfg.blocksizes["FP32"]["kc"])

    def test_blocksizes_without_kernels(self):
        """a data type's blocksizes with no kernel of it: said, not dropped"""
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [1], "n": [2]})
        cfg = configuration(isa="neon", name="ukrgen_neon", families=[fam],
                            blocksizes={"FP32": resolve_blocksizes({"kc": 128}),
                                        "FP64": resolve_blocksizes({"mr-in-mc": 8})})
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(err):
            generate(cfg, d)
        self.assertIn("FP32 blocksizes given, no FP32 gemm kernel", err.getvalue())
        self.assertNotIn("FP64 blocksizes given", err.getvalue())

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
