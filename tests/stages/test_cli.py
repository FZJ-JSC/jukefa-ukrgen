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
        dts = [f"--{c}-data-type" for c in ("A", "B", "AB", "C")]
        args = ["--isa", "sve"] + [a for d in dts for a in (d, "FP64")] + [
            "--A-layout", "m:c", "k:s", "--B-layout", "k:s", "n:c", "--C-layout", "m:c", "n:s",
            "--mm-to", "0", "--betascale-to", "0", "--alphascale-to", "0", "--store-to", "0",
            "--m", "1", "--n", "1", "--k", "1"]
        listing = cli(*args[:-12], "--list-to-candidates").stdout
        first = next(l for l in listing.splitlines() if "--mm-to" in l).split("--mm-to ", 1)[1]
        chosen = next(l for l in cli(*args).stdout.splitlines() if l.startswith("--mm-to"))
        self.assertEqual(f"--mm-to {first}", chosen)


if __name__ == "__main__":
    unittest.main()
