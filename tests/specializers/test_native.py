"""
Kernels run against a reference gemm: natively on x86 where the CPU has the
ISA and gcc is there, emulated (qemu user mode) for AArch64 and RISC-V where
qemu and a cross compiler are there. A harness calls the function with ukrgen's
parameters - k, the start addresses, the strides in bytes - over every case
(alpha 1 or not, beta 0, -0.0, 1 or other), k with and without full
iterations and remainders, C NaN where beta is 0 (never read), guards around C
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from specializers.gemm_helper import gemm

HERE = os.path.dirname(os.path.abspath(__file__))


def cpu_has(flag):
    try:
        with open("/proc/cpuinfo") as f:
            return any(flag in line.split() for line in f if line.startswith("flags"))
    except OSError:
        return False


def header(params):
    args = []
    for name in params:
        if "k" == name:
            args.append("long k")
        elif name in ("base(alpha)", "base(beta)"):
            args.append(f"const double* {name[5:-1]}")
        elif name.startswith("base("):
            args.append(f"double* {name[5:-1]}")
        else:
            args.append("long s" + name[7:-1].replace(",", ""))
    return "void ukr(" + ", ".join(args) + ");\n"


class test_native(unittest.TestCase):

    def run_gemm(self, isa, cc=("gcc",), run=()):
        ctx, res = gemm(isa)
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "base(alpha)", "base(beta)",
                          "stride(A,k)", "stride(B,k)", "stride(C,n)"], list(p.params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(p.function("ukr")) + "\n")
            with open(os.path.join(d, "ukr.h"), "w") as f:
                f.write(header(p.params))
            exe = os.path.join(d, "run")
            r = subprocess.run([*cc, "-O1", f'-DKERNEL_H="{d}/ukr.h"',
                                os.path.join(HERE, "native_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([*run, exe], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn(", 0 wrong", r.stdout)
        return r.stdout

    @unittest.skipUnless(shutil.which("gcc") and cpu_has("avx2") and cpu_has("fma"),
                         "needs gcc and an AVX2 CPU")
    def test_avx2(self):
        self.assertIn("tile 8 x 3", self.run_gemm("avx256"))

    @unittest.skipUnless(shutil.which("gcc") and cpu_has("avx512f"),
                         "needs gcc and an AVX-512 CPU")
    def test_avx512(self):
        self.assertIn("tile 16 x 3", self.run_gemm("avx512"))


    def emulated(self, isa, cc, march, qemu, cpu):
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        return self.run_gemm(isa, cc=(cc, "-static", march), run=(qemu, "-cpu", cpu))

    def test_neon(self):
        out = self.emulated("neon", "aarch64-linux-gnu-gcc", "-march=armv8-a",
                            "qemu-aarch64-static", "max")
        self.assertIn("tile 4 x 3", out)

    def test_sve(self):
        # 256-bit vectors: the tile follows the vector length
        out = self.emulated("sve", "aarch64-linux-gnu-gcc", "-march=armv8-a+sve",
                            "qemu-aarch64-static", "max,sve256=on")
        self.assertIn("tile 8 x 3", out)

    def test_rvv(self):
        out = self.emulated("rvv", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                            "qemu-riscv64-static", "rv64,v=true,vlen=256,elen=64")
        self.assertIn("tile 8 x 3", out)


if __name__ == "__main__":
    unittest.main()
