"""
IR modifications on the specialized IR
"""

import shutil
import unittest

from ukrgen.flow.stages.irmods import irmod_stage
from ukrgen.flow.stages.emit import emit_stage
from ukrgen.models.load_store_operations import lsc_load, lsc_addr_compute, ldst_modifier

from specializers.test_signature import mm, assembles, STAGES

WITHOUT_EMIT = STAGES[:-1]


def run(irmods, **extra):
    from ukrgen.flow.ukr_context import ukr_context
    from ukrgen.flow.stage_engine import stage_engine
    import specializers.test_signature as base
    stages = WITHOUT_EMIT + [irmod_stage, emit_stage]
    saved = base.STAGES
    base.STAGES = stages
    try:
        return mm(irmods=irmods, **extra)
    finally:
        base.STAGES = saved


def ops(ctx):
    for block in ctx.programs[0].blocks:
        for section in ("prologue", "body", "epilogue", "tail"):
            yield from getattr(block, section)


class test_ldinc(unittest.TestCase):

    def test_fuses_address_computations(self):
        plain, _ = run([], n="4")
        fused, _ = run(["ldinc"], n="4")
        before = sum(isinstance(op, lsc_addr_compute) for op in ops(plain))
        after = sum(isinstance(op, lsc_addr_compute) for op in ops(fused))
        self.assertLess(after, before)
        post = [op for op in ops(fused)
                if isinstance(op, lsc_load) and ldst_modifier.postinc in op.mods]
        self.assertTrue(post)
        # a post-increment writes its address register
        self.assertTrue(all(0 in op.writes for op in post))

    def test_emitted(self):
        ctx, _ = run(["ldinc"], n="4")
        text = "\n".join(ctx.emitted[0].instructions())
        self.assertRegex(text, r"ld1r \{v\d+\.2d\}, \[x\d+\], #8")

    @unittest.skipUnless(shutil.which("aarch64-linux-gnu-as"), "needs an AArch64 assembler")
    def test_assembles(self):
        # fewer B registers than tiles: reloads walk backwards, which ld1r cannot
        # post-increment by
        for n, k, regs in (("4", "1", "4"), ("3", "2", "6"), ("4", "1", "2"), ("4", "2", "3")):
            with self.subTest(n=n, k=k, regs=regs):
                ctx, _ = run(["ldinc"], n=n, k=k, **{"B-data-regs": regs})
                ok, err = assembles(ctx.emitted[0].instructions())
                self.assertTrue(ok, err)


class test_lanefuse(unittest.TestCase):

    LANE_FMA = "fma[bdreg:ILANE](A.VEC:direct, B.VEC:use_lane, C.VEC){i=m, n=1, k*=1}"

    def run_lanes(self, model_irmods, **extra):
        from ukrgen.flow.stages.irmods import model_irmod_stage
        from ukrgen.flow.stages.isa_specialize import isa_specialize_stage
        import specializers.test_signature as base
        saved = base.STAGES
        base.STAGES = saved[:7] + [model_irmod_stage, isa_specialize_stage, irmod_stage, emit_stage]
        try:
            return base.mm(**{"mm-to": [self.LANE_FMA], "n": "4", "model-irmods": model_irmods,
                              **extra})
        finally:
            base.STAGES = saved

    def lane_loads(self, ctx):
        return [op for op in ops(ctx) if isinstance(op, lsc_load) and ldst_modifier.lane in op.mods]

    def test_contiguous_lanes_fuse(self):
        ctx, res = self.run_lanes(["lanefuse"])
        self.assertTrue(res.completed, res.output)
        self.assertEqual([], self.lane_loads(ctx))
        unfused, _ = self.run_lanes([])
        self.assertTrue(self.lane_loads(unfused))

    def test_strided_lanes_stay(self):
        # B strided along n: its lanes are not contiguous
        ctx, res = self.run_lanes(["lanefuse"], **{"B-layout": ["k:c", "n:s"]})
        self.assertTrue(res.completed, res.output)
        self.assertTrue(self.lane_loads(ctx))

    @unittest.skipUnless(shutil.which("aarch64-linux-gnu-as"), "needs an AArch64 assembler")
    def test_assembles(self):
        for irmods, layout in ((["lanefuse"], ["n:c", "k:p"]), ([], ["n:c", "k:p"]),
                               (["lanefuse"], ["k:c", "n:s"])):
            with self.subTest(irmods=irmods, layout=layout):
                ctx, _ = self.run_lanes(irmods, **{"B-layout": layout})
                ok, err = assembles(ctx.emitted[0].instructions())
                self.assertTrue(ok, err)
