"""
The signature emitter's address resolution - as test_addr_resolver was for
the old resolver (legacy/): kernels with different numbers of address
registers per component and each pattern of advancing them (rotate,
blocked:N, phase - lsc_model/addressing.py's addr_pattern) compute what a
reference gemm does, run natively (AVX2) or emulated (NEON, RVV), and the
registers' number changes the kernel. Patterns taking a register back to an
earlier column of C walk it there (test_back_to_earlier_columns); C's
column pointers (--C-column-pointers) 0 its pattern's registers alone.
"""
import shutil
import unittest

from tests.specializers import test_native as native
from tests.specializers.gemm_helper import gemm

# component: (address registers, pattern) - what each case sets
CASES = {
    "A rotating over 2": {"A": (2, "rotate")},
    "A blocked by 2 over 3": {"A": (3, "blocked:2")},
    "B rotating over 3": {"B": (3, "rotate")},
    "C by phase over 2": {"C": (2, "phase")},
    "C blocked by 3 over 2": {"C": (2, "blocked:3")},
    "all at once": {"A": (2, "rotate"), "B": (2, "blocked:2"), "C": (2, "phase")},
    "C phase+rotate over 4": {"C": (4, "phase+rotate")},
    "C phase+rotate over 4, no column pointers": {"C": (4, "phase+rotate", 0)},
    "C by phase over 2, no column pointers": {"C": (2, "phase", 0)},
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
    for comp, (regs, pattern, *pointers) in case.items():
        out[f"{comp}-addr-regs"] = str(regs)
        out[f"{comp}-addr-pattern"] = pattern
        if pointers:
            out[f"{comp}-column-pointers"] = str(pointers[0])
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

    def test_imm_offset_by_the_kernels_sizes(self):
        # --max-imm-offset an expression - the kernel's sizes, its element
        # size - is the number it comes to: on AVX2 (displacements) 2e and
        # min(ne, 2e) 16 bytes, a limit the kernel walks its addresses for
        def code(limit):
            ctx, res = gemm("avx256", **({} if limit is None else {"max-imm-offset": limit}))
            self.assertTrue(res.completed, res.output)
            return ctx.emitted[0].code
        sixteen = code("16")
        self.assertNotEqual(code(None), sixteen)
        self.assertEqual(sixteen, code("2e"))
        self.assertEqual(sixteen, code("min(ne, 2e)"))

    def test_back_to_earlier_columns(self):
        # C's tile is 3 columns: a pattern taking a register back to an
        # earlier column - rotating over 2, blocked by 2 - puts an access a
        # negative number of strides from its register: walked there, from the
        # register nearest it (column pointers only reach forward), and right
        self.runnable("rvv")
        for regs, pattern in ((2, "rotate"), (2, "blocked:2"), (3, "blocked:2")):
            with self.subTest(regs=regs, pattern=pattern):
                self.run_gemm("rvv", **RUNS["rvv"], **params({"C": (regs, pattern)}))

    # test_native's own: not again here
    test_avx512 = test_sve = None


if __name__ == "__main__":
    unittest.main()
