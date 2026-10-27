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
            r = subprocess.run(cc + ["-O1", f"-I{HERE}", *defines, os.path.join(d, "w.c"), *objs,
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
              "const void*, void*, inc_t, inc_t, const auxinfo_t*, const cntx_t* );\n" + \
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
            src = "#include \"blis_stub.h\"\n" + vl_helper(make_generator("sve")) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double')}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double')}; }}\n" + \
                  open(os.path.join(HERE, "wrapper_harness.c")).read()
            outs = self.run_c("sve", src, [k], [[QEMU, "-cpu", f"max,sve{v}=on"] for v in (256, 512)],
                              [f"-DUKR={k.symbol}", "-DWT=double"])
            for out, tile in zip(outs, tiles):
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out, k.symbol)

    @needs_tools
    def test_packm(self):
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch, vl_helpers
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
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
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
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
              packm_dispatch("ukrgen_sve", "FP64", built) + \
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
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
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
        fam.cases = [(name, [12], dict(params, **{"pre-specialize-irmods": ["+structfuse"], "X-data-regs": "4"}))]
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
        trans = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"],
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
            trans = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"],
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
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
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
              packm_dispatch("ukrgen_sve", "FP64", built) + \
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
        gather = {"pack-tileop": ["fmul(X.VEC:gather, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
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
              packm_dispatch("ukrgen_avx2", "FP64", built) + \
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

