"""
The family pipeline's kernels against their recording (tests/flow/golden_kernels):
after an intended change, python -m tests.flow.golden_kernels record
"""
import difflib
import os
import unittest

from parameterized import parameterized

from tests.flow.golden_kernels import build, kernels, path_of


class test_golden_kernels(unittest.TestCase):
    @parameterized.expand([(k[0], *k[1:]) for k in kernels()])
    def test_unchanged(self, label, path, family, m, n):
        if not os.path.exists(path_of(label)):
            self.skipTest(f"{label}: not recorded")
        old = open(path_of(label)).read()
        new = build(path, family, m, n)
        if old != new:
            diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), "recorded", "now",
                                             lineterm="", n=1))
            self.fail(f"{label} changed:\n" + "\n".join(diff[:30]))


if __name__ == "__main__":
    unittest.main()
