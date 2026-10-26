"""
The signature emitter's address resolution - as test_addr_resolver was for
the old resolver (legacy/): kernels with different numbers of address
registers per component and each pattern of advancing them (rotate,
blocked:N, phase - lsc_model/addressing.py's addr_pattern) compute what a
reference gemm does, run natively (AVX2) or emulated (NEON, RVV), and the
registers' number changes the kernel. Patterns taking a register back to an
earlier column of C are refused for now (test_not_specialized_yet).
"""
import shutil
import unittest

from tests.specializers import test_native as native
from tests.specializers.gemm_helper import gemm
from ukrgen.flow.stages.stage import stage_error

# component: (address registers, pattern) - what each case sets
CASES = {
    "A rotating over 2": {"A": (2, "rotate")},
    "A blocked by 2 over 3": {"A": (3, "blocked:2")},
    "B rotating over 3": {"B": (3, "rotate")},
    "C by phase over 2": {"C": (2, "phase")},
    "C blocked by 3 over 2": {"C": (2, "blocked:3")},
    "all at once": {"A": (2, "rotate"), "B": (2, "blocked:2"), "C": (2, "phase")},
}
# how each ISA runs: the native runner's arguments
RUNS = {
    "avx256": {},
    "neon": {"cc": ("aarch64-linux-gnu-gcc", "-static", "-march=armv8-a"),
             "run": ("qemu-aarch64-static", "-cpu", "max")},
    "rvv": {"cc": ("riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"),
            "run": ("qemu-riscv64-static", "-cpu", "rv64,v=true,vlen=256,elen=64")},
}


def params(case):
    out = {}
    for comp, (regs, pattern) in case.items():
        out[f"{comp}-addr-regs"] = str(regs)
        out[f"{comp}-addr-pattern"] = pattern
    return out


class test_addresses(native.test_native):
    """
    Each ISA's kernels over the cases: correct whatever the registers
    """

    def runnable(self, isa):
        run = RUNS[isa]
        if not run:
            if not (shutil.which("gcc") and native.cpu_has("avx2") and native.cpu_has("fma")):
                self.skipTest("needs gcc and an AVX2 CPU")
            return
        if not (shutil.which(run["cc"][0]) and shutil.which(run["run"][0])):
            self.skipTest(f"needs {run['cc'][0]} and {run['run'][0]}")

    def cases(self, isa):
        self.runnable(isa)
        for name, case in CASES.items():
            with self.subTest(isa=isa, case=name):
                self.run_gemm(isa, **RUNS[isa], **params(case))

    def test_avx2(self):
        self.cases("avx256")

    def test_neon(self):
        self.cases("neon")

    def test_rvv(self):
        self.cases("rvv")

    def test_registers_matter(self):
        self.runnable("rvv")
        texts = []
        for regs in (1, 3):
            self.run_gemm("rvv", **RUNS["rvv"], **params({"C": (regs, "rotate")}))
            texts.append(self.text)
        self.assertNotEqual(texts[0], texts[1])

    def test_blocked_by_the_kernels_sizes(self):
        # blocked:<expression> - the kernel's sizes, its address registers -
        # is the number it comes to: blocked:n here blocked:3, blocked:mn/R 3
        def code(pattern):
            ctx, res = gemm("rvv", **params({"B": (2, pattern)}))
            self.assertTrue(res.completed, res.output)
            return ctx.emitted[0].code
        self.assertEqual(code("blocked:3"), code("blocked:n"))
        self.assertEqual(code("blocked:3"), code("blocked:mn/R"))

    def test_not_specialized_yet(self):
        # C's tile is 3 columns: a pattern taking a register back to an
        # earlier column - rotating over 2, blocked by 2 - puts an access a
        # negative number of strides from its register, which the specializer
        # refuses for now. This fails, as a reminder, the day it's specialized
        for regs, pattern in ((2, "rotate"), (2, "blocked:2"), (3, "blocked:2")):
            with self.subTest(regs=regs, pattern=pattern):
                with self.assertRaises(stage_error) as caught:
                    gemm("rvv", **params({"C": (regs, pattern)}))
                self.assertIn("not specialized yet", str(caught.exception))

    # test_native's own: not again here
    test_avx512 = test_sve = None


if __name__ == "__main__":
    unittest.main()
