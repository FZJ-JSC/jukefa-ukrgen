"""
A microtile split between implementations, built into one program: SME
outer products for most of it, vector FMAs for the rest - along m (2vx4v
fmopa + 2x4v fmla) or n (2vx4v fmopa + 2vx2 fmla). The parts share what
they both load (B's vectors along an m split, A's along an n split), the
FMA part adding only its broadcasts; C split between tiles and vectors.
Run against a reference at SVL 256 and 512, scheduled with the MRU too
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest

import specializers.test_signature as t

HERE = os.path.dirname(os.path.abspath(__file__))
FOPA = "fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"
SPLIT_M = {"sme-F64F64": "on", "C-layout": ["n:c", "m:s"], "A-data-regs": None, "B-data-regs": None,
           "mm-to": [FOPA, "fma(A.VEC:bc_load, B.VEC:direct, C.VEC){m=1, i=n, k*=1}"],
           "store-to": ["C.TILE:slices_row", "C.VEC:direct"], "m": ["2", "2"], "n": ["4"]}
SPLIT_N = {"sme-F64F64": "on", "A-data-regs": None, "B-data-regs": None,
           "mm-to": [FOPA, "fma(A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"],
           "store-to": ["C.TILE:slices_col", "C.VEC:direct"], "m": ["2"], "n": ["4", "2"]}


def build(params, mru=False):
    if not mru:
        return t.mm(isa="sme", **params)
    from ukrgen.flow.stages.scheduling import schedule_stage
    j = [s.__name__ for s in t.STAGES].index("emit_stage")
    saved, t.STAGES = t.STAGES, t.STAGES[:j] + [schedule_stage] + t.STAGES[j:]
    try:
        return t.mm(isa="sme", **params, **{"mru": True})
    finally:
        t.STAGES = saved


class test_split(unittest.TestCase):

    def runs(self, ctx, defines, tiles):
        cc, qemu = "aarch64-linux-gnu-gcc", "qemu-aarch64-static"
        if not (shutil.which(cc) and shutil.which(qemu)):
            self.skipTest(f"needs {cc} and {qemu}")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ukr.s"), "w") as f:
                f.write("\n".join(ctx.emitted[0].function("ukr")) + "\n")
            r = subprocess.run([cc, "-c", "-Wa,-march=armv9-a+sme+sme-f64f64", os.path.join(d, "ukr.s"),
                                "-o", os.path.join(d, "ukr.o")], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            r = subprocess.run([cc, "-static", "-O1", "-DLDC=263", *defines,
                                os.path.join(HERE, "mm_harness.c"), os.path.join(d, "ukr.o"),
                                "-o", os.path.join(d, "run"), "-lm"], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            for svl, tile in zip((256, 512), tiles):
                r = subprocess.run([qemu, "-cpu", f"max,sme=on,sme{svl}=on", os.path.join(d, "run")],
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(0, r.returncode, r.stdout)
                self.assertIn(tile, r.stdout)
                self.assertIn(", 0 wrong", r.stdout)

    def counts(self, ctx):
        code = ctx.emitted[0].instructions()
        z = {x for l in code for x in re.findall(r"\bz(\d+)\.", l)}
        za = {x for l in code for x in re.findall(r"\bza(\d+)", l)}
        loads = sum(l.startswith("ld1d") for l in code)
        bcast = sum(l.startswith("ld1rd") for l in code)
        return len(z), len(za), loads, bcast

    def test_m(self):
        ctx, res = build(SPLIT_M)
        self.assertEqual(1, len(ctx.emitted))
        z, za, loads, bcast = self.counts(ctx)
        # 8 fmla accumulators, B's 4 vectors shared, A's 2 and 2 broadcasts
        self.assertEqual(16, z)
        self.assertEqual(8, za)
        self.assertEqual(2 * 6, loads)      # per k, twice: preloaded
        self.assertEqual(2 * 2, bcast)
        self.runs(ctx, ["-DC_ROW_MAJOR"], ["tile 10 x 16", "tile 18 x 32"])

    def test_m_mru(self):
        ctx, res = build(SPLIT_M, mru=True)
        self.assertEqual(16, self.counts(ctx)[0])
        self.runs(ctx, ["-DC_ROW_MAJOR"], ["tile 10 x 16", "tile 18 x 32"])

    def test_n(self):
        ctx, res = build(SPLIT_N)
        z, za, loads, bcast = self.counts(ctx)
        # 4 fmla accumulators, A's 2 vectors shared, B's 4 and 2 broadcasts
        self.assertEqual(12, z)
        self.assertEqual(2 * 6, loads)
        self.assertEqual(2 * 2, bcast)
        self.runs(ctx, [], ["tile 8 x 18", "tile 16 x 34"])


if __name__ == "__main__":
    unittest.main()
