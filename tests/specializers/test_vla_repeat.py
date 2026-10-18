"""
Loops over a vector's elements, as many as it has at run time: a strided
operand filled element by element (vla_lanes) on RVV - a scalar load,
vfslide1down into the top lane - run against a reference at two VLENs
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage
from ukrgen.models.load_store_operations import lsc_loop

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = {"rvv-LMUL": "1", "A-layout": ["m:s", "k:c"],
          "mm-to": ["fma(A.VEC:vla_lanes, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]}


def run(isa="rvv", params=None, **extra):
    stages = list(t.STAGES)
    i = [x.__name__ for x in stages].index("model_stage") + 1
    saved, t.STAGES = t.STAGES, stages[:i] + [pre_specialize_irmod_stage] + stages[i:]
    try:
        return t.mm(isa=isa, **(PARAMS if params is None else params), **extra)
    finally:
        t.STAGES = saved


def emulate(test, ctx, harness, cc, march, qemu, cpus):
    if not (shutil.which(cc) and shutil.which(qemu)):
        test.skipTest(f"needs {cc} and {qemu}")
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "ukr.s"), "w") as f:
            f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
        exe = os.path.join(d, "run")
        r = subprocess.run([cc, "-static", "-O1", march, os.path.join(HERE, harness),
                            os.path.join(d, "ukr.s"), "-o", exe, "-lm"], capture_output=True, text=True)
        test.assertEqual(0, r.returncode, r.stderr)
        for cpu, tile in cpus:
            r = subprocess.run([qemu, "-cpu", cpu, exe], capture_output=True, text=True, timeout=120)
            test.assertEqual(0, r.returncode, r.stdout)
            test.assertIn(tile, r.stdout)
            test.assertIn(", 0 wrong", r.stdout)


class test_vla_repeat(unittest.TestCase):

    def test_only_on_vla(self):
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="neon", **{"A-layout": ["m:s", "k:c"], "list-to-candidates": True,
                                           "mm-to": None})
        finally:
            t.STAGES = saved
        self.assertFalse(any("vla_lanes" in l for l in res.output.splitlines()))

    def test_ir(self):
        # one lsc_loop per vector: its block, its subtiling - one element at a
        # time, as many as the vector has at run time - and its information
        ctx, res = run()
        loops = [op for b in ctx.programs[0].blocks for s in ("prologue", "body", "epilogue", "tail")
                 for op in getattr(b, s) if isinstance(op, lsc_loop)]
        self.assertTrue(loops)
        r = loops[0]
        self.assertEqual(2, len(r.block))
        self.assertTrue(r.subtiling.loop)
        self.assertEqual([1, 2], r.subtiling.count.count_unrolls(2))   # 16 bytes of doubles
        self.assertEqual(1, r.subtiling.order)
        self.assertEqual({"component": "A", "index": "m", "direction": "load"},
                         {k: v for k, v in r.info.items() if k not in ("stride", "explicit")})

    def test_loop(self):
        ctx, res = run()
        body = ctx.emitted[0].blocks[0].sections["body"]
        self.assertTrue(any(l.startswith("fld ") for l in body))
        self.assertTrue(any(l.startswith("vfslide1down.vf") for l in body))
        self.assertTrue(any(l.endswith("_elements:") for l in body))

    def test_runs(self):
        cc, qemu = "riscv64-linux-gnu-gcc", "qemu-riscv64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        ctx, res = run()
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(A,m)", "stride(C,n)"],
                         list(ctx.emitted[0].params))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            exe = os.path.join(d, "run")
            r = subprocess.run([cc, "-static", "-O1", "-march=rv64gcv",
                                os.path.join(HERE, "strided_mm_harness.c"), os.path.join(d, "ukr.s"),
                                "-o", exe, "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for vlen, tile in ((128, "tile 4 x 2"), (256, "tile 8 x 2")):
                r = subprocess.run([qemu, "-cpu", f"rv64,v=true,vlen={vlen},elen=64", exe],
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(0, r.returncode, r.stdout)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)


    def test_drain_rvv(self):
        # C stored element by element: vfmv.f.s, a scalar store, vslidedown
        ctx, res = run(params={"rvv-LMUL": "1", "C-layout": ["m:s", "n:s"],
                               "store-to": ["C.VEC:vla_lanes"]})
        self.assertTrue(res.completed, res.output)
        store = ctx.emitted[0].blocks[1].sections["body"]
        self.assertTrue(any(l.startswith("vfmv.f.s") for l in store))
        self.assertTrue(any(l.startswith("vslidedown.vi") for l in store))
        emulate(self, ctx, "strided_c_harness.c", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                "qemu-riscv64-static", [("rv64,v=true,vlen=128,elen=64", "tile 4 x 2"),
                                        ("rv64,v=true,vlen=256,elen=64", "tile 8 x 2")])

    def test_fill_sve(self):
        # insr fills into lane 0, shifting up: the walk runs backwards from
        # the last element
        ctx, res = run(isa="sve", params={"A-layout": ["m:s", "k:c"], "mm-to": PARAMS["mm-to"]})
        self.assertTrue(res.completed, res.output)
        self.assertTrue(any(l.startswith("insr") for l in ctx.emitted[0].blocks[0].sections["body"]))
        emulate(self, ctx, "strided_mm_harness.c", "aarch64-linux-gnu-gcc", "-march=armv8-a+sve",
                "qemu-aarch64-static", [("max,sve256=on", "tile 8 x 2"), ("max,sve512=on", "tile 16 x 2")])


    def test_vectorized(self):
        # the fill information is enough to turn the loop into a strided load
        ctx, res = run(**{"pre-specialize-irmods": ["hoist", "vectorize_loops"]})
        body = ctx.emitted[0].blocks[0].sections["body"]
        self.assertFalse(any(l.startswith("vfslide1down") for l in body))
        self.assertTrue(any(l.startswith("vlse64.v") and l.endswith(ctx.emitted[0].params["stride(A,m)"])
                            for l in body))
        emulate(self, ctx, "strided_mm_harness.c", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                "qemu-riscv64-static", [("rv64,v=true,vlen=256,elen=64", "tile 8 x 2")])

    def test_unrolled(self):
        # two elements an iteration: the body twice, the count stepping by 2
        ctx, res = run(**{"pre-specialize-irmods": ["hoist", "unroll_loops"]})
        body = ctx.emitted[0].blocks[0].sections["body"]
        start = next(i for i, l in enumerate(body) if l.endswith("_elements:"))
        end = next(i for i, l in enumerate(body) if i > start and l.startswith("bne"))
        self.assertEqual(2, sum(l.startswith("fld") for l in body[start:end]))
        self.assertTrue(any(l.endswith(",-2") for l in body[start:end]))
        emulate(self, ctx, "strided_mm_harness.c", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                "qemu-riscv64-static", [("rv64,v=true,vlen=128,elen=64", "tile 4 x 2"),
                                        ("rv64,v=true,vlen=256,elen=64", "tile 8 x 2")])


    def test_unrolled_registers(self):
        # two registers: both elements' loads, then both fills
        ctx, res = run(**{"pre-specialize-irmods": ["hoist", "unroll_loops"],
                          "unroll_loops-factor": "2", "unroll_loops-registers": "2"})
        body = ctx.emitted[0].blocks[0].sections["body"]
        start = next(i for i, l in enumerate(body) if l.endswith("_elements:"))
        loop = [l for l in body[start + 1:] if l.startswith(("fld", "vfslide1down"))][:4]
        self.assertEqual(["fld", "fld", "vfslide1down.vf", "vfslide1down.vf"], [l.split()[0] for l in loop])
        self.assertNotEqual(loop[0].split()[1], loop[1].split()[1])
        emulate(self, ctx, "strided_mm_harness.c", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                "qemu-riscv64-static", [("rv64,v=true,vlen=128,elen=64", "tile 4 x 2"),
                                        ("rv64,v=true,vlen=256,elen=64", "tile 8 x 2")])


    def test_subtiling_listing(self):
        ctx, res = run(**{"list-subtilings": True})
        self.assertFalse(res.completed)
        self.assertIn("A (vla_lanes, load): 1v subtiles of 1x1; unrolls 1, 2; order +1; "
                      "unroll 1, registers 1", res.output)

    def test_subtiling_override(self):
        # set per component and resolution: two elements an iteration, in two
        # registers - the unroll_loops irmod not needed
        ctx, res = run(**{"A-subtiling": "vla_lanes:unroll=2,registers=2"})
        body = ctx.emitted[0].blocks[0].sections["body"]
        start = next(i for i, l in enumerate(body) if l.endswith("_elements:"))
        loop = [l.split()[0] for l in body[start + 1:] if l.startswith(("fld", "vfslide1down"))][:4]
        self.assertEqual(["fld", "fld", "vfslide1down.vf", "vfslide1down.vf"], loop)
        emulate(self, ctx, "strided_mm_harness.c", "riscv64-linux-gnu-gcc", "-march=rv64gcv",
                "qemu-riscv64-static", [("rv64,v=true,vlen=128,elen=64", "tile 4 x 2"),
                                        ("rv64,v=true,vlen=256,elen=64", "tile 8 x 2")])

    def test_subtiling_refused(self):
        from ukrgen.flow.stages.stage import stage_error
        with self.assertRaisesRegex(stage_error, "unrolls by 1, 2, not 4"):
            run(**{"A-subtiling": "unroll=4"})
        with self.assertRaisesRegex(stage_error, "forwards only"):
            run(**{"A-subtiling": "order=-1"})
        with self.assertRaisesRegex(stage_error, "is not unroll=N"):
            run(**{"A-subtiling": "speed=11"})


if __name__ == "__main__":
    unittest.main()
