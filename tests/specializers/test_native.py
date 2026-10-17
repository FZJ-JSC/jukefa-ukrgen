"""
Kernels run natively against a reference gemm: x86 where the CPU has the ISA
and a C compiler is there. A harness calls the function with ukrgen's
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

    def run_gemm(self, isa):
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
            r = subprocess.run(["gcc", "-O1", f'-DKERNEL_H="{d}/ukr.h"',
                                os.path.join(HERE, "native_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([exe], capture_output=True, text=True, timeout=60)
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


if __name__ == "__main__":
    unittest.main()
