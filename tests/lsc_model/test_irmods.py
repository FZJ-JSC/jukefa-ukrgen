"""
IR modifications on the specialized IR
"""

import shutil
import unittest

from ukrgen.flow.stages.irmods import post_specialize_irmod_stage, pre_specialize_irmod_stage
from ukrgen.flow.stages.emit import emit_stage
from ukrgen.models.load_store_operations import lsc_load, lsc_addr_compute, ldst_modifier

from tests.specializers.test_signature import mm, assembles, STAGES

WITHOUT_EMIT = STAGES[:-1]


def run(irmods, **extra):
    from ukrgen.flow.ukr_context import ukr_context
    from ukrgen.flow.stage_engine import stage_engine
    import tests.specializers.test_signature as base
    stages = WITHOUT_EMIT + [post_specialize_irmod_stage, emit_stage]
    saved = base.STAGES
    base.STAGES = stages
    try:
        return mm(**{"post-specialize-irmods": irmods}, **extra)
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
        from ukrgen.flow.stages.isa_specialize import isa_specialize_stage
        import tests.specializers.test_signature as base
        saved = base.STAGES
        base.STAGES = saved[:7] + [pre_specialize_irmod_stage, isa_specialize_stage,
                                   post_specialize_irmod_stage, emit_stage]
        try:
            return base.mm(**{"mm-tileop": [self.LANE_FMA], "n": "4",
                              "pre-specialize-irmods": model_irmods, **extra})
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


class test_irmod_metadata(unittest.TestCase):

    def test_requirements(self):
        from ukrgen.irmod.lsc import lanefuse, ldinc
        neon, _ = run(["ldinc"])
        self.assertEqual([], lanefuse.unmet_requirements(neon))
        self.assertEqual([], ldinc.unmet_requirements(neon))

        class vla_gen:
            is_vla = True
        class vla_ctx:
            gen = vla_gen
        self.assertEqual(["fixed-width vectors"], lanefuse.unmet_requirements(vla_ctx))

    def test_placement(self):
        from ukrgen.irmod.lsc import irmods_at, irmod_placement
        self.assertEqual(["widen", "structfuse", "shufflenet", "tailmask", "vectorize_loops", "fuse_slices", "forward_slices", "hoist_slices",
                          "unroll_loops", "hoist", "cluster", "lanefuse"],
                         [m.name for m in irmods_at(irmod_placement.PRE_SPECIALIZE)])
        self.assertEqual(["addrmerge", "ldinc"], [m.name for m in irmods_at(irmod_placement.POST_SPECIALIZE)])

    def test_required_and_tunable(self):
        # a required modification runs whenever triggered, with its tunables
        # taken from the command line
        import ukrgen.irmod.lsc as registry
        from ukrgen.irmod.lsc.base import lsc_irmod, irmod_param, irmod_placement
        calls = []

        class marker(lsc_irmod):
            name = "marker"
            description = "records that it ran"
            placement = irmod_placement.POST_SPECIALIZE
            required = True
            params = (irmod_param("level", "how much", default=1, parse=int),)

            @classmethod
            def triggered(cls, ctx):
                return True

            def apply(self, program):
                calls.append(self.values["level"])
                return 0

        registry.IRMODS.append(marker)
        try:
            run([], **{"marker-level": "3"})
        finally:
            registry.IRMODS.remove(marker)
        self.assertEqual([3], calls)


class test_irmod_choice(unittest.TestCase):
    """an IR modification chosen that the ISA can't do, or that doesn't exist: said"""
    def build(self, irmods):
        import tests.specializers.test_pack as tp
        from ukrgen.flow.stages.stage import stage_error
        params = dict(tp.PARAMS)
        params.update({"X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"], "m": "4", "n": "1",
                       "pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"],
                       "store-tileop": ["Y.VEC:scatter"], "pre-specialize-irmods": irmods})
        saved, tp.PARAMS = tp.PARAMS, params
        try:
            with self.assertRaises(stage_error) as caught:
                tp.pack("avx512")
        finally:
            tp.PARAMS = saved
        return str(caught.exception)

    def test_unavailable(self):
        self.assertIn("structfuse isn't available for this kernel: avx512 has no structure stores",
                      self.build(["structfuse"]))

    def test_unknown(self):
        said = self.build(["nosuch"])
        self.assertIn("no IR modification nosuch", said)
        self.assertIn("shufflenet", said)


class test_irmod_changes(unittest.TestCase):
    """
    +name and -name: the defaults changed - one toggled in a sweep, the
    others still run - in the modifications' usual order
    """
    def pack(self, isa, irmods, m="3", store="Y.VEC:scatter"):
        import tests.specializers.test_pack as tp
        params = dict(tp.PARAMS)
        params.update({"X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"], "m": m, "n": "1",
                       "pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"],
                       "store-tileop": [store], "pre-specialize-irmods": irmods})
        saved, tp.PARAMS = tp.PARAMS, params
        try:
            return tp.pack(isa)
        finally:
            tp.PARAMS = saved

    def test_added_and_removed(self):
        ctx, res = self.pack("sve", ["+structfuse", "-cluster"])
        self.assertTrue(res.completed, res.output)
        self.assertTrue(any(line.startswith("st3d") for line in ctx.emitted[0].code))

    def test_a_string_of_changes(self):
        # a sweep's grid gives one value, a string: its changes by commas or spaces
        for value in ("+structfuse", "+structfuse, -cluster"):
            with self.subTest(value=value):
                ctx, res = self.pack("sve", value)
                self.assertTrue(res.completed, res.output)
                self.assertTrue(any(line.startswith("st3d") for line in ctx.emitted[0].code))

    def test_names_or_changes(self):
        from ukrgen.flow.stages.stage import stage_error
        with self.assertRaises(stage_error) as caught:
            self.pack("sve", ["structfuse", "+hoist"])
        self.assertIn("not both", str(caught.exception))
        with self.assertRaises(stage_error) as caught:
            self.pack("sve", ["+nosuch"])
        self.assertIn("no IR modification nosuch", str(caught.exception))

