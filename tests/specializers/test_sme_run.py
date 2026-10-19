"""
An SME FP64 mm: outer products (fmopa) into ZA tiles, the tiles zeroed,
stored slice by slice in loops over their columns - run under qemu against
a reference, the same binary at two streaming vector lengths
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = {"sme-F64F64": "on", "mm-to": ["fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"],
          "store-to": ["C.TILE:slices_col"]}


def run(**extra):
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa="sme", **PARAMS, **extra)
    finally:
        t.STAGES = saved


class test_sme_run(unittest.TestCase):

    def test_code(self):
        ctx, res = run()
        code = ctx.emitted[0].instructions()
        self.assertTrue(any(l.startswith("fmopa za0.d") for l in code))
        self.assertTrue(any(l.startswith("zero {za0.d}") for l in code))
        self.assertTrue(any(l.startswith("st1d {za0v.d[w12, 0]}") for l in code))
        # streaming mode once in, once out; the caller's d8-d15 kept by the
        # calling convention - the setup declares them clobbered
        self.assertEqual(1, sum("smstart" == l for l in code))
        self.assertEqual(1, sum("smstop" == l for l in code))
        for n in range(8, 16):
            self.assertTrue(any(l.startswith(f"str d{n},") for l in code), n)
            self.assertTrue(any(l.startswith(f"ldr d{n},") for l in code), n)
        self.assertLess(next(i for i, l in enumerate(code) if l.startswith("str d8,")),
                        code.index("smstart"))
        self.assertGreater(next(i for i, l in enumerate(code) if l.startswith("ldr d8,")),
                           code.index("smstop"))

    def test_runs(self):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        ctx, res = run()
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(C,n)"],
                         list(ctx.emitted[0].params))
        with tempfile.TemporaryDirectory() as d:
            src, obj, exe = (os.path.join(d, n) for n in ("ukr.s", "ukr.o", "run"))
            with open(src, "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            r = subprocess.run([cc, "-c", "-Wa,-march=armv9-a+sme+sme-f64f64", src, "-o", obj],
                               capture_output=True, text=True)
            if r.returncode and "sme" in r.stderr:
                self.skipTest("the assembler doesn't know SME")
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([cc, "-static", "-O1", os.path.join(HERE, "mm_harness.c"), obj,
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for svl, tile in ((256, "tile 8 x 8"), (512, "tile 16 x 16")):
                r = subprocess.run([qemu, "-cpu", f"max,sme=on,sme{svl}=on", exe],
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)


    def test_unrolled(self):
        # two columns an iteration: the slice immediates 0 and 1 off w12
        ctx, res = run(**{"C-subtiling": "slices_col:unroll=2"})
        code = ctx.emitted[0].instructions()
        start = next(i for i, l in enumerate(code) if l.endswith("_slices:"))
        end = next(i for i, l in enumerate(code) if i > start and l.startswith("cbnz"))
        stores = [l.split("}")[0] + "}" for l in code[start:end] if l.startswith("st1d {za0v")]
        self.assertEqual(["st1d {za0v.d[w12, 0]}", "st1d {za0v.d[w12, 1]}"], stores)
        self.assertTrue(any(l.endswith(",#2") and "x12" in l for l in code[start:end]))


if __name__ == "__main__":
    unittest.main()


class test_required_registers(unittest.TestCase):
    """
    Registers an instruction restricts an operand to are kept for it: SME's
    slice index registers (w12-w15, from the slice operands' constraints)
    aren't taken by general allocation
    """

    def test_slice_registers_kept(self):
        ctx, res = run()
        code = ctx.emitted[0].instructions()
        words = {w for l in code for w in l.replace(",", " ").replace("[", " ").replace("]", " ").split()}
        general = {int(w[1:]) for w in words if w[:1] == "x" and w[1:].isdigit()}
        slices = {int(l.split("[w")[1].split(",")[0]) for l in code if "za" in l and "[w" in l}
        self.assertTrue(slices <= set(range(12, 16)))
        self.assertFalse((general - slices) & set(range(12, 16)), sorted(general))


GEMM = {
    "sme-F64F64": "on", "AB-data-type": "FP64", "C-data-regs": "4",
    "A-layout": ["m:c", "k:s"], "B-layout": ["n:c", "k:s"],
    "mm-to": ["fopa(A.VEC:direct, B.VEC:direct, AB.TILE){i=m, j=n, k*=1}"],
    "store_ab-to": ["AB.TILE:slices_col"],
    "alphamul-to": ["fmul(AB.TILE:slice_vec_col[0:adreg:COL], alpha.VEC:bc_load, "
                    "C.TILE:>slice_vec_col[0:bdreg:COL]){i=m, n=1}"],
    "betascale-to": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.TILE:>slice_vec_col){i=m, n=1}"],
    "add-to": ["fadd(AB.TILE:slice_vec_col[0:adreg:COL], C.VEC:direct, "
               "C.TILE:>slice_vec_col[0:bdreg:COL]){i=m, n=1}"],
    "alphaadd-to": ["fma(AB.TILE:slice_vec_col[0:adreg:COL], alpha.VEC:bc_load, "
                    "C.TILE:direct>slice_vec_col[0:bdreg:COL]){i=m, n=1}"],
    "betaadd-to": ["fma(C.VEC:direct, beta.VEC:bc_load, "
                   "AB.TILE:slice_vec_col[0:adreg:COL]>slice_vec_col[0:bdreg:COL]){i=m, n=1}"],
    "alphascale-to": ["fma(AB.TILE:slice_vec_col[0:adreg:COL], alpha.VEC:bc_load, "
                      "C.TILE:slice_vec_col[0:adreg:COL]>slice_vec_col[0:bdreg:COL]){i=m, n=1}"],
    "store-to": ["C.TILE:slices_col"]}


class test_sme_gemm(unittest.TestCase):
    """
    gemm on SME: outer products into AB's tiles, then alpha and beta applied
    on the tiles slice by slice - each STO a loop over a tile's slices, moved
    through vectors (slice_vec) - the C tiles stored by columns; every case of
    the alpha/beta dispatch run against a reference at SVL 256 and 512
    """

    def test_runs(self):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        from specializers.test_native import header
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            ctx, res = t.mm(isa="sme", ukr="gemm", **GEMM)
        finally:
            t.STAGES = saved
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        self.assertTrue(any(l.startswith("mova z") for l in p.instructions()))
        with tempfile.TemporaryDirectory() as d:
            for name, text in (("ukr.s", "\n".join(p.function("ukr")) + "\n"),
                               ("ukr.h", header(p.params))):
                with open(os.path.join(d, name), "w") as f:
                    f.write(text)
            r = subprocess.run([cc, "-c", "-Wa,-march=armv9-a+sme+sme-f64f64",
                                os.path.join(d, "ukr.s"), "-o", os.path.join(d, "ukr.o")],
                               capture_output=True, text=True)
            if r.returncode and "sme" in r.stderr:
                self.skipTest("the assembler doesn't know SME")
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([cc, "-static", "-O1", f'-DKERNEL_H="{d}/ukr.h"',
                                os.path.join(HERE, "native_harness.c"), os.path.join(d, "ukr.o"),
                                "-o", os.path.join(d, "run"), "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for svl, tile in ((256, "tile 8 x 8"), (512, "tile 16 x 16")):
                r = subprocess.run([qemu, "-cpu", f"max,sme=on,sme{svl}=on", os.path.join(d, "run")],
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)


class test_slice_irmods(unittest.TestCase):
    """
    gemm's loops over tiles' slices fused (each tile's scaling and store in one
    pass), C stored from the vectors rather than through its tile, the tile
    writes then dead dropped, alpha's and beta's broadcasts hoisted out
    """

    def build(self, **extra):
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            ctx, res = t.mm(isa="sme", ukr="gemm", **GEMM, **extra)
        finally:
            t.STAGES = saved
        return ctx.emitted[0].instructions()

    def test_fewer(self):
        plain = self.build(**{"pre-specialize-irmods": ["hoist"]})
        fused = self.build()
        count = lambda code, f: sum(1 for l in code if f(l))
        self.assertLess(count(fused, lambda l: l.endswith("_slices:")),
                        count(plain, lambda l: l.endswith("_slices:")))
        self.assertLess(count(fused, lambda l: l.startswith("mova")),
                        count(plain, lambda l: l.startswith("mova")))
        self.assertLess(count(fused, lambda l: l.startswith("st1d {za")),
                        count(plain, lambda l: l.startswith("st1d {za")))
        self.assertLess(len(fused), len(plain))
        # across tiles: one loop over slices per case of the dispatch
        import re
        cases = sum(1 for l in fused if re.fullmatch(r"\.ukr\d+_case\d+:", l))
        self.assertEqual(cases, count(fused, lambda l: l.endswith("_slices:")))
        # no broadcast left inside a loop over slices
        inside = False
        for l in fused:
            if l.endswith("_slices:"):
                inside = True
            elif l.startswith("cbnz") and "_slices" in l:
                inside = False
            elif inside:
                self.assertFalse(l.startswith("ld1rd"), l)


class test_slice_unroll(unittest.TestCase):
    """
    Loops over slices unrolled - an iteration's slices at the immediates 0
    and 1 (doubles), their vectors in two register sets - run exactly
    """

    def test_runs(self):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        from specializers.test_native import header
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            ctx, res = t.mm(isa="sme", ukr="gemm", **GEMM, **{
                "pre-specialize-irmods": ["fuse_slices", "forward_slices", "hoist_slices",
                                          "unroll_loops", "hoist"],
                "unroll_loops-factor": "2", "unroll_loops-registers": "2"})
        finally:
            t.STAGES = saved
        code = ctx.emitted[0].instructions()
        start = next(i for i, l in enumerate(code) if l.endswith("_slices:")
                     and any(x.startswith("mova") for x in code[i:i + 20]))
        end = next(i for i, l in enumerate(code) if i > start and l.startswith("cbnz"))
        body = code[start:end]
        self.assertTrue(any("[w12,1]" in l.replace(" ", "") for l in body))
        vectors = {w for l in body for w in l.replace(",", " ").split() if w.startswith("z") and "." in w}
        self.assertGreater(len(vectors), 3)
        with tempfile.TemporaryDirectory() as d:
            for name, text in (("ukr.s", "\n".join(ctx.emitted[0].function("ukr")) + "\n"),
                               ("ukr.h", header(ctx.emitted[0].params))):
                with open(os.path.join(d, name), "w") as f:
                    f.write(text)
            r = subprocess.run([cc, "-c", "-Wa,-march=armv9-a+sme+sme-f64f64",
                                os.path.join(d, "ukr.s"), "-o", os.path.join(d, "ukr.o")],
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([cc, "-static", "-O1", f'-DKERNEL_H="{d}/ukr.h"',
                                os.path.join(HERE, "native_harness.c"), os.path.join(d, "ukr.o"),
                                "-o", os.path.join(d, "run"), "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for svl in (256, 512):
                r = subprocess.run([qemu, "-cpu", f"max,sme=on,sme{svl}=on", os.path.join(d, "run")],
                                   capture_output=True, text=True, timeout=120)
                self.assertIn(", 0 wrong", r.stdout)


GEMM_ROWS = {
    "sme-F64F64": "on", "AB-data-type": "FP64", "C-data-regs": "4",
    "A-layout": ["m:c", "k:s"], "B-layout": ["n:c", "k:s"], "C-layout": ["n:c", "m:s"],
    "mm-to": ["fopa(A.VEC:direct, B.VEC:direct, AB.TILE){i=m, j=n, k*=1}"],
    "store_ab-to": ["AB.TILE:slices_row"], "store-to": ["C.TILE:slices_row"],
    "alphamul-to": ["fmul(AB.TILE:slice_vec_row[0:adreg:ROW], alpha.VEC:bc_load, "
                    "C.TILE:>slice_vec_row[0:bdreg:ROW]){m=1, i=n}"],
    "add-to": ["fadd(AB.TILE:slice_vec_row[0:adreg:ROW], C.VEC:direct, "
               "C.TILE:>slice_vec_row[0:bdreg:ROW]){m=1, i=n}"],
    "alphaadd-to": ["fma(AB.TILE:slice_vec_row[0:adreg:ROW], alpha.VEC:bc_load, "
                    "C.TILE:direct>slice_vec_row[0:bdreg:ROW]){m=1, i=n}"],
    "betaadd-to": ["fma(C.VEC:direct, beta.VEC:bc_load, "
                   "AB.TILE:slice_vec_row[0:adreg:ROW]>slice_vec_row[0:bdreg:ROW]){m=1, i=n}"],
    "betascale-to": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.TILE:>slice_vec_row){m=1, i=n}"],
    "alphascale-to": ["fma(AB.TILE:slice_vec_row[0:adreg:ROW], alpha.VEC:bc_load, "
                      "C.TILE:slice_vec_row[0:adreg:ROW]>slice_vec_row[0:bdreg:ROW]){m=1, i=n}"]}


def run_gemm(test, params, defines=(), march="armv9-a+sme+sme-f64f64", ctype="double", **extra):
    """
    An SME gemm against the gemm harness under qemu at SVL 256 and 512
    """
    cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
    if not (shutil.which(cc) and shutil.which(qemu)):
        test.skipTest(f"needs {cc} and {qemu}")
    from specializers.test_native import header
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        ctx, res = t.mm(isa="sme", ukr="gemm", **params, **extra)
    finally:
        t.STAGES = saved
    test.assertTrue(res.completed, res.output)
    p = ctx.emitted[0]
    with tempfile.TemporaryDirectory() as d:
        for name, text in (("ukr.s", "\n".join(p.function("ukr")) + "\n"),
                           ("ukr.h", header(p.params).replace("double", ctype))):
            with open(os.path.join(d, name), "w") as f:
                f.write(text)
        r = subprocess.run([cc, "-c", f"-Wa,-march={march}",
                            os.path.join(d, "ukr.s"), "-o", os.path.join(d, "ukr.o")],
                           capture_output=True, text=True)
        test.assertEqual(0, r.returncode, r.stderr)
        r = subprocess.run([cc, "-static", "-O1", *defines, f'-DKERNEL_H="{d}/ukr.h"',
                            os.path.join(HERE, "native_harness.c"), os.path.join(d, "ukr.o"),
                            "-o", os.path.join(d, "run"), "-lm"], capture_output=True, text=True)
        test.assertEqual(0, r.returncode, r.stderr)
        outs = []
        for svl in (256, 512):
            r = subprocess.run([qemu, "-cpu", f"max,sme=on,sme{svl}=on", os.path.join(d, "run")],
                               capture_output=True, text=True, timeout=120)
            test.assertIn(", 0 wrong", r.stdout, r.stdout[:400])
            outs.append(r.stdout)
    return ctx, outs


class test_sme_rows(unittest.TestCase):
    """
    Row-major C: AB's and C's tiles reached and stored by rows, the
    operations' vectors along n, the loops walking m
    """

    def test_runs(self):
        ctx, outs = run_gemm(self, GEMM_ROWS, defines=["-DC_ROW_MAJOR"])
        self.assertEqual("stride(C,m)", list(ctx.emitted[0].params)[-1])
        code = ctx.emitted[0].instructions()
        self.assertTrue(any("h.d[w12" in l for l in code))


GEMM32 = {k: v for k, v in GEMM.items() if "sme-F64F64" != k}
GEMM32.update({k: "FP32" for k in ("A-data-type", "B-data-type", "C-data-type", "AB-data-type")})


class test_sme_fp32(unittest.TestCase):
    """
    Single precision: four tiles instead of eight, each twice as many
    elements a side - gemm's 2x2 tiles of AB take all four, C reached
    through vectors only once the loops over slices are fused
    """

    def test_gemm(self):
        ctx, outs = run_gemm(self, GEMM32, defines=["-DWT=float", "-DNT=float", "-DTOL=1e-4",
                                                    "-DNCOLS=64"],
                             march="armv9-a+sme", ctype="float")
        self.assertIn("tile 16 x 16", outs[0])
        self.assertIn("tile 32 x 32", outs[1])
        code = ctx.emitted[0].instructions()
        tiles = {w.split(".")[0].lstrip("{").rstrip("vh") for l in code
                 for w in l.replace(",", " ").split() if w.lstrip("{").startswith("za")}
        self.assertTrue(tiles <= {"za0", "za1", "za2", "za3"}, tiles)

    def test_tiles_run_out(self):
        # unfused, C's tiles would be four more than single precision has
        from ukrgen.flow.stages.stage import stage_error
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        try:
            with self.assertRaisesRegex(stage_error, "no tile left - SINGLE has 4 tiles"):
                t.mm(isa="sme", ukr="gemm", **GEMM32, **{"pre-specialize-irmods": ["hoist"]})
        finally:
            t.STAGES = saved


class test_slice_scheduling(unittest.TestCase):
    """
    Loops over slices scheduled as loop bodies: unrolled into explicit
    copies - each copy's temporaries its own, its slices at its immediate,
    its memory from its own first slice - the scheduler interleaves the
    tiles' chains and the copies
    """

    def test_interleaved(self):
        from ukrgen.flow.stages.scheduling import schedule_stage
        stages = list(t.STAGES)
        i = [x.__name__ for x in stages].index("model_stage") + 1
        stages = stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
        j = [x.__name__ for x in stages].index("emit_stage")
        saved, t.STAGES = t.STAGES, stages[:j] + [schedule_stage] + stages[j:]
        try:
            ctx, res = t.mm(isa="sme", ukr="gemm", **GEMM, **{
                "pre-specialize-irmods": ["fuse_slices", "forward_slices", "hoist_slices",
                                          "unroll_loops", "hoist"],
                "unroll_loops-factor": "2", "unroll_loops-registers": "2", "mru": True})
        finally:
            t.STAGES = saved
        code = ctx.emitted[0].instructions()
        start = next(i for i, l in enumerate(code) if l.endswith("_slices:")
                     and sum(x.startswith("mova") for x in code[i:i + 30]) >= 8)
        body = [l.split()[0] for l in code[start + 1:start + 25]]
        # every slice moved out before the first multiply: tiles and copies
        self.assertEqual(["mova"] * 8, body[:8])


class test_slice_preload(unittest.TestCase):
    """
    Loops over slices software pipelined: the first copy's slices moved out
    of the tiles before the loop and, for the next iteration, at the end of
    each; the last iteration without - exact at both vector lengths
    """

    def test_runs(self):
        ctx, outs = run_gemm(self, GEMM, **{
            "pre-specialize-irmods": ["fuse_slices", "forward_slices", "hoist_slices",
                                      "unroll_loops", "hoist"],
            "unroll_loops-factor": "2", "unroll_loops-registers": "2",
            "unroll_loops-preload": "1"})
        code = ctx.emitted[0].instructions()
        start = next(i for i, l in enumerate(code) if l.endswith("_slices:")
                     and sum(x.startswith("mova") for x in code[i:i + 30]) >= 4)
        before = [l.split()[0] for l in code[start - 8:start]]
        self.assertGreaterEqual(before.count("mova"), 4)
        self.assertEqual("fmul", code[start + 1].split()[0])
        self.assertTrue(any(l.endswith("_last:") for l in code))
