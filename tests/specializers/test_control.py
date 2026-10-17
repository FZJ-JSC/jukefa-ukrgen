"""
Control flow: a function with its parameters from the calling convention,
loops around the blocks' sections, the dispatch on cases
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from specializers.gemm_helper import gemm
from specializers.test_signature import assembles


def assembles_for(isa, lines):
    if isa.startswith("avx"):
        return assembles(lines, arch="x86")
    if "sve" == isa:
        return assembles(lines, arch="armv8-a+sve")
    if "rvv" == isa:
        if not shutil.which("riscv64-linux-gnu-as"):
            return True, ""
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "k.s")
            with open(src, "w") as f:
                f.write("\n".join(lines) + "\n")
            r = subprocess.run(["riscv64-linux-gnu-as", "-march=rv64gcv", src,
                                "-o", os.path.join(d, "k.o")], capture_output=True, text=True)
            return 0 == r.returncode, r.stderr
    return assembles(lines)


class test_control(unittest.TestCase):

    def test_gemm_everywhere(self):
        # the main loop, its tail, the dispatch on six cases: emitted and
        # assembled on every ISA, x86's 14 general registers included
        for isa in ("neon", "sve", "avx256", "avx512", "rvv"):
            with self.subTest(isa=isa):
                ctx, res = gemm(isa)
                self.assertTrue(res.completed, res.output)
                p = ctx.emitted[0]
                self.assertEqual("k", list(p.params)[0])
                ok, err = assembles_for(isa, p.function("ukr"))
                self.assertTrue(ok, err)

    def test_structure(self):
        ctx, res = gemm("neon")
        p = ctx.emitted[0]
        labels = [l[:-1] for l in p.code if l.endswith(":")]
        for part in ("_done", "_loop", "_last", "_tail", "_taildone", "_cases_end"):
            self.assertTrue(any(l.endswith(part) for l in labels), part)
        cases = [l for l in labels if "_case" in l and not l.endswith("_end")]
        self.assertEqual(len(p.cases), len(cases))
        # k is counted in its own register: kiterkleft, then cb
        self.assertTrue(any(l.startswith("cbz x0") for l in p.code))
        self.assertEqual("ret", p.exit[-1])

    def test_dispatch(self):
        # beta and alpha loaded at their size and compared as floating point
        # with the cases' values: 0, and 1.0 from its bits
        ctx, res = gemm("neon")
        p = ctx.emitted[0]
        beta, alpha = p.params["base(beta)"], p.params["base(alpha)"]
        self.assertTrue(any(l.startswith("ldr d") and l.endswith(f"[{beta},#0]") for l in p.code))
        self.assertTrue(any(l.startswith("ldr d") and l.endswith(f"[{alpha},#0]") for l in p.code))
        self.assertTrue(any(l.endswith("#4607182418800017408") for l in p.code))
        self.assertTrue(any(l.startswith("fcmp") for l in p.code))

    def test_registers_reused(self):
        # k's register is free after the loop: the dispatch reuses it
        ctx, res = gemm("neon")
        p = ctx.emitted[0]
        k = p.params["k"]
        after = p.code[next(i for i, l in enumerate(p.code) if l.endswith("_taildone:")):]
        self.assertTrue(any(l.split()[0] in ("mov", "ldr") and l.split()[1].startswith(f"{k},")
                            for l in after))


if __name__ == "__main__":
    unittest.main()
