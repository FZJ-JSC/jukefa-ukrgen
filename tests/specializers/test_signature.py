"""
Specializing LSC IR through operation signatures
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.layout import layout_stage
from ukrgen.flow.stages.solve import solve_stage
from ukrgen.flow.stages.dimension import dimension_stage
from ukrgen.flow.stages.sto import sto_stage
from ukrgen.flow.stages.model import model_stage
from ukrgen.flow.stages.isa_specialize import isa_specialize_stage
from ukrgen.flow.stages.emit import emit_stage
from ukrgen.models.load_store_operations import lsc_load, lsc_store, lsc_addr_compute

STAGES = [setup_stage, datatype_stage, layout_stage, solve_stage, dimension_stage, sto_stage,
          model_stage, isa_specialize_stage, emit_stage]


def mm(isa="neon", **extra):
    params = {"isa": isa, "ukr": "mm", "A-data-type": "FP64", "B-data-type": "FP64",
              "C-data-type": "FP64", "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
              "C-layout": ["m:c", "n:s"],
              "mm-to": ["fma(A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"],
              "store-to": ["C.VEC:direct"], "m": "2", "n": "2", "k": "1",
              "A-data-regs": "2", "B-data-regs": "2"}
    params.update(extra)
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    res = stage_engine(STAGES, ctx, prolog=prolog).run()
    return ctx, res


def assembles(lines, arch="armv8-a"):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "k.s")
        with open(src, "w") as f:
            f.write("\n".join(lines) + "\n")
        r = subprocess.run(["aarch64-linux-gnu-as", f"-march={arch}", src,
                            "-o", os.path.join(d, "k.o")], capture_output=True, text=True)
        return r.returncode == 0, r.stderr


class test_signature_specializer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx, cls.res = mm()
        cls.spec = cls.ctx.emitted[0]

    @unittest.skipUnless(shutil.which("aarch64-linux-gnu-as"), "needs an AArch64 assembler")
    def test_assembles(self):
        for k, n in (("1", "2"), ("3", "3")):
            with self.subTest(k=k, n=n):
                ctx, _ = mm(k=k, n=n, **{"B-data-regs": str(int(n) * int(k))})
                ok, err = assembles(ctx.emitted[0].instructions())
                self.assertTrue(ok, err)

    def test_sections(self):
        loop = self.spec.blocks[0]
        self.assertEqual("mm", loop.name)
        self.assertTrue(any(l.startswith("fmla") for l in loop.sections["body"]))
        self.assertTrue(loop.advance)

    def test_column_pointer(self):
        # C is strided along n: column 1 goes through a pointer computed once
        # from C's address register and the stride register, then reused
        store = self.spec.blocks[1].sections["body"]
        stride = self.spec.bases["stride(C,n) in bytes"]
        adds = [l for l in store if l.startswith("add") and l.endswith(stride)]
        self.assertEqual(1, len(adds))
        self.assertEqual(4, sum(l.startswith(("st1", "str")) for l in store))

    def test_bases(self):
        self.assertEqual({"A", "B", "C", "stride(C,n) in bytes"}, set(self.spec.bases))

    def test_specialized_ir(self):
        # still LSC IR: the adaptations are explicit address computations
        prog = self.ctx.programs[0]
        loop, store = prog.blocks[0], prog.blocks[1]
        # B's broadcast loads (ld1r) take no immediate offset: a scratch
        # address is set right before each that needs one
        scratch = [op for op in loop.body if isinstance(op, lsc_addr_compute)]
        self.assertTrue(scratch)
        for pos, op in enumerate(loop.body):
            if isinstance(op, lsc_addr_compute):
                nxt = loop.body[pos + 1]
                self.assertIsInstance(nxt, lsc_load)
                self.assertEqual(op.indices[1].indices, nxt.indices[0].indices)
        # C's store along its strided n: one column pointer, from C's register
        pointers = [op for op in store.body if isinstance(op, lsc_addr_compute)]
        self.assertEqual(["stride(C,n)"], [str(op.delta) for op in pointers])

    def test_print_specialized_ir(self):
        _, res = mm(**{"print-specialized-ir": True})
        self.assertFalse(res.completed)
        self.assertIn("C@a1 <- C@a0 + stride(C,n)", res.output)

    def test_scalar_broadcast(self):
        # bc_scalar: B's element into a scalar register, then broadcast - a
        # move between registers, emitted through asmgen's move signatures
        ctx, res = mm(**{"mm-to": ["fma(A.VEC:direct, B.VEC:bc_scalar, C.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed, res.output)
        body = ctx.emitted[0].blocks[0].sections["body"]
        self.assertTrue(any(l.startswith("dup ") and ".d[0]" in l for l in body))
        if shutil.which("aarch64-linux-gnu-as"):
            ok, err = assembles(ctx.emitted[0].instructions())
            self.assertTrue(ok, err)

    def test_sve(self):
        # masked signatures governed by the all-true predicate the ISA sets up,
        # offsets in vector lengths, advances by whole vectors
        ctx, res = mm(isa="sve")
        self.assertTrue(res.completed, res.output)
        p = ctx.emitted[0]
        self.assertEqual("ptrue p0.d", p.setup[0])
        body = "\n".join(p.blocks[0].sections["body"])
        self.assertIn("p0/m", body)
        self.assertRegex(body, r"ld1d \{z\d+\.d\}, p0/z, \[x\d+, #\d+, MUL VL\]")
        self.assertTrue(any(l.startswith("incb") for l in p.blocks[0].advance))
        # only the model's address registers advance
        self.assertEqual(2, len(p.blocks[0].advance))
        if shutil.which("aarch64-linux-gnu-as"):
            ok, err = assembles(p.instructions(), arch="armv8-a+sve")
            self.assertTrue(ok, err)

    BLOCK_FMA = ("fma[bdreg:BLOCKLANE+bdreg_blocksize=2](A.VEC:direct, B.VEC:bc_block, C.VEC)"
                 "{i=m, n=1, k*=1}")

    def test_sve_indexed_fma(self):
        # two consecutive B elements replicated into every 128-bit block
        # (ld1rqd), each feeding an FMA by element
        ctx, res = mm(isa="sve", n="4", **{"mm-to": [self.BLOCK_FMA]})
        self.assertTrue(res.completed, res.output)
        body = ctx.emitted[0].blocks[0].sections["body"]
        self.assertTrue(any(l.startswith("ld1rqd") for l in body))
        lanes = [l.split("[")[-1].rstrip("]") for l in body if l.startswith("fmla")]
        self.assertEqual({"0", "1"}, set(lanes))
        if shutil.which("aarch64-linux-gnu-as"):
            ok, err = assembles(ctx.emitted[0].instructions(), arch="armv8-a+sve")
            self.assertTrue(ok, err)

    def test_register_constraints(self):
        # the indexed register of fmla .d must be z0..z15: with 16
        # accumulators those registers are allocated first
        ctx, res = mm(isa="sve", m="2", n="8", **{"B-data-regs": "4", "mm-to": [self.BLOCK_FMA]})
        self.assertTrue(res.completed, res.output)
        body = ctx.emitted[0].blocks[0].sections["body"]
        indexed = {int(l.split(",")[2].split(".")[0][1:]) for l in body if l.startswith("fmla")}
        self.assertTrue(indexed and max(indexed) <= 15)

    def test_print_asm(self):
        _, res = mm(**{"print-asm": True})
        self.assertFalse(res.completed)
        self.assertIn("// block mm, loop over k", res.output)


if __name__ == "__main__":
    unittest.main()
