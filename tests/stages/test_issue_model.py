"""
The issue model: what a core issues a cycle, and the scheduler placing
instructions cycle by cycle by it
"""

import copy
import os
import shutil
import subprocess
import tempfile
import unittest

from ukrgen.schedulers.issue import issue_model

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class test_issue_model(unittest.TestCase):

    def test_slots(self):
        # the K1's: vector loads, stores and FP operations one a cycle, a
        # scalar load and an integer operation beside it, two a cycle
        m = issue_model("2:vl|vs|vf,sl,i")
        self.assertEqual(2, m.width)
        self.assertEqual(0, m.take("vf", set()))
        self.assertIsNone(m.take("vl", {0}))
        self.assertEqual(1, m.take("sl", {0}))
        self.assertIsNone(m.take("i", {0, 1}))
        # address arithmetic falls back to the integer slot no slot names
        self.assertEqual(2, m.take("addr", {0}))
        # a class with no slot of its own takes any free one
        self.assertEqual(1, m.take("t", {0}))
        # one class a slot: as many a cycle as slots
        self.assertEqual(7, issue_model("vl,vl,sl,vf,vf,vi,i").width)
        with self.assertRaisesRegex(ValueError, "classes are"):
            issue_model("2:vl|xx,sl")
        # forbidden pairs: a scalar load never beside a vector FP operation
        m = issue_model("2:vl|vs|vf,sl,i;vf-sl")
        self.assertIsNone(m.take("sl", {0}, {"vf"}))
        self.assertEqual(1, m.take("sl", {0}, {"vl"}))

    def test_classes(self):
        # by the registers' machine types: the K1 loop's vfmacc.vf a vector FP
        # operation, its vle a vector load, its fld a scalar one
        from ukrgen.injectors.blis.families import configuration, build_gemm
        import ukrgen.schedulers.list_scheduler as L
        from ukrgen.schedulers.issue import classify
        seen = set()
        orig = L.list_scheduler.place_cycles
        def spy(sched, ops, *a, **kw):
            seen.update(classify(op) for op in ops)
            return orig(sched, ops, *a, **kw)
        L.list_scheduler.place_cycles = spy
        try:
            cfg = configuration.from_files({("gemm", "FP64"): os.path.join(ROOT, "ukrconfig/rvv/fma_vf/dgemm.yaml")})
            vm = copy.deepcopy(next(f for f in cfg.families if "vm" == f.name))
            vm.sizes = {"m": [2], "n": [14]}
            vm.params["sched-cycle-slots"] = "2:vl|vs|vf,sl,i"
            build_gemm("rvv", "ukrgen_rvv", vm)
        finally:
            L.list_scheduler.place_cycles = orig
        self.assertTrue({"vf", "vl", "sl"} <= seen, seen)

    @unittest.skipUnless(shutil.which("riscv64-linux-gnu-gcc") and shutil.which("qemu-riscv64-static"),
                         "needs the RISC-V cross toolchain and qemu")
    def test_k1_interleaves(self):
        # 2vx14 vfmacc.vf: the B scalars' loads issue beside the FMAs - one
        # or two in a row, not fourteen - and the kernel stays exact
        from ukrgen.injectors.blis.families import configuration, build_gemm
        from ukrgen.injectors.blis.cgen import gemm_wrapper, asm_source, vl_helpers, c_expr
        from ukrgen.flow.isa_map import make_generator
        cfg = configuration.from_files({("gemm", "FP64"): os.path.join(ROOT, "ukrconfig/rvv/fma_vf/dgemm.yaml")})
        vm = copy.deepcopy(next(f for f in cfg.families if "vm" == f.name))
        vm.sizes = {"m": [2], "n": [14]}
        vm.params["sched-cycle-slots"] = "2:vl|vs|vf,sl,i"
        # the issue model alone: without the configuration's distances, which
        # hold loads 13 cycles ahead of their uses at the loop's start
        vm.params.pop("distances", None)
        built, skipped = build_gemm("rvv", "ukrgen_rvv", vm)
        self.assertEqual(1, len(built), skipped)
        k = built[0]
        body = [l.strip() for l in k.program.blocks[0].sections["body"]
                if l.strip() and not l.strip().startswith(("#", "."))]
        run = longest = 0
        for line in body:
            run = run + 1 if line.startswith("fld") else 0
            longest = max(longest, run)
        self.assertLessEqual(longest, 2)
        here = os.path.join(ROOT, "tests", "injectors")
        cc = ["riscv64-linux-gnu-gcc", "-static", "-march=rv64gcv"]
        src = "#include \"blis_stub.h\"\n" + vl_helpers([k], make_generator("rvv")) + gemm_wrapper(k) + \
              f"\ndim_t MR_OF( void ) {{ return {c_expr(k.mr, 'double', k.vl_fn)}; }}\n" \
              f"dim_t NR_OF( void ) {{ return {c_expr(k.nr, 'double', k.vl_fn)}; }}\n" + \
              open(os.path.join(here, "wrapper_harness.c")).read()
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "k.s"), "w") as fh:
                fh.write(asm_source(k))
            subprocess.run(cc + ["-c", os.path.join(d, "k.s"), "-o", os.path.join(d, "k.o")], check=True)
            with open(os.path.join(d, "w.c"), "w") as fh:
                fh.write(src)
            r = subprocess.run(cc + ["-O1", f"-I{here}", f"-DUKR={k.symbol}", "-DWT=double",
                                     os.path.join(d, "w.c"), os.path.join(d, "k.o"), "-o",
                                     os.path.join(d, "run")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for vlen, tile in ((128, "mr 4 nr 14"), (256, "mr 8 nr 14")):
                out = subprocess.run(["qemu-riscv64-static", "-cpu", f"rv64,v=true,vlen={vlen},elen=64",
                                      os.path.join(d, "run")], capture_output=True, text=True,
                                     timeout=200).stdout
                self.assertIn(f"{tile}: 81 runs, 0 wrong", out)


    def test_rates_and_occupancy(self):
        # "sl/2": the slot at most once every two cycles; "vl*2": a vector
        # load holds the vector slot two cycles
        m = issue_model("2:vl*2|vs|vf,sl/2,addr|i")
        self.assertEqual({1: 2}, m.rate)
        self.assertEqual(2, m.holds(0, "vl"))
        self.assertEqual(1, m.holds(0, "vf"))
        self.assertIsNone(m.take("sl", set(), set(), {1}))
        self.assertEqual(1, m.take("sl", set(), set(), set()))
        # placed so on the K1's 2vx14 loop
        from ukrgen.injectors.blis.families import configuration, build_gemm
        import ukrgen.schedulers.list_scheduler as L
        from ukrgen.schedulers.issue import classify
        seen = []
        orig = L.list_scheduler.place_cycles
        def spy(sched, ops, *a, **kw):
            out = orig(sched, ops, *a, **kw)
            if len(ops) > 100:
                seen.append(({j: classify(op) for j, op in enumerate(ops)}, dict(sched.cycle_of)))
            return out
        L.list_scheduler.place_cycles = spy
        try:
            cfg = configuration.from_files({("gemm", "FP64"): os.path.join(ROOT, "ukrconfig/rvv/fma_vf/dgemm.yaml")})
            vm = copy.deepcopy(next(f for f in cfg.families if "vm" == f.name))
            vm.sizes = {"m": [2], "n": [14]}
            vm.params["sched-cycle-slots"] = "2:vl*2|vs|vf,sl/2,addr|i"
            build_gemm("rvv", "ukrgen_rvv", vm)
        finally:
            L.list_scheduler.place_cycles = orig
        self.assertTrue(seen)
        classes, cycle = seen[-1]
        sl = sorted(cycle[j] for j, c in classes.items() if "sl" == c and j in cycle)
        self.assertTrue(all(b - a >= 2 for a, b in zip(sl, sl[1:])), sl[:12])
        after_vl = {cycle[j] + 1 for j, c in classes.items() if "vl" == c and j in cycle}
        self.assertFalse([j for j, c in classes.items()
                          if c in ("vf", "vl", "vs") and cycle.get(j) in after_vl])

if __name__ == "__main__":
    unittest.main()
