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
from ukrgen.injectors.blis.families import family, build_gemm, configuration
from ukrgen.injectors.blis.cgen import (gemm_wrapper, asm_source, vl_helper, vl_helpers, c_expr, gemm_table,
                                        GEMM_TABLE_PRELUDE, CTYPE, cntx_init, stack_buf_size,
                                        family_header)
from tests.injectors.test_families import VM, VN, VNF, VMF

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

    def run_c(self, isa, sources, kernels, runners, defines=(), cc=None):
        cc = cc or CC
        with tempfile.TemporaryDirectory() as d:
            objs = []
            for i, k in enumerate(kernels):
                with open(os.path.join(d, f"k{i}.s"), "w") as f:
                    f.write(asm_source(k))
                r = subprocess.run(cc + ["-c", os.path.join(d, f"k{i}.s"), "-o", os.path.join(d, f"k{i}.o")],
                                   capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                objs.append(os.path.join(d, f"k{i}.o"))
            with open(os.path.join(d, "w.c"), "w") as f:
                f.write(sources)
            # packm's harness with kappa 1 - the copy - and 2 - the multiply -
            # where the test doesn't choose
            kappas = [None]
            if any(x.startswith("-DPACKM=") for x in defines) and \
                    not any(x.startswith("-DKAPPA=") for x in defines):
                kappas = [1, 2]
            outs = []
            for kappa in kappas:
                run = os.path.join(d, f"run{kappa or ''}")
                r = subprocess.run(cc + ["-O1", f"-I{HERE}", *defines,
                                         *([f"-DKAPPA={kappa}"] if kappa else []),
                                         os.path.join(d, "w.c"), *objs, "-o", run],
                                   capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                outs += [subprocess.run(q + [run], capture_output=True, text=True,
                                        timeout=60).stdout for q in runners]
            return outs

    @needs_tools
    def test_wrappers(self):
        for isa, dt, m, n in (("neon", "FP64", 2, 2), ("sve", "FP64", 2, 3), ("sve", "FP32", 1, 4)):
            fam, built = build(isa, dt, [m], [n])
            self.assertEqual(1, len(built))
            k, ctype = built[0], CTYPE[dt]
            src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator(isa)) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, ctype, k.vl_fn)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, ctype, k.vl_fn)}; }}\n" + \
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
              "const void*, void*, inc_t, inc_t, const auxinfo_t*, const cntx_t* );\n" + \
              vl_helpers(built, make_generator("sve")) + "".join(gemm_wrapper(k) for k in built) + \
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
                        {"FP64": {"kc": 128, "kc-max": 512, "mr-in-mc-max": 32}}).replace('#include "blis.h"', "") + \
              "".join(gemm_wrapper(k) for k in built) + """
#include <stdio.h>
void bli_cntx_init_ukrgen_sve_ref( cntx_t* c )
{ stub_bs[ BLIS_MR ][ 0 ] = 7; stub_bs[ BLIS_NR ][ 0 ] = 5; stub_bs[ BLIS_MC ][ 0 ] = 70; stub_bs[ BLIS_KC ][ 0 ] = 99;
  stub_bs_max[ BLIS_MR ][ 0 ] = 7; stub_bs_max[ BLIS_NR ][ 0 ] = 5; stub_bs_max[ BLIS_MC ][ 0 ] = 70;
  stub_bs_max[ BLIS_KC ][ 0 ] = 198; }
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
	// the maxima: the configuration's where it gives one, else its default's
	printf( "d max mr %ld nr %ld mc %ld nc %ld kc %ld | s max mr %ld kc %ld\\n",
	        stub_bs_max[ BLIS_MR ][ 1 ], stub_bs_max[ BLIS_NR ][ 1 ], stub_bs_max[ BLIS_MC ][ 1 ],
	        stub_bs_max[ BLIS_NC ][ 1 ], stub_bs_max[ BLIS_KC ][ 1 ], stub_bs_max[ BLIS_MR ][ 0 ],
	        stub_bs_max[ BLIS_KC ][ 0 ] );
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
            # the maxima: MC 32 x MR and KC 512 the configuration's, NC, MR and
            # NR its defaults'; FP32's are the reference's, which differ
            self.assertIn("d max mr 8 nr 3 mc 256 nc 600 kc 512 | s max mr 7 kc 198", run({}))
            # another kernel: MR 4, so MC's maximum follows it
            self.assertIn("d max mr 4 nr 2 mc 128 nc 400 kc 512",
                          run({"BLIS_MR_D": "4", "BLIS_NR_D": "2"}))

    @needs_tools
    def test_large_tiles(self):
        # the accumulators fill the register file: C streams through the
        # epilogue, scheduled into their registers as they are consumed
        plain = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"],
                                          "params": dict(VM, **{"no-mru": True}), "m": [2], "n": [8]})
        # the cluster irmod pulls each tile's chain together before addresses
        # are fixed: even unscheduled, C streams through a few registers
        built, skipped = build_gemm("sve", "ukrgen_sve", plain)
        self.assertEqual(1, len(built), skipped)
        for params, m, n, tiles in ((dict(VM, mru=True), 2, 8, ("mr 8 nr 8", "mr 16 nr 8")),
                                    (VN, 8, 3, ("mr 8 nr 12", "mr 8 nr 24"))):
            fam = family.from_yaml("gemm", {"family": "f", "dtypes": ["FP64"], "params": params,
                                            "m": [m], "n": [n]})
            built, skipped = build_gemm("sve", "ukrgen_sve", fam)
            self.assertEqual(1, len(built), skipped)
            k = built[0]
            src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("sve")) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            outs = self.run_c("sve", src, [k], [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                              [f"-DUKR={k.symbol}", "-DWT=double"])
            for out, tile in zip(outs, tiles):
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out, k.symbol)

    @needs_tools
    def test_packm(self):
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:p"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"],
                                         "cases": [{"kind": "vec", "m": [1, 2], "params": vec}]})
        built, skipped = build_packm("sve", "ukrgen_sve", fam)
        self.assertEqual(["bli_dpackm_ukrgen_sve_p_vec1v", "bli_dpackm_ukrgen_sve_p_vec2v"],
                         [k.symbol for k in built])
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("sve")) + \
              "\n#define bli_ddpackm_ukrgen_sve_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_sve", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        outs = self.run_c("sve", src + harness, built,
                          [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                          ["-DPACKM=bli_dpackm_ukrgen_sve"])
        for out in outs:
            # three full panels by the generated cases, three by the reference
            self.assertIn("6 runs, 3 by generated cases, 0 wrong", out)

    def test_packm_masked_tail(self):
        # cdim = N*VL + M in one pass: N vectors and the last one masked to
        # the M rows left (SVE's whilelo, tail(m)) - cdim below VL too - the
        # reference only zeroing rows past cdim; exact multiples the vec
        # case's, rows past the masked cases' vec and the reference
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "cases": [
            {"kind": "vec", "m": [1, 2], "params": vec},
            {"kind": "vec", "name": "vtail", "mask": True, "m": [0, 1], "params": vec}]})
        built, skipped = build_packm("sve", "ukrgen_sve", fam)
        self.assertEqual([], skipped)
        self.assertEqual(["vec1v", "vec2v", "vtail0vt", "vtail1vt"],
                         sorted(k.symbol.rsplit("_", 1)[1] for k in built))
        self.assertTrue(all(k.tail == k.symbol.endswith("t") for k in built))
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("sve")) + \
              "\n#define bli_ddpackm_ukrgen_sve_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_sve", "FP64", built, tail="reference") + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        # cdim, cdim_max, n, inca, lda, the reference calls expected
        cases = ("{ 3, 3, 7, 1, 5, 0 }, { vl + 3, vl + 3, 9, 1, vl + 5, 0 }, "
                 "{ 2 * vl - 1, 2 * vl, 6, 1, 2 * vl + 2, 1 }, { vl, vl, 5, 1, vl + 3, 0 }, "
                 "{ 2 * vl + 1, 2 * vl + 1, 4, 1, 2 * vl + 1, 1 }")
        outs = self.run_c("sve", src + harness, built,
                          [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                          ["-DPACKM=bli_dpackm_ukrgen_sve", f"-DCASES={cases}"])
        for out in outs:
            self.assertIn("5 runs, 3 by generated cases, 0 wrong", out)

    def test_packm_masked_tail_rvv(self):
        # RVV's masked vec cases: the last vector's load and store under v0
        # (vid.v, vmsltu.vx from tail(m), set once) - cdim below a vector,
        # N*VL + M, padded; exact the vec case's, past the masked ones vec2v
        # and an overlapping vec1v - VLEN 128 and 256
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        if not (shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "cases": [
            {"kind": "vec", "m": [1, 2], "params": vec},
            {"kind": "vec", "name": "vtail", "mask": True, "m": [0, 1], "params": vec}]})
        built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
        self.assertEqual([], skipped)
        masked = [asm_source(k) for k in built if k.tail]
        self.assertEqual(2, len(masked))
        for asm in masked:
            self.assertIn("vid.v", asm)
            self.assertIn("vmsltu.vx v0", asm)
            self.assertIn("v0.t", asm)
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("rvv")) + \
              "\n#define bli_ddpackm_ukrgen_rvv_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_rvv", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        # cdim, cdim_max, n, inca, lda, the reference calls expected
        cases = ("{ 1, 1, 7, 1, 3, 0 }, { vl + 1, vl + 1, 9, 1, vl + 3, 0 }, "
                 "{ 2 * vl - 1, 2 * vl, 6, 1, 2 * vl + 2, 1 }, { vl, vl, 5, 1, vl + 3, 0 }, "
                 "{ 2 * vl + 1, 2 * vl + 1, 4, 1, 2 * vl + 1, 0 }")
        outs = self.run_c("rvv", src + harness, built,
                          [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                          ["-DPACKM=bli_dpackm_ukrgen_rvv", f"-DCASES={cases}"], cc=cc)
        for out in outs:
            self.assertIn("5 runs, 4 by generated cases, 0 wrong", out)

    def test_packm_masked_tail_rvv_vl(self):
        # RVV's other route (tailmask route vl): the last vector at the tail's
        # vector length between lsc_states - vsetvli zero, tail, then vsetvli
        # t, zero - not masked, v0 free. Preloaded, each last-vector access its
        # own short region; its own registers, not preloaded, a column's load,
        # multiply and store one (two switches, not four)
        from ukrgen.injectors.blis.families import build_packm
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        if not (shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        for merged in (False, True):
            with self.subTest(merged=merged):
                tail = dict(vec, **{"tailmask-route": "vl"})
                if merged:
                    tail.update({"X-data-regs": "4", "Y-data-regs": "4"})
                case = {"kind": "vec", "name": "vtail", "mask": True, "m": [0, 1], "params": tail}
                if merged:
                    case["max-preload"] = {"X": 0}
                fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "cases": [
                    {"kind": "vec", "m": [1, 2], "params": vec}, case]})
                built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
                self.assertEqual([], skipped)
                self.check_vl_route(built, merged, cc)

    def check_vl_route(self, built, merged, cc):
        import re
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        # the multiply's, or the copy's (kappa 1) while it moves
        whole = ["vle64.v", "vfmul.vv", "vmv.v.v", "vse64.v"]
        merges = []
        for asm in [asm_source(k) for k in built if k.tail]:
            self.assertNotIn("v0.t", asm)
            # the schedulers keep every other vector instruction out of a region
            short, regions = False, []
            for line in (l.strip() for l in asm.split("\n")):
                if re.match(r"vsetvli zero, \w+,", line):
                    self.assertFalse(short, "two short lengths in a row")
                    short = True
                    regions.append([])
                elif re.match(r"vsetvli \w+, zero,", line):
                    short = False
                elif short and line.startswith("v"):
                    regions[-1].append(line.split()[0])
            self.assertFalse(short)
            self.assertTrue(regions and all(r for r in regions))
            # last vectors' loads, stores, multiplies only - a full vector at the
            # short length would pack wrong panels, which the runs below catch
            self.assertTrue(all(set(r) <= set(whole) for r in regions), regions)
            merges.append(any(len(r) > 1 for r in regions))
        # regions merged somewhere: a pipelined loop's store and next load
        # (merge_switches), or a column's load, multiply and store (tailmask)
        self.assertTrue(any(merges))
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("rvv")) + \
              "\n#define bli_ddpackm_ukrgen_rvv_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_rvv", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        cases = ("{ 1, 1, 7, 1, 3, 0 }, { vl + 1, vl + 1, 9, 1, vl + 3, 0 }, "
                 "{ 2 * vl - 1, 2 * vl, 6, 1, 2 * vl + 2, 1 }, { vl, vl, 5, 1, vl + 3, 0 }, "
                 "{ 2 * vl + 1, 2 * vl + 1, 4, 1, 2 * vl + 1, 0 }")
        outs = self.run_c("rvv", src + harness, built,
                          [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                          ["-DPACKM=bli_dpackm_ukrgen_rvv", f"-DCASES={cases}"], cc=cc)
        for out in outs:
            self.assertIn("5 runs, 4 by generated cases, 0 wrong", out)

    def test_packm_sme_scatters_need_fa64(self):
        # streaming mode runs scatters only with FEAT_SME_FA64 (asmgen: their
        # signatures require sm == 0 without it): the SME trans case's
        # scatters - the kernel in streaming mode (sm = 1) - refused where a
        # config says FA64 is off (Apple's parts), built where it's on (LX2's)
        import copy
        from ukrgen.injectors.blis.families import configuration, build_packm
        # LX2's config keeps its scatter case (the Apple-safe one has none left)
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(HERE, "..", "..", "ukrconfig", "smesve",
                                                                        "fopa_fma_split", "dpackm.yaml")})
        base = cfg.families[0]
        for fa64, expect in (("on", 1), ("off", 0)):
            fam = copy.deepcopy(base)
            fam.cases = [(c, [4], dict(p, **{"sme-FA64": fa64})) for c, _, p in base.cases if "trans" == c]
            built, skipped = build_packm(cfg.isa, cfg.name, fam)
            with self.subTest(fa64=fa64):
                self.assertEqual(expect, len(built))
                if not built:
                    self.assertIn("no form whose state requirements hold (sm ==0", str(skipped[0][2]))

    def packm_ztrans(self, sizes, cases, svls=(256, 512), ylayout=("m:c", "n:p"), extra=None, tail="overlap",
                     mask=False):
        # SME's ZA transpose: A's rows scaled and moved into a tile's horizontal
        # slices, its vertical slices stored as P's columns - through BLIS's
        # dispatch against the reference under qemu
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        cc = ["aarch64-linux-gnu-gcc", "-static", "-Wa,-march=armv9-a+sme+sme-f64f64"]
        if not (shutil.which(cc[0]) and shutil.which(QEMU)):
            self.skipTest("needs aarch64-linux-gnu-gcc and qemu-aarch64-static")
        ztrans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.TILE:>slice_vec_row){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.TILE:>slice_vec_row){m=1, i=n}"],
                  "store-tileop": ["Y.TILE:slices_col"], "X-layout": ["n:c", "m:s"], "Y-layout": list(ylayout),
                  "sme-F64F64": "on"}
        ztrans.update(extra or {})
        case = {"kind": "trans", "name": "ztrans", "m": list(sizes), "params": ztrans}
        if mask:
            case["mask"] = True
        fam = family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], "cases": [case]})
        built, skipped = build_packm("sme", "ukrgen_sme", fam)
        self.assertEqual([], skipped)
        for k in built:
            self.assertNotIn("[x2, z", asm_source(k))       # no scatters
        helper = vl_helpers(built, make_generator("sme")).replace('"smstart', '".arch_extension sme\\n\\tsmstart', 1)
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + helper + \
              "\n#define bli_ddpackm_ukrgen_sme_ref REF\n" + "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_sme", "FP64", built, tail=tail) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        outs = self.run_c("sme", src + harness, built, [[QEMU, "-cpu", f"max,sme=on,sme{v}=on"] for v in svls],
                          ["-DPACKM=bli_dpackm_ukrgen_sme", f"-DCASES={cases}"], cc=cc)
        return outs

    def test_packm_ztrans_chunks(self):
        # a tile stored inside n's loop: each slice loop steps its address back
        # by its walk - one chunk of columns (only the last iteration), two,
        # three, four, five with a column over, two with three over
        cases = ("{ vl, vl, vl, vl + 1, 1, 0 }, { vl, vl, 2 * vl, 3 * vl, 1, 0 }, "
                 "{ vl, vl, 3 * vl, 3 * vl, 1, 0 }, { vl, vl, 4 * vl, 4 * vl + 1, 1, 0 }, "
                 "{ vl, vl, 5 * vl + 1, 6 * vl, 1, 1 }, { vl, vl, 2 * vl + 3, 3 * vl, 1, 1 }")
        for out in self.packm_ztrans([1], cases):
            self.assertIn("6 runs, 4 by generated cases, 0 wrong", out)

    def test_packm_ztrans_tiles(self):
        # sized in tiles - VL, 2*VL, 4*VL rows, za0.d to za3.d - the tiles'
        # loops over slices fused (one over every tile's rows, one over their
        # columns) inside n's loop: the loops' copies in its last iteration
        # their own operations, not the body's
        cases = ("{ vl, vl, 2 * vl, 3 * vl, 1, 0 }, { 2 * vl, 2 * vl, 2 * vl + 1, 3 * vl, 1, 1 }, "
                 "{ 4 * vl, 4 * vl, 3 * vl, 3 * vl, 1, 0 }, { 2 * vl, 2 * vl, vl, vl, 1, 0 }, "
                 "{ 4 * vl, 4 * vl, vl + 2, 2 * vl, 1, 1 }")
        for out in self.packm_ztrans([1, 2, 4], cases):
            self.assertIn("5 runs, 3 by generated cases, 0 wrong", out)

    def test_packm_ztrans_fused(self):
        from ukrgen.injectors.blis.families import build_packm
        ztrans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.TILE:>slice_vec_row){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.TILE:>slice_vec_row){m=1, i=n}"],
                  "store-tileop": ["Y.TILE:slices_col"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"],
                  "sme-F64F64": "on"}
        loops = {}
        # the defaults (no list: an empty one would be no passes at all), then
        # without fuse_slices
        for irmods in (None, ["-fuse_slices"]):
            params = dict(ztrans, **({"pre-specialize-irmods": irmods} if irmods else {}))
            fam = family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], "cases": [
                {"kind": "trans", "name": "ztrans", "m": [2], "params": params}]})
            built, skipped = build_packm("sme", "ukrgen_sme", fam)
            self.assertEqual([], skipped)
            loops[bool(irmods)] = sum(1 for l in asm_source(built[0]).split("\n") if l.strip().endswith("_slices:"))
        self.assertEqual(loops[True], 2 * loops[False])

    def test_packm_ztrans_blocks(self):
        # ZA kernels taking P's leading dimension: blocks of whole tiles, any
        # cdim; the rows left - fewer than a tile - a one-tile kernel ending at
        # cdim (vec-tail overlap: tile + overlap), or the reference (tile +
        # reference); below one tile the reference either way
        for tail, refs in (("overlap", 0), ("reference", 1)):
            cases = ("{ 2 * vl, 2 * vl, 3 * vl, 3 * vl, 1, 0 }, "
                     f"{{ 2 * vl + 3, 2 * vl + 3, 3 * vl, 3 * vl, 1, {refs} }}, "
                     "{ 5 * vl, 5 * vl, 2 * vl, 2 * vl, 1, 0 }, { 3, 3, 2 * vl, 2 * vl, 1, 1 }")
            with self.subTest(tail=tail):
                for out in self.packm_ztrans([4, 2, 1], cases, ylayout=("m:c", "n:s"), tail=tail):
                    self.assertIn(f"4 runs, {3 - refs} by generated cases, 0 wrong", out)

    def test_packm_ztrans_masked(self):
        # tile + mask: whole tiles and a last one of the rows left - its row
        # loop counted tail(m) (A has no more), its column stores under the
        # mask of the first tail(m) elements (whilelo) - any cdim up to the
        # case's tiles in one call: below a tile, a tile and some, two and some
        # with a column over (the reference's), padded
        cases = ("{ 3, 3, 2 * vl, 2 * vl, 1, 0 }, { vl + 1, vl + 1, 3 * vl, 3 * vl, 1, 0 }, "
                 "{ 2 * vl + 3, 2 * vl + 3, 2 * vl + 1, 3 * vl, 1, 1 }, { vl - 1, vl, vl, vl, 1, 1 }")
        for out in self.packm_ztrans([0, 1, 2], cases, ylayout=("m:c", "n:s"), mask=True):
            self.assertIn("4 runs, 2 by generated cases, 0 wrong", out)

    def test_packm_ztrans_tile_limits(self):
        # the tiles an element type has - eight of doubles, four of singles -
        # and max-tiles under them: a case needing more refused, saying so;
        # eight tiles of doubles packing right
        from ukrgen.injectors.blis.families import build_packm
        def fam(sizes, dt="FP64", extra=None):
            z = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.TILE:>slice_vec_row){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.TILE:>slice_vec_row){m=1, i=n}"],
                 "store-tileop": ["Y.TILE:slices_col"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"]}
            if "FP64" == dt:
                z["sme-F64F64"] = "on"
            case = dict({"kind": "trans", "name": "ztrans", "m": list(sizes), "params": z}, **(extra or {}))
            return family.from_yaml("packm", {"family": "pk", "dtypes": [dt], "cases": [case]})
        for f, built_sizes, refused in ((fam([8]), [8], []), (fam([4, 5], "FP32"), [4], [5]),
                                         (fam([2, 4], extra={"max-tiles": 2}), [2], [4])):
            built, skipped = build_packm("sme", "ukrgen_sme", f)
            with self.subTest(sizes=[k.symbol for k in built]):
                self.assertEqual([f"ztrans{n}v" for n in built_sizes], [k.symbol.rsplit("_", 1)[1] for k in built])
                self.assertEqual(refused, [s[1][1] for s in skipped])
                self.assertTrue(all("no tile left" in str(s[2]) for s in skipped))
        for out in self.packm_ztrans([8], "{ 8 * vl, 8 * vl, 3 * vl, 3 * vl, 1, 0 }, { 8 * vl, 8 * vl, vl + 1, 2 * vl, 1, 1 }"):
            self.assertIn("2 runs, 1 by generated cases, 0 wrong", out)

    def test_packm_sme_configs(self):
        # the SME configs pack across the grain through ZA (ztrans, sizes in
        # tiles): the Apple-safe one (sme-FA64 off: no scatters in streaming
        # mode) with no scatter case left, LX2's (FA64 declared) with its
        # scatters for other row counts; their ztrans through BLIS's dispatch
        # against the reference under qemu
        import copy
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        root = os.path.join(HERE, "..", "..", "ukrconfig")
        for cfgdir, scatters in (("sme/fopa_bc_vindex", False), ("smesve/fopa_fma_split", True)):
            for dt, f in (("FP64", "dpackm"), ("FP32", "spackm")):
                cfg = configuration.from_files({("packm", dt): os.path.join(root, cfgdir, f + ".yaml")})
                built, skipped = build_packm(cfg.isa, cfg.name, cfg.families[0])
                names = {k.symbol.rsplit("_", 1)[1] for k in built}
                with self.subTest(config=cfgdir, f=f):
                    self.assertTrue({"ztrans1v", "ztrans2v", "ztrans3v", "ztrans4v"} <= names)
                    self.assertEqual(scatters, any(n.startswith("trans") for n in names))
                    self.assertFalse([s for s in skipped if "processor state" in str(s[2])])
        cc = ["aarch64-linux-gnu-gcc", "-static", "-Wa,-march=armv9-a+sme+sme-f64f64"]
        if not (shutil.which(cc[0]) and shutil.which(QEMU)):
            self.skipTest("needs aarch64-linux-gnu-gcc and qemu-aarch64-static")
        cases = ("{ vl, vl, 2 * vl, 3 * vl, 1, 0 }, { 2 * vl, 2 * vl, 2 * vl + 1, 3 * vl, 1, 1 }, "
                 "{ 3 * vl, 3 * vl, 5 * vl, 5 * vl, 1, 0 }, { 4 * vl, 4 * vl, vl + 2, 2 * vl, 1, 1 }, "
                 "{ 4 * vl, 4 * vl, 9 * vl, 9 * vl, 1, 0 }")
        for cfgdir, dt, f in (("sme/fopa_bc_vindex", "FP64", "dpackm"), ("smesve/fopa_fma_split", "FP32", "spackm")):
            cfg = configuration.from_files({("packm", dt): os.path.join(root, cfgdir, f + ".yaml")})
            fam = copy.deepcopy(cfg.families[0])
            fam.cases = [c for c in fam.cases if "ztrans" == c[0]]
            built, skipped = build_packm(cfg.isa, cfg.name, fam)
            ctype, ch = ("float", "s") if "FP32" == dt else ("double", "d")
            helper = vl_helpers(built, make_generator("sme")).replace('"smstart', '".arch_extension sme\\n\\tsmstart', 1)
            src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + helper + \
                  f"\n#define bli_{ch}{ch}packm_{cfg.name}_ref REF\n" + "typedef int conj_t;\ntypedef int pack_t;\n" + \
                  "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
                  "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
                  packm_dispatch(cfg.name, dt, built) + \
                  f"\ndim_t VL_OF( void ) {{ return ukrgen_vl( sizeof( {ctype} ) ); }}\n"
            harness = open(os.path.join(HERE, "packm_harness.c")).read() \
                .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
            defs = [f"-DPACKM=bli_{ch}packm_{cfg.name}", f"-DCASES={cases}"] + (["-DWT=float"] if "FP32" == dt else [])
            outs = self.run_c("sme", src + harness, built, [[QEMU, "-cpu", f"max,sme=on,sme{v}=on"] for v in (256, 512)],
                              defs, cc=cc)
            for out in outs:
                with self.subTest(config=cfgdir, dt=dt):
                    self.assertIn("5 runs, 3 by generated cases, 0 wrong", out)

    def test_packm_masked_tail_avx512(self):
        # AVX-512's masked vec cases, run here: the last vector's vmovupd
        # under a k mask (movq, bzhiq, kmovw from tail(m) - the 7th argument,
        # on the stack, loaded at entry) - cdim below a vector, N*VL + M,
        # padded; exact the vec case's, past the masked ones vec2v and an
        # overlapping vec1v
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        from tests.specializers.test_native import cpu_has
        if not (cpu_has("avx512f") and cpu_has("bmi2")):
            self.skipTest("needs AVX512F and BMI2")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "cases": [
            {"kind": "vec", "m": [1, 2], "params": vec},
            {"kind": "vec", "name": "vtail", "mask": True, "m": [0, 1], "params": vec}]})
        built, skipped = build_packm("avx512", "ukrgen_avx512", fam)
        self.assertEqual([], skipped)
        masked = [asm_source(k) for k in built if k.tail]
        self.assertEqual(2, len(masked))
        for asm in masked:
            self.assertIn("bzhiq", asm)
            self.assertIn("{z}", asm)
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("avx512")) + \
              "\n#define bli_ddpackm_ukrgen_avx512_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_avx512", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return 8; }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        # cdim, cdim_max, n, inca, lda, the reference calls expected
        cases = ("{ 1, 1, 7, 1, 3, 0 }, { vl + 1, vl + 1, 9, 1, vl + 3, 0 }, "
                 "{ 2 * vl - 1, 2 * vl, 6, 1, 2 * vl + 2, 1 }, { vl, vl, 5, 1, vl + 3, 0 }, "
                 "{ 2 * vl + 1, 2 * vl + 1, 4, 1, 2 * vl + 1, 0 }")
        outs = self.run_c("avx512", src + harness, built, [[]],
                          ["-DPACKM=bli_dpackm_ukrgen_avx512", f"-DCASES={cases}"], cc=["gcc", "-mavx512f"])
        for out in outs:
            self.assertIn("5 runs, 4 by generated cases, 0 wrong", out)

    def test_vl_needs_its_function(self):
        # a blocksize with VL in C needs the kernel's own vector length
        # function, vl_helpers' - an RVV LMUL's VL its group's, not a
        # register's: unnamed, refused (ukropt's dispatch read ukrgen_vl's)
        from ukrgen.injectors.blis.cgen import c_expr
        self.assertEqual("8", c_expr("8", "double"))
        self.assertEqual("2*ukrgen_vl_1( sizeof( double ) )", c_expr("2*VL", "double", "ukrgen_vl_1"))
        with self.assertRaises(ValueError) as caught:
            c_expr("2*VL", "double")
        self.assertIn("vl_helpers first", str(caught.exception))

    def test_packm_branch_loops(self):
        # a branch whose cases loop (packm's kappa == 1 copy and its multiply,
        # each over n): the loop order each index once, each case's loop its
        # own counters - kappa 1 running the copy, 2 the multiply, each against
        # the reference (AVX2, natively)
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch
        from tests.specializers.test_native import cpu_has
        if not (cpu_has("avx2") and shutil.which("gcc")):
            self.skipTest("needs AVX2 and gcc")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "cases": [
            {"kind": "vec", "m": [1, 2], "params": vec}]})
        built, skipped = build_packm("avx256", "ukrgen_avx2", fam)
        self.assertEqual([], skipped)
        for k in built:
            asm = asm_source(k)
            self.assertIn("_case1:", asm)
            self.assertEqual(2, sum(1 for l in asm.split("\n") if l.strip().endswith("_loop:")))
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              "\n#define bli_ddpackm_ukrgen_avx2_ref REF\n" + "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_avx2", "FP64", built) + "\ndim_t VL_OF( void ) { return 4; }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        cases = "{ vl, vl, 7, 1, vl + 3, 0 }, { 2 * vl, 2 * vl, 5, 1, 2 * vl, 0 }"
        for kappa in (1, 2):
            with self.subTest(kappa=kappa):
                outs = self.run_c("avx256", src + harness, built, [[]],
                                  ["-DPACKM=bli_dpackm_ukrgen_avx2", f"-DCASES={cases}", f"-DKAPPA={kappa}"],
                                  cc=["gcc", "-mavx2", "-mfma"])
                for out in outs:
                    self.assertIn("2 runs, 2 by generated cases, 0 wrong", out)

    def test_packm_lmul_by_size(self):
        # RVV's vec cases at LMUL 2 where it divides their vectors, 1 where it
        # doesn't: 2v and 4v one and two m2 groups, 1v and 3v m1 - each its
        # vector length's function, the dispatch by rows - against the
        # reference at two VLENs
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        if not (shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:p"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"],
                                         "cases": [{"kind": "vec", "m": [1, 2, 3, 4], "lmul": 2, "params": vec}]})
        built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
        self.assertEqual([], skipped)
        self.assertEqual({"vec1v": 1, "vec2v": 2, "vec3v": 1, "vec4v": 2},
                         {k.symbol.rsplit("_", 1)[1]: k.lmul for k in built})
        for k in built:
            self.assertEqual(2 == k.lmul, ", m2" in asm_source(k), k.symbol)
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("rvv")) + \
              "\n#define bli_ddpackm_ukrgen_rvv_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_rvv", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        outs = self.run_c("rvv", src + harness, built,
                          [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                          ["-DPACKM=bli_dpackm_ukrgen_rvv"], cc=cc)
        for out in outs:
            self.assertIn("6 runs, 3 by generated cases, 0 wrong", out)

    def test_packm_trans(self):
        # vectors along the panel, counted in chunks of a vector length,
        # unrolled with a tail; the last partial chunk the reference's. Each
        # vector stored into the packed panel a cdim apart: RVV's strided
        # store, SVE's scatter
        self.packm_trans()

    def test_packm_trans16(self):
        # 16 rows: X's and Y's rings a register a row by default, with kappa's
        # broadcast and the scatter's index more than 32 - X's ring halved
        # where the registers ran out (it only streams through)
        self.packm_trans(m=16)

    def test_packm_trans_structfuse(self):
        # the rows' vectors stored interleaved, one structure store a step:
        # SVE's st3d, RVV's vsseg3e64.v - the same panels
        self.packm_trans(irmods=["structfuse", "hoist", "cluster"],
                         expect={"sve": "st3d", "rvv": "vsseg3e64.v"})

    def test_packm_trans_fixed_length(self):
        # AVX-512: vectors along the panel of a fixed length - the loop counts
        # chunks of it as RVV's and SVE's do, the reference takes what's left
        # (it went unpacked: the dispatch passed the kernel every column)
        from tests.specializers.test_native import cpu_has
        isas = {"avx512": ("Y.VEC:scatter", ["gcc", "-mavx512f"], [[]], cpu_has("avx512f"))}
        for m in (3, 8):
            with self.subTest(m=m):
                self.packm_trans(m=m, isas=isas)

    def test_packm_trans_structfuse_parts(self):
        # rows beyond a structure store's most parted, each part's rows
        # interleaved into the columns a stride apart: RVV's 12 rows in 8 and
        # 4, 5 rows in 3 and 2 (fields 3), 8 rows one plain segment store
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        isas = {"rvv": ("Y.VEC:strided", cc,
                        [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                        bool(shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")))}
        for m, extra, expect in ((12, {}, ("vssseg8e64.v", "vssseg4e64.v")),
                                 (5, {"structfuse-fields": "3"}, ("vssseg3e64.v", "vssseg2e64.v")),
                                 (8, {}, ("vsseg8e64.v",))):
            for inst in expect:
                with self.subTest(m=m, inst=inst):
                    self.packm_trans(irmods=["+structfuse"], expect={"rvv": inst}, m=m, isas=isas, extra=extra)

    def test_packm_trans_structfuse_scheduled(self):
        # the K1's trans case - its schedule reorders - with structfuse: 12
        # rows in 8 and 4, the second step's 8 from row 12. Each part its
        # registers consecutive wherever its first row's is, and the fused
        # store reading every one: else a row's multiply was scheduled after
        # the store (vssseg8 v20 before vfmul v27) - wrong panels from the
        # second step on
        import copy
        from ukrgen.injectors.blis.families import configuration
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        available = bool(shutil.which(cc[0]) and shutil.which("qemu-riscv64-static"))
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(HERE, "..", "..", "ukrconfig", "rvv", "k1",
                                                                        "dpackm.yaml")})
        base = cfg.families[0]
        name, _, params = next(c for c in base.cases if "trans" == base.case_kinds.get(c[0], c[0]))
        fam = copy.deepcopy(base)
        # fields 0, whatever the config's tuning: 12 = 8 + 4
        fam.cases = [(name, [12], dict(params, **{"pre-specialize-irmods": ["+structfuse"], "X-data-regs": "4",
                                                   "structfuse-fields": "0"}))]
        self.packm_trans(m=12, fam=fam, expect={"rvv": "vssseg8e64.v"},
                         isas={"rvv": (None, cc, [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"]
                                                  for v in (128, 256)], available)})

    def test_packm_trans_structfuse_split(self):
        # parts given by row count (structfuse-split), in their order - the
        # K1 config's trans case, its schedule reordering: 12 = 4+8, 3+3+3+3;
        # a part wider than the ISA's structures refused
        import copy
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        available = bool(shutil.which(cc[0]) and shutil.which("qemu-riscv64-static"))
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(HERE, "..", "..", "ukrconfig", "rvv", "k1",
                                                                        "dpackm.yaml")})
        base = cfg.families[0]
        name, _, params = next(c for c in base.cases if "trans" == base.case_kinds.get(c[0], c[0]))
        runners = [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)]
        for split, expect in (("12=4+8", ("vssseg4e64.v", "vssseg8e64.v")), ("12=3+3+3+3", ("vssseg3e64.v",))):
            fam = copy.deepcopy(base)
            fam.cases = [(name, [12], dict(params, **{"pre-specialize-irmods": ["+structfuse"], "X-data-regs": "4",
                                                       "structfuse-split": split}))]
            for inst in expect:
                with self.subTest(split=split, inst=inst):
                    self.packm_trans(m=12, fam=fam, expect={"rvv": inst},
                                     isas={"rvv": (None, cc, runners, available)})
        fam = copy.deepcopy(base)
        fam.cases = [(name, [12], dict(params, **{"pre-specialize-irmods": ["+structfuse"],
                                                   "structfuse-split": "12=9+3"}))]
        built, skipped = build_packm(cfg.isa, cfg.name, fam)
        self.assertEqual([], built)
        self.assertIn("a part of 9 rows, the ISA's structures take 8 at most", str(skipped[0][2]))
    def test_packm_trans_blocks(self):
        # A's rows contiguous, any cdim - large vectors' 2*VL rows and more,
        # past any one trans kernel - in blocks of rows: a trans case taking
        # P's leading dimension (its segment stores strided: ldp), the
        # dispatch calling its kernels on blocks, the widest first; the
        # reference for a block's last columns (n past whole chunks) and the
        # padding - VLEN 128 and 1024 (16 doubles a vector)
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        if not (shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        trans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){m=1, i=n}"],
                 "store-tileop": ["Y.VEC:strided"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:s"],
                 "X-data-regs": "4", "pre-specialize-irmods": ["+structfuse"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "unroll": 2,
                                         "cases": [{"kind": "trans", "name": "tblock", "m": [16, 8, 4, 2, 1],
                                                    "params": trans}]})
        built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
        self.assertEqual([], skipped)
        self.assertTrue(any("vssseg8e64.v" in asm_source(k) for k in built))
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("rvv")) + \
              "\n#define bli_ddpackm_ukrgen_rvv_ref REF\n" + \
              "typedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_rvv", "FP64", built) + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        # cdim, cdim_max, n, inca, lda, the reference calls expected
        cases = ("{ 2 * vl, 2 * vl, 3 * vl, 4 * vl, 1, 0 }, { vl + 5, vl + 5, 2 * vl + 3, 3 * vl, 1, 3 }, "
                 "{ 3, 4, vl, 2 * vl, 1, 1 }")
        outs = self.run_c("rvv", src + harness, built,
                          [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 1024)],
                          ["-DPACKM=bli_dpackm_ukrgen_rvv", f"-DCASES={cases}"], cc=cc)
        for out in outs:
            self.assertIn("3 runs, 1 by generated cases, 0 wrong", out)

    def test_packm_vec_overlap(self):
        # the rows a vec case leaves - cdim = N*VL + M, the K1's A panels of
        # 14 and 6 rows - packed by a kernel of the case ending at cdim, its
        # first rows packed again (the same values): no reference, whose call
        # for 2 rows cost ~660 cycles a column on the K1; below a vector the
        # reference. vec-tail: reference keeps the reference for them
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        if not (shutil.which(cc[0]) and shutil.which("qemu-riscv64-static")):
            self.skipTest("needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        harness = open(os.path.join(HERE, "packm_harness.c")).read() \
            .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        # cdim, cdim_max, n, inca, lda, the reference calls expected
        for tail, refs, expect in (("overlap", (0, 0), "4 runs, 2 by generated cases, 0 wrong"),
                                   ("reference", (1, 1), "4 runs, 0 by generated cases, 0 wrong")):
            with self.subTest(tail=tail):
                fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "vec-tail": tail,
                                                 "cases": [{"kind": "vec", "m": [1, 3], "params": vec}]})
                built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
                self.assertEqual([], skipped)
                src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
                      vl_helpers(built, make_generator("rvv")) + \
                      "\n#define bli_ddpackm_ukrgen_rvv_ref REF\n" + \
                      "typedef int conj_t;\ntypedef int pack_t;\n" + \
                      "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
                      "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
                      packm_dispatch("ukrgen_rvv", "FP64", built, tail=fam.vec_tail) + \
                      "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n"
                cases = (f"{{ 3 * vl + 2, 3 * vl + 2, 9, 1, 3 * vl + 5, {refs[0]} }}, "
                         f"{{ vl + 2, vl + 2, 7, 1, vl + 2, {refs[1]} }}, "
                         "{ vl - 1, vl - 1, 5, 1, vl, 1 }, "
                         f"{{ 3 * vl + 1, 3 * vl + 3, 6, 1, 3 * vl + 1, {1 + refs[0]} }}")
                outs = self.run_c("rvv", src + harness, built,
                                  [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                                  ["-DPACKM=bli_dpackm_ukrgen_rvv", f"-DCASES={cases}"], cc=cc)
                for out in outs:
                    self.assertIn(expect, out)

    def test_packm_trans_shufflenet(self):
        # a block of rows - as many as a vector's lanes - transposed in
        # registers, its columns stored contiguously (the shuffle stores,
        # shufflenet running for them): AVX-512's doubles in 3 rounds (AMD's
        # zen4 network), AVX2's in 2 and NEON's in 1; singles in 4, 3 and 2 -
        # the same panels as the reference's
        from tests.specializers.test_native import cpu_has
        neon_cc = ["aarch64-linux-gnu-gcc", "-static"]
        neon = bool(shutil.which(neon_cc[0]) and shutil.which(QEMU))
        runs = (("avx512", ["gcc", "-mavx512f"], [[]], cpu_has("avx512f"), {"FP64": (8, 16), "FP32": (16,)},
                 "vshuff64x2"),
                ("avx256", ["gcc", "-mavx2", "-mfma"], [[]], cpu_has("avx2"), {"FP64": (4, 8), "FP32": (8,)},
                 "vperm2f128"),
                ("neon", neon_cc, [[QEMU, "-cpu", "max"]], neon, {"FP64": (2, 4), "FP32": (4, 8)}, "trn1"))
        for isa, cc, runners, available, rows, inst in runs:
            for dt, ms in rows.items():
                for m in ms:
                    with self.subTest(isa=isa, dt=dt, m=m):
                        self.packm_trans(expect={isa: inst}, m=m, dt=dt,
                                         isas={isa: ("Y.VEC:shuffle", cc, runners, available)})

    def test_shuffle_refused(self):
        # rows not a multiple of the lanes (3 on AVX2's 4 doubles), or a
        # vector whose length isn't known (SVE): no transpose - refused
        from ukrgen.injectors.blis.families import build_packm
        trans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){m=1, i=n}"],
                 "store-tileop": ["Y.VEC:shuffle"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"]}
        for isa, m, said in (("avx256", 3, "as many rows as a vector has lanes"),
                             ("sve", 4, "the vector's length isn't known")):
            with self.subTest(isa=isa):
                fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "unroll": 2,
                                                 "cases": [{"kind": "trans", "m": [m], "params": trans}]})
                built, skipped = build_packm(isa, f"ukrgen_{isa}", fam)
                self.assertEqual([], built)
                self.assertIn(said, str(skipped[0][2]))

    def test_packm_trans_configs(self):
        # the configs' shuffle cases, doubles and singles - their own params
        # (unroll, registers) - through BLIS's dispatch against the reference
        import copy
        from tests.specializers.test_native import cpu_has
        from ukrgen.injectors.blis.families import configuration
        neon_cc = ["aarch64-linux-gnu-gcc", "-static"]
        configs = (("avx2/fma_bc_blocks", "avx256", ["gcc", "-mavx2", "-mfma"], [[]], cpu_has("avx2"), "vperm2f128"),
                   ("neon/fma_bc_lanes", "neon", neon_cc, [[QEMU, "-cpu", "max"]],
                    bool(shutil.which(neon_cc[0]) and shutil.which(QEMU)), "trn1"),
                   ("avx512/fma_bc_blocks", "avx512", ["gcc", "-mavx512f"], [[]], cpu_has("avx512f"), "vshuff64x2"))
        root = os.path.join(HERE, "..", "..", "ukrconfig")
        for path, isa, cc, runners, available, inst in configs:
            for name, dt in (("dpackm.yaml", "FP64"), ("spackm.yaml", "FP32")):
                cfg = configuration.from_files({("packm", dt): os.path.join(root, path, name)})
                base = next(f for f in cfg.families)
                for kind, ms, params in base.cases:
                    if "Y.VEC:shuffle" not in (params.get("store-tileop") or []):
                        continue
                    for m in ms:
                        with self.subTest(config=path, dt=dt, m=m):
                            fam = copy.deepcopy(base)
                            fam.cases = [(kind, [m], params)]
                            self.packm_trans(expect={isa: inst}, m=m, fam=fam, dt=dt,
                                             isas={isa: (None, cc, runners, available)})

    def packm_trans(self, irmods=None, expect=None, m=3, isas=None, fam=None, dt="FP64", extra=None):
        """
        A trans family of m rows built and run through BLIS's dispatch
        against the reference - per ISA its store, compiler, runners (an
        empty one: natively) and whether it can run here
        """
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        ctype, ch = {"FP64": ("double", "d"), "FP32": ("float", "s")}[dt]
        cases = (f"{{ {m}, {m}, 2 * vl + 3, 2 * vl + 9, 1, 1 }}, {{ {m}, {m}, 4 * vl, 4 * vl + 1, 1, 0 }}, "
                 f"{{ {m}, {m}, 3 * vl + 1, 3 * vl + 2, 1, 1 }}, {{ {m}, {m}, vl - 1, vl + 2, 1, 1 }}, "
                 f"{{ {m}, {m + 1}, 2 * vl, 2 * vl + 9, 1, 1 }}")
        if isas is None:
            rvv_cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
            isas = {"rvv": ("Y.VEC:strided", rvv_cc,
                            [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                            bool(shutil.which(rvv_cc[0]) and shutil.which("qemu-riscv64-static"))),
                    "sve": ("Y.VEC:scatter", CC, [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                            bool(shutil.which(CC[0]) and shutil.which(QEMU)))}
        ran = 0
        for isa, (store, cc, runners, available) in isas.items():
            if not available:
                continue
            ran += 1
            trans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){m=1, i=n}"],
                     "store-tileop": [store], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"]}
            if irmods is not None:
                trans["pre-specialize-irmods"] = irmods
            trans.update(extra or {})
            if m > 4:
                # Y a register a row; X streams the rows into the multiply
                trans.update({"X-data-regs": "4", "Y-data-regs": str(m)})
            built, skipped = build_packm(isa, f"ukrgen_{isa}", fam if fam is not None else family.from_yaml(
                "packm", {"family": "p", "dtypes": [dt], "unroll": 2,
                          "cases": [{"kind": "trans", "m": [m], "params": trans}]}))
            self.assertEqual(1, len(built), skipped)
            if make_generator(isa).is_vla:
                self.assertEqual("VL", built[0].loop_unit)
            src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
                  vl_helpers(built, make_generator(isa)) + \
                  f"\n#define bli_{ch}{ch}packm_ukrgen_{isa}_ref REF\ntypedef int conj_t;\ntypedef int pack_t;\n" + \
                  "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
                  "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
                  packm_dispatch(f"ukrgen_{isa}", dt, built) + \
                  f"\ndim_t VL_OF( void ) {{ return ukrgen_vl( sizeof( {ctype} ) ); }}\n" + \
                  open(os.path.join(HERE, "packm_harness.c")).read() \
                  .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
            with tempfile.TemporaryDirectory() as d:
                asm = asm_source(built[0])
                if expect:
                    self.assertIn(expect[isa], asm, isa)
                with open(os.path.join(d, "k.s"), "w") as f:
                    f.write(asm)
                subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
                with open(os.path.join(d, "t.c"), "w") as f:
                    f.write(src)
                r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DCASES={cases}",
                                         f"-DPACKM=bli_{ch}packm_ukrgen_{isa}", f"-DWT={ctype}",
                                         os.path.join(d, "t.c"),
                                         os.path.join(d, "k.o"), "-o", os.path.join(d, "run")],
                                   capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                for runner in runners:
                    out = subprocess.run(runner + [os.path.join(d, "run")], capture_output=True,
                                         text=True, timeout=60).stdout
                    self.assertIn("5 runs, 1 by generated cases, 0 wrong", out, isa)
        if not ran:
            self.skipTest(f"none of {', '.join(isas)} can run here")

    @unittest.skipUnless(shutil.which("riscv64-linux-gnu-gcc") and shutil.which("qemu-riscv64-static"),
                         "needs riscv64-linux-gnu-gcc and qemu-riscv64-static")
    def test_rvv_scalar_forms(self):
        # 8x3v and 2vx14 unrolled 4: the broadcast operand in FP registers
        # (vfmacc.vf), fitted in their own file; C's 14 columns walked by
        # one pointer beyond the few kept
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        for params, m, n, tiles in ((VNF, 8, 3, ("mr 8 nr 6", "mr 8 nr 12")),
                                    (VMF, 2, 14, ("mr 4 nr 14", "mr 8 nr 14"))):
            fam = family.from_yaml("gemm", {"family": "f", "dtypes": ["FP64"], "params": params,
                                            "m": [m], "n": [n], "unroll": 4})
            built, skipped = build_gemm("rvv", "ukrgen_rvv", fam)
            self.assertEqual(1, len(built), skipped)
            k = built[0]
            src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("rvv")) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "k.s"), "w") as f:
                    f.write(asm_source(k))
                subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
                with open(os.path.join(d, "w.c"), "w") as f:
                    f.write(src)
                r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DUKR={k.symbol}", "-DWT=double",
                                         os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                         os.path.join(d, "run")], capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                for vlen, tile in zip((128, 256), tiles):
                    out = subprocess.run(["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={vlen},elen=64",
                                          os.path.join(d, "run")], capture_output=True, text=True,
                                         timeout=120).stdout
                    self.assertIn(f"{tile}: 81 runs, 0 wrong", out, k.symbol)

    @needs_tools
    def test_split_family(self):
        # outer products and FMAs split along m, each part its preset: 2vx4v +
        # 2x4v doubles, 2vx2v + 2x2v singles (one fopa per fma); MR the parts'
        # sum, symbols naming both
        cc = ["aarch64-linux-gnu-gcc", "-static", "-Wa,-march=armv9-a+sme+sme-f64f64"]
        for dt, ctype, n, (m1, m2), symbol, tiles in (
                ("FP64", "double", 4, (2, 2), "bli_dgemm_ukrgen_sme_sf_2vx4v_2x4v",
                 ("mr 10 nr 16", "mr 18 nr 32")),
                ("FP32", "float", 2, (2, 2), "bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v",
                 ("mr 18 nr 16", "mr 34 nr 32"))):
            fam = family.from_yaml("gemm", {
                "family": "sf", "dtypes": [dt], "split": "m", "n": [n],
                "parts": [{"preset": "gemm_fopa_bc_vindex", "m": m1}, {"preset": "gemm_fma_bc", "m": m2}],
                "default": {dt: f"{m1}+{m2}x{n}"},
                "params": {"sme-F64F64": "on", "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
                           "C-layout": ["n:c", "m:s"]}})
            self.assertEqual({dt: (m1, m2, n)}, fam.default)
            built, skipped = build_gemm("sme", "ukrgen_sme", fam)
            self.assertEqual(1, len(built), skipped)
            k = built[0]
            self.assertEqual((symbol, "2*VL + 2", f"{n}*VL"), (k.symbol, k.mr, k.nr))
            # an older compiler knows no SME: the helper enables it itself
            helper = vl_helpers([k], make_generator("sme")).replace(
                '"smstart', '".arch_extension sme\\n\\tsmstart', 1)
            src = "#include \"blis_stub.h\"\n" + helper + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, ctype, k.vl_fn)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, ctype, k.vl_fn)}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "k.s"), "w") as f:
                    f.write(asm_source(k))
                subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
                with open(os.path.join(d, "w.c"), "w") as f:
                    f.write(src)
                r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DUKR={k.symbol}", f"-DWT={ctype}",
                                         os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                         os.path.join(d, "run")], capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                for svl, tile in zip((256, 512), tiles):
                    out = subprocess.run([QEMU, "-cpu", f"max,sme=on,sme{svl}=on", os.path.join(d, "run")],
                                         capture_output=True, text=True, timeout=120).stdout
                    self.assertIn(f"{tile}: 81 runs, 0 wrong", out, k.symbol)

    @needs_tools
    def test_packm_mixed_cdim(self):
        # P's leading dimension a parameter: a vec kernel packs the vectors of
        # a cdim up to PACKM_REST rows more - a split's 2*VL + 2 - the
        # reference the rows left and a narrower panel's edge
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"],
                                         "cases": [{"kind": "vec", "m": [1, 2, 4], "params": vec}]})
        built, skipped = build_packm("sve", "ukrgen_sve", fam)
        self.assertEqual(3, len(built), skipped)
        self.assertIn("stride(Y,n)", built[0].params)
        cases = ("{ 2 * vl + 2, 2 * vl + 2, 5, 1, 2 * vl + 7, 1 }, { 4 * vl, 4 * vl, 3, 1, 4 * vl + 1, 0 }, "
                 "{ 2 * vl, 2 * vl + 3, 4, 1, 2 * vl + 5, 1 }, { vl + 5, vl + 5, 2, 1, vl + 6, 1 }, "
                 "{ 4 * vl + 2, 4 * vl + 2, 3, 1, 4 * vl + 3, 1 }, { vl - 1, vl - 1, 3, 1, vl, 1 }, "
                 "{ 2 * vl, 2 * vl, 3, 2, 1, 1 }")
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("sve")) + \
              "\n#define bli_ddpackm_ukrgen_sve_ref REF\ntypedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_sve", "FP64", built, tail="reference") + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n" + \
              open(os.path.join(HERE, "packm_harness.c")).read() \
              .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        outs = self.run_c("sve", src, built, [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                          [f"-DCASES={cases}", "-DPACKM=bli_dpackm_ukrgen_sve"])
        for out in outs:
            self.assertIn("7 runs, 1 by generated cases, 0 wrong", out)

    @unittest.skipUnless("avx2" in open("/proc/cpuinfo").read() and shutil.which("gcc"), "needs an AVX2 CPU")
    def test_packm_gather(self):
        # A row-major (lda 1): its rows gathered into vectors along cdim (AVX2's
        # gathers), the kernel of the whole size first, the reference the rest
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch
        gather = {"pack-tileop": ["mul(X.VEC:gather, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"], "copy-tileop": ["move(X.VEC:gather, Y.VEC){i=m, n=1}"],
                  "store-tileop": ["Y.VEC:direct"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"],
                                         "cases": [{"kind": "gather", "m": [1, 2], "params": gather}]})
        built, skipped = build_packm("avx256", "ukrgen_avx2", fam)
        self.assertEqual(2, len(built), skipped)
        cases = ("{ vl, vl, 7, 9, 1, 0 }, { 2 * vl, 2 * vl, 5, 13, 1, 0 }, { 2 * vl + 3, 2 * vl + 3, 4, 17, 1, 1 }, "
                 "{ vl, vl + 2, 3, 11, 1, 1 }, { vl, vl, 5, 1, vl + 3, 1 }, { vl - 1, vl - 1, 3, 5, 1, 1 }")
        src = "#include <stdio.h>\n#include <stdlib.h>\n#include \"blis_stub.h\"\n" + \
              vl_helpers(built, make_generator("avx256")) + \
              "\n#define bli_ddpackm_ukrgen_avx2_ref REF\ntypedef int conj_t;\ntypedef int pack_t;\n" + \
              "void REF( conj_t, pack_t, dim_t, dim_t, dim_t, dim_t, dim_t, const void*, const void*, " \
              "inc_t, inc_t, void*, inc_t, const void*, const cntx_t* );\n" + \
              packm_dispatch("ukrgen_avx2", "FP64", built, tail="reference") + \
              "\ndim_t VL_OF( void ) { return ukrgen_vl( sizeof( double ) ); }\n" + \
              open(os.path.join(HERE, "packm_harness.c")).read() \
              .replace("typedef int conj_t;\ntypedef int pack_t;\n", "").replace("#include KERNEL_C\n", "")
        cc = ["gcc", "-mavx2", "-mfma"]
        with tempfile.TemporaryDirectory() as d:
            objs = []
            for i, k in enumerate(built):
                with open(os.path.join(d, f"k{i}.s"), "w") as f:
                    f.write(asm_source(k))
                subprocess.run(cc + ["-c", os.path.join(d, f"k{i}.s"), "-o", os.path.join(d, f"k{i}.o")], check=True)
                objs.append(os.path.join(d, f"k{i}.o"))
            with open(os.path.join(d, "t.c"), "w") as f:
                f.write(src)
            r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DCASES={cases}", "-DPACKM=bli_dpackm_ukrgen_avx2",
                                     os.path.join(d, "t.c"), *objs, "-o", os.path.join(d, "run")],
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            out = subprocess.run([os.path.join(d, "run")], capture_output=True, text=True, timeout=60).stdout
            self.assertIn("6 runs, 2 by generated cases, 0 wrong", out)

    @unittest.skipUnless("avx512f" in open("/proc/cpuinfo").read() and shutil.which("gcc"),
                         "needs an AVX-512 CPU")
    def test_any_storage(self):
        # vectors along n gathered with C's column stride, rows a row stride
        # apart: C of any storage, the temporary for edge tiles only
        import copy
        cfg = configuration.from_files({("gemm", "FP64"): os.path.join(
            os.path.dirname(HERE), os.pardir, "ukrconfig/avx512/fma_bc_vindex/dgemm.yaml")})
        vn = next(f for f in cfg.families if "vn" == f.name)
        f = copy.deepcopy(vn)
        f.sizes = {"m": [8], "n": [3]}
        built, skipped = build_gemm("avx512", "ukrgen_avx512", f)
        self.assertEqual(1, len(built), skipped)
        k = built[0]
        self.assertEqual("any", k.c_layout)
        wrapper = gemm_wrapper(k)
        self.assertIn("GEMM_UKR_SETUP_CT_ANY", wrapper)
        src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("avx512")) + wrapper + \
              f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
              f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
              open(os.path.join(HERE, "wrapper_harness.c")).read()
        cc = ["gcc", "-mavx512f", "-mavx512dq", "-mavx512vl"]
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "k.s"), "w") as fh:
                fh.write(asm_source(k))
            subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
            with open(os.path.join(d, "w.c"), "w") as fh:
                fh.write(src)
            r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DUKR={k.symbol}", "-DWT=double",
                                     os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                     os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            out = subprocess.run([os.path.join(d, "run")], capture_output=True, text=True, timeout=60).stdout
            self.assertIn("mr 8 nr 24: 81 runs, 0 wrong", out)

    def storage_kernel(self, isa, preset, storages):
        fam = family.from_yaml("gemm", {"family": "vn", "dtypes": ["FP64"], "m": [8], "n": [3],
                                        "preset": preset, "vectorize": "n", "unroll": 4,
                                        "c-storage": storages,
                                        "params": {"A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"]}})
        built, skipped = build_gemm(isa, f"ukrgen_{isa}", fam)
        self.assertEqual(1, len(built), skipped)
        k = built[0]
        # one kernel, C's parameters only: the storages' aliases take C's
        self.assertEqual(storages, k.c_storages)
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "base(alpha)", "base(beta)"],
                         [p for p in k.params if not p.startswith("stride(")])
        return k

    def run_storage_kernel(self, isa, k, cc, runners):
        src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator(isa)) + gemm_wrapper(k) + \
              f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
              f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
              open(os.path.join(HERE, "wrapper_harness.c")).read()
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "k.s"), "w") as fh:
                fh.write(asm_source(k))
            subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
            with open(os.path.join(d, "w.c"), "w") as fh:
                fh.write(src)
            r = subprocess.run(cc + ["-O1", f"-I{HERE}", f"-DUKR={k.symbol}", "-DWT=double",
                                     os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                     os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            return [subprocess.run(q + [os.path.join(d, "run")], capture_output=True, text=True,
                                   timeout=200).stdout for q in runners]

    @unittest.skipUnless("avx512f" in open("/proc/cpuinfo").read() and shutil.which("gcc"),
                         "needs an AVX-512 CPU")
    def test_storage_branches(self):
        # C's storages as branches of one kernel: row-major C with plain
        # vectors, any other gathered - or row- and column-major, the
        # temporary where neither stride is 1
        cc = ["gcc", "-mavx512f", "-mavx512dq", "-mavx512vl"]
        for storages, setup in ((["row", "any"], "GEMM_UKR_SETUP_CT_ANY"),
                                (["row", "col"], "GEMM_UKR_SETUP_CT_AMBI")):
            k = self.storage_kernel("avx512", "gemm_fma_bc_vindex", storages)
            self.assertIn(setup, gemm_wrapper(k))
            src = asm_source(k)
            # the row branch's plain stores beside the other's
            self.assertTrue(any(l.strip().startswith("vmovupd %zmm") for l in src.splitlines()))
            for out in self.run_storage_kernel("avx512", k, cc, [[]]):
                self.assertIn("mr 8 nr 24: 81 runs, 0 wrong", out, storages)

    @needs_tools
    def test_storage_branches_vla(self):
        for isa, preset, cc, runners, tiles in (
                ("sve", "gemm_fma_bc_vindex", ["aarch64-linux-gnu-gcc", "-static", "-march=armv8-a+sve"],
                 [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)], ("mr 8 nr 12", "mr 8 nr 24")),
                ("rvv", "gemm_fma_vf", ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"],
                 [["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={v},elen=64"] for v in (128, 256)],
                 ("mr 8 nr 6", "mr 8 nr 12"))):
            if not shutil.which(cc[0]):
                continue
            k = self.storage_kernel(isa, preset, ["row", "any"])
            for out, tile in zip(self.run_storage_kernel(isa, k, cc, runners), tiles):
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out, isa)

    def test_stack_and_family_header(self):
        # what BLIS checks: MR x NR in double complex elements (16 bytes),
        # whatever the kernel's type - 2 vectors of 32 doubles (2048 bits) by 3
        fam, built = build("sve", "FP64", [2], [3])
        self.assertEqual(64 * 3 * 16, stack_buf_size("sve", None, built))
        fam, built = build("sve", "FP64", [2], [6])
        self.assertEqual(1, len(built))
        self.assertEqual(64 * 6 * 16, stack_buf_size("sve", None, built))
        self.assertEqual(65536, stack_buf_size("sve", None, built, given=65536))
        # fixed width: AVX-512's 8x3v singles, 8 x 48 - their own 1536 bytes
        # too little for BLIS's check
        fam, built = build("avx512", "FP32", [8], [3])
        self.assertEqual(1, len(built))
        self.assertEqual(8 * 48 * 16, stack_buf_size("avx512", None, built))
        header = family_header("ukrgen_sve", 12288)
        self.assertIn("#define BLIS_STACK_BUF_MAX_SIZE 12288", header)
        self.assertIn("#define BLIS_RELAX_MCNR_NCMR_CONSTRAINTS", header)


if __name__ == "__main__":
    unittest.main()


class test_vl_function_static_once(unittest.TestCase):
    """
    asmgen's get_simd_size, inline or static inline (asmgen 0.6): renamed,
    static once
    """
    def test_both_forms(self):
        from ukrgen.injectors.blis.cgen import vl_function
        for head in ("inline size_t get_simd_size()", "static inline size_t get_simd_size()"):
            with self.subTest(head=head):
                text = vl_function(head + " { return 16; }", "ukrgen_vl")
                self.assertIn("static inline size_t ukrgen_vl_bytes( void ) { return 16; }", text)
                self.assertNotIn("static static", text)

