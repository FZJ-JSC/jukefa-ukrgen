"""
Tests running the command line tool
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# gemm's epilogue cases, vectors along m: C contiguous along m, or general strides
CASES_CONTIGUOUS = [
    "--alphamul-tileop", "mul(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}",
    "--add-tileop", "add(AB.VEC, C.VEC:direct, C.VEC){i=m, n=1}",
    "--alphaadd-tileop", "fma(AB.VEC, alpha.VEC:bc_load, C.VEC:direct){i=m, n=1}",
    "--betaadd-tileop", "fma(C.VEC:direct, beta.VEC:bc_load, AB.VEC){i=m, n=1}",
    "--store_ab-tileop", "AB.VEC:direct"]
CASES_STRIDED = [
    "--alphamul-tileop", "mul(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}",
    "--add-tileop", "add(AB.VEC, C.VEC:gather, C.VEC){i=m, n=1}",
    "--alphaadd-tileop", "fma(AB.VEC, alpha.VEC:bc_load, C.VEC:gather){i=m, n=1}",
    "--betaadd-tileop", "fma(C.VEC:gather, beta.VEC:bc_load, AB.VEC){i=m, n=1}",
    "--store_ab-tileop", "AB.VEC:scatter"]


def cli(*args):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    return subprocess.run([sys.executable, "-m", "clitools.ukrgen", *args], cwd=ROOT,
                          env=env, capture_output=True, text=True, timeout=600)


class test_cli(unittest.TestCase):

    def test_later_options_are_not_abbreviations(self):
        # --m is a dimension, not an abbreviation of --mm-tileop
        mm = "fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"
        dts = [f"--{c}-data-type" for c in ("A", "B", "AB", "C")]
        # NEON: a complete run goes through the specializer, which doesn't
        # handle SVE's predicates yet
        args = ["--isa", "neon"] + [a for d in dts for a in (d, "FP64")] + [
            "--A-layout", "m:c", "k:s", "--B-layout", "k:s", "n:c", "--C-layout", "m:c", "n:s",
            "--mm-tileop", mm, "--betascale-tileop", "mul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}",
            "--alphascale-tileop", "fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}", "--store-tileop", "C.VEC:direct",
            "--m", "1", "--n", "1", "--k", "1",
            "--A-data-regs", "1", "--B-data-regs", "1", "--C-data-regs", "1"] + CASES_CONTIGUOUS
        out = cli(*args)
        self.assertEqual(0, out.returncode, out.stderr)
        chosen = next(l for l in out.stdout.splitlines() if l.startswith("--mm-tileop"))
        self.assertEqual(f'--mm-tileop "{mm}"', chosen)


class test_cli_help_and_errors(unittest.TestCase):

    COMMON = ["--isa", "sve", "--ukr", "gemm"] + \
        [a for c in ("A", "B", "AB", "C") for a in (f"--{c}-data-type", "DOUBLE")] + \
        ["--A-layout", "m:c", "k:s", "--B-layout", "k:s", "n:c", "--C-layout", "m:s", "n:s"]

    def test_plain_help(self):
        out = cli("--help")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertIn("--isa", out.stdout)

    def test_help_at_the_solve_stage(self):
        # the solve stage's choices aren't required by argparse, but the stage
        # needs them: help stops there and shows them
        out = cli(*self.COMMON, "--help")
        self.assertEqual(0, out.returncode, out.stderr)
        for option in ("--mm-tileop", "--store-tileop", "--list-tileop-candidates"):
            self.assertIn(option, out.stdout)

    def test_unknown_option_reported(self):
        out = cli(*self.COMMON, "--print-tos")
        self.assertEqual(2, out.returncode)
        self.assertIn("not recognized by the stages so far (or mistyped): --print-tos", out.stderr)
        # the missing choice is reported briefly, pointing at the listing
        self.assertIn("--list-tileop-candidates lists them all", out.stderr)
        self.assertLess(len(out.stderr.splitlines()), 20)

    def test_unknown_option_after_a_complete_run(self):
        dts = [a for c in ("A", "B", "AB", "C") for a in (f"--{c}-data-type", "DOUBLE")]
        out = cli("--isa", "neon", "--ukr", "gemm", *dts,
                  "--A-layout", "m:c", "k:s", "--B-layout", "k:s", "n:c", "--C-layout", "m:c", "n:s",
                  "--mm-tileop", "fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}",
                  "--betascale-tileop", "mul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}",
                  "--alphascale-tileop", "fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}",
                  "--store-tileop", "C.VEC:direct", "--m", "1", "--n", "1", "--k", "1",
                  "--A-data-regs", "1", "--B-data-regs", "1", "--C-data-regs", "1",
                  *CASES_CONTIGUOUS, "--bogus")
        self.assertEqual(2, out.returncode, out.stdout + out.stderr)
        self.assertIn("unrecognized arguments: --bogus", out.stderr)


if __name__ == "__main__":
    unittest.main()
