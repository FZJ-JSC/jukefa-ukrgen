"""
Tests running the command line tool
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cli(*args):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    return subprocess.run([sys.executable, "-m", "clitools.ukrgen", *args], cwd=ROOT,
                          env=env, capture_output=True, text=True, timeout=600)


class test_cli(unittest.TestCase):

    def test_later_options_are_not_abbreviations(self):
        # --m is a dimension, not an abbreviation of --mm-to
        mm = "fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"
        dts = [f"--{c}-data-type" for c in ("A", "B", "AB", "C")]
        args = ["--isa", "sve"] + [a for d in dts for a in (d, "FP64")] + [
            "--A-layout", "m:c", "k:s", "--B-layout", "k:s", "n:c", "--C-layout", "m:c", "n:s",
            "--mm-to", mm, "--betascale-to", "fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}",
            "--alphascale-to", "fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}", "--store-to", "C.VEC:direct",
            "--m", "1", "--n", "1", "--k", "1"]
        out = cli(*args)
        self.assertEqual(0, out.returncode, out.stderr)
        chosen = next(l for l in out.stdout.splitlines() if l.startswith("--mm-to"))
        self.assertEqual(f'--mm-to "{mm}"', chosen)


if __name__ == "__main__":
    unittest.main()
