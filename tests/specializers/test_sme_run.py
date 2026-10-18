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
        stores = [l for l in code[start:start + 8] if l.startswith("st1d")]
        self.assertEqual(["st1d {za0v.d[w12, 0]}", "st1d {za0v.d[w12, 1]}"],
                         [l.split(",")[0] + "," + l.split(",")[1] for l in stores])
        self.assertTrue(any(l.endswith(",#2") and "x12" in l for l in code[start:start + 8]))


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
