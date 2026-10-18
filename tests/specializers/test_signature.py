"""
Specializing LSC IR through operation signatures
"""

import os
import re
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
    if "x86" == arch:
        # the host assembler, the inline-assembly escapes undone
        lines = [l.replace("%%", "%").replace("%=", "0") for l in lines]
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "k.s")
            with open(src, "w") as f:
                f.write("\n".join(lines) + "\n")
            r = subprocess.run(["as", src, "-o", os.path.join(d, "k.o")],
                               capture_output=True, text=True)
            return 0 == r.returncode, r.stderr
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
        # the stride is a parameter, in the register the calling convention
        # passes it in
        stride = self.spec.params["stride(C,n)"]
        adds = [l for l in store if l.startswith("add") and l.endswith(stride)]
        self.assertEqual(1, len(adds))
        self.assertEqual(4, sum(l.startswith(("st1", "str")) for l in store))

    def test_bases(self):
        # the function's parameters, as the calling convention passes them:
        # k, the start addresses, the run-time stride
        self.assertEqual({"A", "B", "C"}, set(self.spec.bases))
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "stride(C,n)"],
                         list(self.spec.params))
        self.assertEqual(["x0", "x1", "x2", "x3", "x4"], list(self.spec.params.values()))

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

    def test_reserved_registers_untouched(self):
        # the kernel's own code: the function's boilerplate saves on the stack
        # the generator's tracker keeps sp, lr, fp and x18 out of reach
        reserved = {"sp", "x30", "x29", "x18"}
        for isa in ("neon", "sve"):
            with self.subTest(isa=isa):
                ctx, res = mm(isa=isa, m="2", n="4", k="3", **{"B-data-regs": "4"})
                self.assertTrue(res.completed, res.output)
                used = {r for line in (ctx.emitted[0].setup + ctx.emitted[0].code)
                        for r in re.findall(r"\b(x\d+|sp)\b", line)}
                self.assertFalse(used & reserved, used & reserved)

    def rvv(self, **extra):
        ctx, res = mm(isa="rvv", **{"rvv-LMUL": "1"}, **extra)
        self.assertTrue(res.completed, res.output)
        lines = ctx.emitted[0].instructions()
        if shutil.which("riscv64-linux-gnu-as"):
            with tempfile.TemporaryDirectory() as d:
                src = os.path.join(d, "k.s")
                with open(src, "w") as f:
                    f.write("\n".join(lines) + "\n")
                r = subprocess.run(["riscv64-linux-gnu-as", "-march=rv64gcv", src,
                                    "-o", os.path.join(d, "k.o")], capture_output=True, text=True)
                self.assertEqual(0, r.returncode, r.stderr)
        return ctx.emitted[0]

    def test_rvv(self):
        # the vector length is in a register: offsets and advances in vector
        # lengths add it in bytes, computed once after vsetvli
        p = self.rvv()
        self.assertTrue(p.setup[0].startswith("vsetvli"))
        self.assertTrue(any(l.startswith("slli") for l in p.setup))

    def test_rvv_vf(self):
        p = self.rvv(**{"mm-to": ["fma[bdreg:VF](A.VEC:direct, B.FP:use_scalar, C.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(any(".vf" in l for l in p.blocks[0].sections["body"]))

    def test_rvv_strided(self):
        # A strided along m: vlse with A's stride register; its second vector
        # is a vector length of strides on, vl times the stride multiplied once
        p = self.rvv(**{"A-layout": ["m:s", "k:c"],
                        "mm-to": ["fma(A.VEC:strided, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(any(l.startswith("vlse64.v") for l in p.blocks[0].sections["body"]))
        self.assertTrue(any(l.startswith("mul ") for l in p.setup))

    def gather(self, isa):
        ctx, res = mm(isa=isa, **{"A-layout": ["m:s", "k:c"],
                                  "mm-to": ["fma(A.VEC:gather, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed, res.output)
        return ctx.emitted[0]

    def test_sve_gather(self):
        # the index vector is built once from A's stride register, in bytes
        p = self.gather("sve")
        # built at the start of the region using it, before its loop
        loop = next(i for i, l in enumerate(p.code) if l.endswith("_loop:"))
        self.assertTrue(any(l.startswith("index ") for l in p.code[:loop]))
        self.assertTrue(any(", z" in l and l.startswith("ld1d") for l in p.blocks[0].sections["body"]))
        if shutil.which("aarch64-linux-gnu-as"):
            ok, err = assembles(p.instructions(), arch="armv8-a+sve")
            self.assertTrue(ok, err)

    def test_avx_gathers(self):
        # the gather clears its mask: it is set all-true before each
        for isa, reset in (("avx512", "kxnorw"), ("avx256", "vpcmpeqd")):
            with self.subTest(isa=isa):
                p = self.gather(isa)
                body = p.blocks[0].sections["body"]
                gathers = [i for i, l in enumerate(body) if l.startswith("vgather")]
                self.assertTrue(gathers)
                self.assertTrue(all(body[i - 1].startswith(reset) for i in gathers))
                self.assertTrue(all(",1)" in body[i] for i in gathers))

    def test_rvv_gather(self):
        # a gather is a choice of its own on RVV too: vid.v and vmul.vx build
        # the index vector of byte offsets, vluxei64 loads through it
        p = self.rvv(**{"A-layout": ["m:s", "k:c"],
                        "mm-to": ["fma(A.VEC:gather, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]})
        # built at the start of the region using it, before its loop
        loop = next(i for i, l in enumerate(p.code) if l.endswith("_loop:"))
        self.assertTrue(any(l.startswith("vid.v") for l in p.code[:loop]))
        self.assertTrue(any(l.startswith("vluxei64") for l in p.blocks[0].sections["body"]))

    def test_avx_block_lanes(self):
        # AVX lane loads reach the low 128-bit block and don't keep the lanes
        # above (ZEROOTHERS): each block's lanes go into a scratch in
        # increasing order, then the block is inserted
        for isa, insert in (("avx256", "vinsertf128"), ("avx512", "vinsertf32x4")):
            with self.subTest(isa=isa):
                ctx, res = mm(isa=isa, **{
                    "A-layout": ["m:s", "k:c"], "no-preload": True,
                    "mm-to": ["fma(A.VEC:block_lanes, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]})
                self.assertTrue(res.completed, res.output)
                body = ctx.emitted[0].blocks[0].sections["body"]
                loads = [l.split()[0] for l in body if l.startswith(("vmovsd", "vmovhpd"))]
                self.assertEqual(["vmovsd", "vmovhpd"] * (len(loads) // 2), loads)
                inserts = [i for i, l in enumerate(body) if l.startswith(insert)]
                self.assertTrue(inserts)
                self.assertTrue(all(body[i - 1].startswith("vmovhpd") for i in inserts))

    def test_avx512_block_lanes_256(self):
        # 128-bit blocks into a 256-bit scratch, then 256-bit inserts: two on
        # the destination per vector, each after its half is complete
        ctx, res = mm(isa="avx512", **{
            "A-layout": ["m:s", "k:c"], "no-preload": True,
            "mm-to": ["fma(A.VEC:block_lanes_256, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed, res.output)
        body = ctx.emitted[0].blocks[0].sections["body"]
        wide = [i for i, l in enumerate(body) if l.startswith("vinsertf64x4")]
        self.assertTrue(wide)
        self.assertTrue(all(body[i - 1].startswith("vinsertf32x4 $1") for i in wide))
        ok, err = assembles(ctx.emitted[0].instructions(), arch="x86")
        self.assertTrue(ok, err)

    def test_avx_block_lanes_store(self):
        # C strided both ways: each block extracted, its lanes stored; the
        # lanes walk a pointer from the column's
        for isa, extract in (("avx256", "vextractf128"), ("avx512", "vextractf32x4")):
            with self.subTest(isa=isa):
                ctx, res = mm(isa=isa, **{"C-layout": ["m:s", "n:s"],
                                          "store-to": ["C.VEC:block_lanes"]})
                self.assertTrue(res.completed, res.output)
                store = [l for l in ctx.emitted[0].blocks[1].sections["body"]
                         if l.startswith(("vextract", "vmovsd", "vmovhpd"))]
                self.assertTrue(store[0].startswith(extract))
                self.assertEqual(len(store) // 3, sum(l.startswith(extract) for l in store))
                ok, err = assembles(ctx.emitted[0].instructions(), arch="x86")
                self.assertTrue(ok, err)

    def test_print_asm(self):
        _, res = mm(**{"print-asm": True})
        self.assertFalse(res.completed)
        self.assertIn("// block mm, loop over k", res.output)


if __name__ == "__main__":
    unittest.main()
