"""
blisgen's C: gemm wrappers with BLIS's signature run against a reference
through BLIS's edge-case macros (a stub of blis.h) - full and partial tiles,
C column-major, row-major and general strided - and the kernel table's
chooser: an MR x NR asked for, else the family's default
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from ukrgen.flow.isa_map import make_generator
from ukrgen.injectors.blis.families import family, build_gemm
from ukrgen.injectors.blis.cgen import (gemm_wrapper, asm_source, vl_helper, c_expr, gemm_table,
                                        GEMM_TABLE_PRELUDE, CTYPE)
from injectors.test_families import VM

HERE = os.path.dirname(os.path.abspath(__file__))
CC = ["aarch64-linux-gnu-gcc", "-static", "-march=armv8-a+sve"]
QEMU = "qemu-aarch64-static"


def needs_tools(test):
    return unittest.skipUnless(shutil.which(CC[0]) and shutil.which(QEMU),
                               f"needs {CC[0]} and {QEMU}")(test)


def build(isa, dt, m, n, default=None):
    fam = family.from_yaml("gemm", {"family": "vm", "dtypes": [dt], "params": VM, "m": m, "n": n,
                                    **({"default": {dt: default}} if default else {})})
    built, skipped = build_gemm(isa, f"ukrgen_{isa}", fam)
    return fam, built


class test_cgen(unittest.TestCase):

    def run_c(self, isa, sources, kernels, runners, defines=()):
        with tempfile.TemporaryDirectory() as d:
            objs = []
            for i, k in enumerate(kernels):
                with open(os.path.join(d, f"k{i}.s"), "w") as f:
                    f.write(asm_source(k))
                r = subprocess.run(CC + ["-c", os.path.join(d, f"k{i}.s"), "-o", os.path.join(d, f"k{i}.o")],
                                   capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                objs.append(os.path.join(d, f"k{i}.o"))
            with open(os.path.join(d, "w.c"), "w") as f:
                f.write(sources)
            r = subprocess.run(CC + ["-O1", f"-I{HERE}", *defines, os.path.join(d, "w.c"), *objs,
                                     "-o", os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            return [subprocess.run(q + [os.path.join(d, "run")], capture_output=True, text=True,
                                   timeout=60).stdout for q in runners]

    @needs_tools
    def test_wrappers(self):
        for isa, dt, m, n in (("neon", "FP64", 2, 2), ("sve", "FP64", 2, 3), ("sve", "FP32", 1, 4)):
            fam, built = build(isa, dt, [m], [n])
            self.assertEqual(1, len(built))
            k, ctype = built[0], CTYPE[dt]
            src = "#include \"blis_stub.h\"\n" + vl_helper(make_generator(isa)) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, ctype)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, ctype)}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            runners = [[QEMU, "-cpu", "max"]] if "neon" == isa else \
                [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)]
            for out in self.run_c(isa, src, [k], runners, [f"-DUKR={k.symbol}", f"-DWT={ctype}"]):
                self.assertIn("81 runs, 0 wrong", out, k.symbol)

    @needs_tools
    def test_chooser(self):
        fam, built = build("sve", "FP64", [1, 2], [2, 3], default="2x3")
        self.assertEqual(4, len(built))
        src = "#include \"blis_stub.h\"\n#include <stdio.h>\n" \
              "typedef void (*gemm_ukr_ft)( dim_t, dim_t, dim_t, const void*, const void*, const void*, " \
              "const void*, void*, inc_t, inc_t, auxinfo_t*, const cntx_t* );\n" + \
              vl_helper(make_generator("sve")) + "".join(gemm_wrapper(k) for k in built) + \
              GEMM_TABLE_PRELUDE + gemm_table("FP64", built, fam.default["FP64"]) + """
int main( void )
{
	const dim_t vl = ukrgen_vl( sizeof( double ) );
	printf( "exact %s\\n", ukrgen_dgemm_choose( vl, 2 )->name );
	printf( "absent %s\\n", ukrgen_dgemm_choose( 3, 3 )->name );
	return 0;
}
"""
        out = self.run_c("sve", src, built, [[QEMU, "-cpu", "max,sve256=on"]])[0]
        self.assertIn("exact vm_1vx2", out)
        # absent: the family's default, 2 vectors by 3
        self.assertIn("absent vm_2vx3", out)


if __name__ == "__main__":
    unittest.main()
