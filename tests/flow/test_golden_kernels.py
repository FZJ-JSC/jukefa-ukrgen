"""
The family pipeline's kernels against their recording (tests/flow/golden_kernels):
after an intended change, python -m tests.flow.golden_kernels record
"""
import difflib
import glob
import os
import re
import unittest

from parameterized import parameterized

from tests.flow.golden_kernels import build, kernels, path_of

HERE = os.path.dirname(os.path.abspath(__file__))


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


class test_no_mergeable_adds(unittest.TestCase):
    """
    No address register is added to twice with nothing between using it -
    the last iteration's advance and its move back one step (add $128, then
    add $-32): addrmerge's one add
    """
    ADDS = [re.compile(r"^addi\s+(\w+),\s*(\w+),\s*(-?\d+)$"),
            re.compile(r"^add\s+(x\d+),\s*(x\d+),\s*#(-?\d+)$"),
            re.compile(r"^add\s+(\w+),\s*(\w+),\s*(-?\d+)$"),
            re.compile(r"^addq\s+\$(-?\d+),\s*%?(\w+)$")]

    def reg(self, line):
        for k, p in enumerate(self.ADDS):
            m = p.match(line)
            if m:
                return m.group(2) if 3 == k else (m.group(1) if m.group(1) == m.group(2) else None)
        return None

    def test_recorded(self):
        for path in sorted(glob.glob(os.path.join(HERE, "golden_kernels", "*.s"))):
            lines = [l.strip() for l in open(path) if l.strip() and not l.strip().startswith(("#", ".", "//"))]
            for i, line in enumerate(lines):
                reg = self.reg(line)
                if reg is None:
                    continue
                for nxt in lines[i + 1:]:
                    if self.reg(nxt) == reg:
                        self.fail(f"{os.path.basename(path)}: {line} ... {nxt}")
                    if re.search(rf"%?\b{reg}\b", nxt) or nxt.endswith(":") or \
                            re.match(r"^(b\w*|j\w*|cb\w*|ret)\b", nxt):
                        break


if __name__ == "__main__":
    unittest.main()
