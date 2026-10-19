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
                                        GEMM_TABLE_PRELUDE, CTYPE, cntx_init, stack_buf_size,
                                        family_header)
from injectors.test_families import VM, VN

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

    @needs_tools
    def test_cntx_init(self):
        # FP64 kernels only: FP32 keeps the reference's
        fam, built = build("sve", "FP64", [1, 2], [2, 3], default="2x3")
        src = "#include \"cntx_stub.h\"\n" + \
              cntx_init("ukrgen_sve", make_generator("sve"), built, fam.default,
                        {"FP64": {"kc": 128}}).replace('#include "blis.h"', "") + \
              "".join(gemm_wrapper(k) for k in built) + """
#include <stdio.h>
void bli_cntx_init_ukrgen_sve_ref( cntx_t* c )
{ stub_bs[ BLIS_MR ][ 0 ] = 7; stub_bs[ BLIS_NR ][ 0 ] = 5; stub_bs[ BLIS_MC ][ 0 ] = 70; stub_bs[ BLIS_KC ][ 0 ] = 99; }
int main( void )
{
	cntx_t c; bli_cntx_init_ukrgen_sve( &c );
	const char* name = "?";
	for ( int i = 0; i < ( int )( sizeof( ukrgen_dgemm_kernels ) / sizeof( ukrgen_dgemm_kernels[ 0 ] ) ); i++ )
		if ( ukrgen_dgemm_kernels[ i ].ukr == stub_ukr[ 1 ] ) name = ukrgen_dgemm_kernels[ i ].name;
	printf( "d %s mr %ld nr %ld mc %ld nc %ld kc %ld | s mr %ld kc %ld %s\\n", name,
	        stub_bs[ BLIS_MR ][ 1 ], stub_bs[ BLIS_NR ][ 1 ], stub_bs[ BLIS_MC ][ 1 ], stub_bs[ BLIS_NC ][ 1 ],
	        stub_bs[ BLIS_KC ][ 1 ], stub_bs[ BLIS_MR ][ 0 ], stub_bs[ BLIS_KC ][ 0 ],
	        stub_ukr[ 0 ] ? "set" : "reference" );
	return 0;
}
"""
        with tempfile.TemporaryDirectory() as d:
            objs = []
            for i, k in enumerate(built):
                with open(os.path.join(d, f"k{i}.s"), "w") as f:
                    f.write(asm_source(k))
                subprocess.run(CC + ["-c", os.path.join(d, f"k{i}.s"), "-o", os.path.join(d, f"k{i}.o")],
                               check=True)
                objs.append(os.path.join(d, f"k{i}.o"))
            with open(os.path.join(d, "c.c"), "w") as f:
                f.write(src)
            r = subprocess.run(CC + ["-O1", f"-I{HERE}", os.path.join(d, "c.c"), *objs,
                                     "-o", os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            def run(env):
                e = dict(os.environ)
                e.pop("BLIS_MR_D", None)
                e.pop("BLIS_NR_D", None)
                e.update(env)
                return subprocess.run([QEMU, "-cpu", "max,sve256=on", os.path.join(d, "run")],
                                      capture_output=True, text=True, env=e).stdout
            # unset: the default, 2 vectors (8 doubles at 256 bits) by 3
            self.assertIn("d vm_2vx3 mr 8 nr 3 mc 128 nc 600 kc 128 | s mr 7 kc 99 reference", run({}))
            self.assertIn("d vm_1vx2 mr 4 nr 2", run({"BLIS_MR_D": "4", "BLIS_NR_D": "2"}))
            # a size not made: the default
            self.assertIn("d vm_2vx3 mr 8 nr 3", run({"BLIS_MR_D": "5", "BLIS_NR_D": "5"}))

    @needs_tools
    def test_large_tiles(self):
        # the accumulators fill the register file: C streams through the
        # epilogue, scheduled into their registers as they are consumed
        plain = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                          "m": [2], "n": [8]})
        built, skipped = build_gemm("sve", "ukrgen_sve", plain)
        self.assertEqual([], built)
        self.assertIn("--mru", skipped[0][2])
        for params, m, n, tiles in ((dict(VM, mru=True), 2, 8, ("mr 8 nr 8", "mr 16 nr 8")),
                                    (VN, 8, 3, ("mr 8 nr 12", "mr 8 nr 24"))):
            fam = family.from_yaml("gemm", {"family": "f", "dtypes": ["FP64"], "params": params,
                                            "m": [m], "n": [n]})
            built, skipped = build_gemm("sve", "ukrgen_sve", fam)
            self.assertEqual(1, len(built), skipped)
            k = built[0]
            src = "#include \"blis_stub.h\"\n" + vl_helper(make_generator("sve")) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double')}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double')}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            outs = self.run_c("sve", src, [k], [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                              [f"-DUKR={k.symbol}", "-DWT=double"])
            for out, tile in zip(outs, tiles):
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out, k.symbol)

    def test_stack_and_family_header(self):
        fam, built = build("sve", "FP64", [2], [3])
        # 2 vectors by 3 doubles at 2048 bits: 64 x 3 x 8 bytes; at least BLIS's 2048
        self.assertEqual(2048, stack_buf_size("sve", None, built))
        fam, built = build("sve", "FP64", [2], [6])
        self.assertEqual(1, len(built))
        # 2 vectors of 32 doubles by 6: 3 KiB
        self.assertEqual(64 * 6 * 8, stack_buf_size("sve", None, built))
        self.assertEqual(65536, stack_buf_size("sve", None, built, given=65536))
        header = family_header("ukrgen_sve", 12288)
        self.assertIn("#define BLIS_STACK_BUF_MAX_SIZE 12288", header)
        self.assertIn("#define BLIS_RELAX_MCNR_NCMR_CONSTRAINTS", header)


if __name__ == "__main__":
    unittest.main()
