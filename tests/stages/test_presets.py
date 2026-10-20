"""
Tile operation presets: every STO's tile operation from one name - for each
the first of the preset's alternatives the ISA offers, the variant along C's
contiguous index first, C reached across vectors (strided, gathers and
scatters, block trees) where the vectors run across it
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from ukrgen.flow import presets
from ukrgen.injectors.blis.families import run_flow

BASE = {"ukr": "gemm", "k": "1", "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"]}


def build(isa, preset, dt="FP64", c_layout=("m:c", "n:s"), m="2", n="2", **extra):
    p = dict(BASE, isa=isa, **{"tileop-preset": preset, "C-layout": list(c_layout), "m": m, "n": n})
    for comp in ("A", "B", "C", "AB", "alpha", "beta"):
        p[f"{comp}-data-type"] = dt
    p.update(extra)
    return run_flow(p)


def chosen(ctx, sto):
    return ctx.to_parts[0][sto].encoding


class test_presets(unittest.TestCase):

    def test_shipped(self):
        self.assertEqual(["gemm_fma_bc", "gemm_fma_bc_blocks", "gemm_fma_bc_lanes", "gemm_fma_bc_vindex",
                          "gemm_fma_blocklane_vindex", "gemm_fma_lane", "gemm_fma_vf",
                          "gemm_fopa_bc_vindex"],
                         presets.names())

    def test_layout_decides_the_variant(self):
        ctx, _ = build("neon", "gemm_fma_bc")
        self.assertEqual("fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}", chosen(ctx, "mm"))
        ctx, _ = build("neon", "gemm_fma_bc", c_layout=("n:c", "m:s"))
        self.assertEqual("fma(B.VEC:direct, A.VEC:bc_load, AB.VEC){m=1, i=n, k*=1}", chosen(ctx, "mm"))
        self.assertEqual("C.VEC:direct", chosen(ctx, "store"))

    def test_across_c(self):
        # vectors along n, C column-major: strided, scattered, by block trees
        for isa, preset, store in (("rvv", "gemm_fma_bc", "C.VEC:strided"),
                                   ("sve", "gemm_fma_bc_vindex", "C.VEC:scatter"),
                                   ("avx256", "gemm_fma_bc_blocks", "C.VEC:block_lanes")):
            ctx, _ = build(isa, preset, m="1", **{"tileop-vectorize": "n"})
            self.assertEqual(store, chosen(ctx, "store"), (isa, preset))

    def test_forms(self):
        ctx, _ = build("rvv", "gemm_fma_vf", c_layout=("n:c", "m:s"), m="8", n="3")
        self.assertEqual("fma[bdreg:VF](B.VEC:direct, A.FP:use_scalar, AB.VEC){m=1, i=n, k*=1}",
                         chosen(ctx, "mm"))
        for dt, size in (("FP64", 2), ("FP32", 4)):
            ctx, _ = build("sve", "gemm_fma_blocklane_vindex", dt=dt)
            self.assertIn(f"BLOCKLANE+bdreg_blocksize={size}](A.VEC:direct, B.VEC:bc_block",
                          chosen(ctx, "mm"))
        for c_layout, slices in ((("m:c", "n:s"), "slices_col"), (("n:c", "m:s"), "slices_row")):
            ctx, _ = build("sme", "gemm_fopa_bc_vindex", c_layout=c_layout, n="4",
                           **{"sme-F64F64": "on"})
            self.assertEqual(f"C.TILE:{slices}", chosen(ctx, "store"))

    def test_given_wins_and_errors(self):
        ctx, _ = build("neon", "gemm_fma_bc", **{"store-tileop": ["C.VEC:direct"]})
        self.assertEqual("C.VEC:direct", chosen(ctx, "store"))
        with self.assertRaisesRegex(Exception, "no tile operation preset"):
            build("neon", "gemm_nothing")
        with self.assertRaisesRegex(Exception, "no variant vectorizing k"):
            build("neon", "gemm_fma_bc", **{"tileop-vectorize": "k"})

    @unittest.skipUnless(shutil.which("aarch64-linux-gnu-gcc") and shutil.which("qemu-aarch64-static"),
                         "needs aarch64-linux-gnu-gcc and qemu-aarch64-static")
    def test_scattered_kernel_runs(self):
        # through BLIS's microkernel wrapper: C column-major reached by
        # gathers and scatters, vectors along n
        from ukrgen.injectors.blis.families import family, build_gemm
        from ukrgen.injectors.blis.cgen import gemm_wrapper, asm_source, vl_helpers, c_expr
        from ukrgen.flow.isa_map import make_generator
        here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "injectors")
        fam = family.from_yaml("gemm", {"family": "x", "dtypes": ["FP64"], "m": [2], "n": [2],
                                        "preset": "gemm_fma_bc_vindex", "vectorize": "n",
                                        "params": {"A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
                                                   "C-layout": ["m:c", "n:s"]}})
        built, skipped = build_gemm("sve", "ukrgen_sve", fam)
        self.assertEqual(1, len(built), skipped)
        k = built[0]
        self.assertEqual("col", k.c_layout)
        cc = ["aarch64-linux-gnu-gcc", "-static", "-march=armv8-a+sve"]
        src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("sve")) + gemm_wrapper(k) + \
              f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
              f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
              open(os.path.join(here, "wrapper_harness.c")).read()
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "k.s"), "w") as f:
                f.write(asm_source(k))
            subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
            with open(os.path.join(d, "w.c"), "w") as f:
                f.write(src)
            r = subprocess.run(cc + ["-O1", f"-I{here}", f"-DUKR={k.symbol}", "-DWT=double",
                                     os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                     os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for svl, tile in ((256, "mr 2 nr 8"), (512, "mr 2 nr 16")):
                out = subprocess.run(["qemu-aarch64-static", "-cpu", f"max,sve{svl}=on",
                                      os.path.join(d, "run")], capture_output=True, text=True,
                                     timeout=120).stdout
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out)

    @unittest.skipUnless("avx2" in open("/proc/cpuinfo").read() and shutil.which("gcc"),
                         "needs an AVX2 CPU")
    def test_block_trees_run(self):
        # 4x3v and 2x6v: C reached by block trees, the epilogue's chains
        # pulled together (cluster irmod), their scratch their own
        from ukrgen.injectors.blis.families import family, build_gemm
        from ukrgen.injectors.blis.cgen import gemm_wrapper, asm_source, vl_helpers, c_expr
        from ukrgen.flow.isa_map import make_generator
        here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "injectors")
        cc = ["gcc", "-mavx2", "-mfma"]
        for m, n, tile in ((4, 3, "mr 4 nr 12"), (2, 6, "mr 2 nr 24")):
            fam = family.from_yaml("gemm", {"family": "bt", "dtypes": ["FP64"], "m": [m], "n": [n],
                                            "preset": "gemm_fma_bc_blocks", "vectorize": "n",
                                            "params": {"A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
                                                       "C-layout": ["m:c", "n:s"]}})
            built, skipped = build_gemm("avx256", "ukrgen_avx2", fam)
            self.assertEqual(1, len(built), skipped)
            k = built[0]
            src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("avx256")) + gemm_wrapper(k) + \
                  f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
                  f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
                  open(os.path.join(here, "wrapper_harness.c")).read()
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "k.s"), "w") as f:
                    f.write(asm_source(k))
                subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
                with open(os.path.join(d, "w.c"), "w") as f:
                    f.write(src)
                r = subprocess.run(cc + ["-O1", f"-I{here}", f"-DUKR={k.symbol}", "-DWT=double",
                                         os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                         os.path.join(d, "run")], capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
                out = subprocess.run([os.path.join(d, "run")], capture_output=True, text=True,
                                     timeout=60).stdout
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out)


if __name__ == "__main__":
    unittest.main()
