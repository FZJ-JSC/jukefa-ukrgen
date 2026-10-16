"""
Building LSC IR from tiled STOs
"""

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
from ukrgen.flow.stages.stage import stage_error
from ukrgen.lsc_model.builder import program_builder, addressing_plan, model_error
from ukrgen.lsc_model.addressing import addr_pattern
from ukrgen.lsc_model.ir import ir_mem, ir_move, ir_compute, ir_zero

TO_STAGES = [setup_stage, datatype_stage, layout_stage, solve_stage, dimension_stage, sto_stage]

FMA_M = "fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"
BETA = "fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"
ALPHA = "fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"


def run(stages=TO_STAGES, **extra):
    params = {"isa": "sve", "ukr": "gemm",
              "A-data-type": "FP64", "B-data-type": "FP64", "AB-data-type": "FP64",
              "C-data-type": "FP64", "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
              "C-layout": ["m:c", "n:s"], "mm-to": [FMA_M], "betascale-to": [BETA],
              "alphascale-to": [ALPHA], "store-to": ["C.VEC:direct"],
              "m": "2", "n": "2", "k": "1"}
    params.update(extra)
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    return ctx, stage_engine(stages, ctx, prolog=prolog).run()


def loads(ops, comp=None):
    return [op for op in ops if isinstance(op, ir_mem) and "load" == op.kind
            and (comp is None or comp == op.addr.component)]


class test_builder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx, _ = run()

    def build(self, **kw):
        kw.setdefault("addressing", {"C": addressing_plan(2, addr_pattern.parse("phase"))})
        return program_builder(self.ctx, **kw).build()

    def test_preload(self):
        prog = self.build()
        mm = prog.blocks[0]
        # the prologue zeroes the accumulators and loads the first iteration
        self.assertEqual(4, sum(isinstance(op, ir_zero) for op in mm.prologue))
        self.assertEqual(4, len(loads(mm.prologue)))
        # the body loads the next iteration into each register right after
        # this iteration last reads it
        for pos, op in enumerate(mm.body):
            if isinstance(op, ir_mem):
                later = mm.body[pos + 1:]
                self.assertFalse(any(isinstance(c, ir_compute) and op.reg in c.regs.values()
                                     for c in later), f"{op.reg} read after its reload")
                # the next iteration: one step further along k
                self.assertEqual("1", str(prog.offsets[op.addr.offset].along("k")))
        # the last iteration loads nothing
        self.assertEqual([], loads(mm.epilogue))
        self.assertEqual(4, len(mm.epilogue))

    def test_no_preload(self):
        mm = self.build(preload=False).blocks[0]
        self.assertEqual(4, len(loads(mm.body)))
        self.assertEqual([], mm.epilogue)

    def test_tail(self):
        # with an unroll of 1 the loop already steps by one operation
        self.assertEqual([], self.build().blocks[0].tail)
        ctx, _ = run(k="2")
        mm = program_builder(ctx).build().blocks[0]
        self.assertEqual(4, len(loads(mm.tail)))
        self.assertEqual(4, sum(isinstance(op, ir_compute) for op in mm.tail))
        # an FMA covers one element of k: no subtail, no constraint on k
        self.assertEqual([], mm.subtail)
        self.assertIsNone(mm.requires_multiple)

    def test_subtail(self):
        # No implementation offered yet covers more than one element of k, so
        # pretend the main one covers VL of them
        import copy
        from ukrgen.components.tile import dimension_properties as dimp, dimension_type as dimt
        ctx, _ = run(k="2")
        ctx.stos[0]["mm"].extents["k"] = dimp(dt=dimt.vla, size=1, sdt=dimt.vla, sd_size=1)
        mm = program_builder(ctx).build().blocks[0]
        self.assertEqual("VL", str(mm.requires_multiple))
        self.assertIn("k must be a multiple of VL", program_builder(ctx).build().render())
        # with a subtail implementation: one element of k at a time, no constraint
        sub = copy.copy(ctx.stos[0]["mm"])
        sub.ops = sub.regenerate(counts={"k": 1})
        ctx.subtail_stos = [{"mm": sub}]
        ctx.subtail_parts = [{"mm": ctx.to_parts[0]["mm"]}]
        mm = program_builder(ctx).build().blocks[0]
        self.assertIsNone(mm.requires_multiple)
        self.assertEqual("1", str(mm.subtail_step))
        self.assertEqual(4, sum(isinstance(op, ir_compute) for op in mm.subtail))
        self.assertEqual(4, len(loads(mm.subtail)))

    def test_c_phases(self):
        prog = self.build()
        epi = prog.blocks[1].body
        self.assertEqual({0}, {op.addr.reg for op in loads(epi, "C")})
        self.assertEqual({1}, {op.addr.reg for op in epi
                               if isinstance(op, ir_mem) and "store" == op.kind})
        # both start at C's base: the stores need no rewinding
        self.assertEqual(prog.addr_setup[("C", 0)], prog.addr_setup[("C", 1)])

    def test_scalars_loaded_once(self):
        epi = self.build().blocks[1].body
        self.assertEqual(1, len(loads(epi, "beta")))
        self.assertEqual(1, len(loads(epi, "alpha")))

    def test_strides(self):
        prog = self.build()
        self.assertEqual("2*VL", str(prog.strides["A"]["k"]))
        self.assertEqual("stride(C,n)", str(prog.strides["C"]["n"]))

    def test_fewer_data_registers(self):
        # one register for A: reloaded whenever another tile is needed
        mm = self.build(preload=False, data_regs={"A": 1}).blocks[0]
        self.assertEqual(2, len(loads(mm.body, "A")))
        self.assertEqual({0}, {op.reg.index for op in loads(mm.body, "A")})
        with self.assertRaises(model_error):
            self.build(data_regs={"AB": 2})

    def test_unroll(self):
        # --k unrolls: an iteration covers --k operations' extents along k, and
        # streamed operands advance by as much
        ctx, _ = run(k="3")
        prog = program_builder(ctx).build()
        mm = prog.blocks[0]
        self.assertEqual(3, mm.unroll)
        self.assertEqual("3", str(mm.step))
        self.assertEqual("1", str(mm.tail_step))
        self.assertEqual("3", str(prog.offsets[mm.advance["A"]].along("k")))
        # preloads reach one whole iteration ahead
        ahead = [op for op in mm.body if isinstance(op, ir_mem)]
        self.assertEqual({"3", "4", "5"},
                         {str(prog.offsets[op.addr.offset].along("k")) for op in ahead})

    def test_rotating_registers(self):
        prog = self.build(addressing={"A": addressing_plan(2, addr_pattern.parse("rotate"))})
        self.assertEqual([0, 1], [op.addr.reg for op in loads(prog.blocks[0].prologue, "A")])


class test_builder_resolutions(unittest.TestCase):

    def test_chain_temporaries(self):
        ctx, res = run(**{"mm-to": [
            "fmul(A.VEC:direct, B.VEC:bc_load, T0.VEC){i=m, n=1, k*=1} ; "
            "fadd(AB.VEC, T0.VEC, AB.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed)
        mm = program_builder(ctx, preload=False).build().blocks[0]
        ops = [op for op in mm.body if isinstance(op, ir_compute)]
        self.assertEqual(["fmul", "fadd"] * 4, [op.opname for op in ops])
        self.assertIn("T0", {r.owner for op in ops for r in op.regs.values()})

    def test_scalar_broadcast_via_register(self):
        # bc_scalar: load B's element into a scalar register, then broadcast it
        ctx, res = run(**{"mm-to": ["fma(A.VEC:direct, B.VEC:bc_scalar, AB.VEC){i=m, n=1, k*=1}"]})
        mm = program_builder(ctx, preload=False).build().blocks[0]
        moves = [op for op in mm.body if isinstance(op, ir_move)]
        self.assertEqual(2, len(moves))
        self.assertEqual({"S"}, {op.src.owner for op in moves})

    def test_lanes_resolution(self):
        # NEON, row-major A: vectors along m loaded lane by lane
        ctx, res = run(isa="neon", **{"A-layout": ["m:s", "k:c"],
                                      "mm-to": ["fma(A.VEC:lanes, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed, res.output)
        mm = program_builder(ctx, preload=False).build().blocks[0]
        a = loads(mm.body, "A")
        self.assertEqual([0, 1, 0, 1], [op.lane for op in a])
        self.assertEqual({"lanes"}, {op.resolution for op in a})

    def test_lane_fma(self):
        ctx, res = run(isa="neon", n="4", m="1", **{
            "mm-to": ["fma[bdreg:ILANE](A.VEC:direct, B.VEC:use_lane, AB.VEC){i=m, n=1, k*=1}"]})
        mm = program_builder(ctx, preload=False).build().blocks[0]
        self.assertEqual(2, len(loads(mm.body, "B")))
        computes = [op for op in mm.body if isinstance(op, ir_compute)]
        self.assertEqual([0, 1, 0, 1], [op.lanes["bdreg"] for op in computes])


class test_model_stage(unittest.TestCase):

    def test_print_ir(self):
        ctx, res = run(stages=TO_STAGES + [model_stage], **{"print-ir": True})
        self.assertFalse(res.completed)
        self.assertIn("block mm, loop over k by 1 per iteration (unrolled 1x)\n", res.output)
        self.assertIn("a1 of C starts at C[]", res.output)

    def test_programs(self):
        ctx, res = run(stages=TO_STAGES + [model_stage],
                       **{"A-addr-regs": "2", "A-addr-pattern": "blocked:2"})
        self.assertTrue(res.completed)
        self.assertEqual(1, len(ctx.programs))
        self.assertEqual({0}, {op.addr.reg for op in loads(ctx.programs[0].blocks[0].prologue, "A")})

    def test_subtail_not_needed(self):
        # the main FMA already covers one element of k
        with self.assertRaisesRegex(stage_error, "--mm-subtail-to: not needed"):
            run(**{"mm-subtail-to": [FMA_M]})

    def test_invalid_pattern(self):
        with self.assertRaisesRegex(stage_error, "--A-addr-pattern"):
            run(stages=TO_STAGES + [model_stage], **{"A-addr-pattern": "spiral"})


if __name__ == "__main__":
    unittest.main()


class test_register_pressure(unittest.TestCase):

    GENERAL = {"A-layout": ["m:c", "k:s"], "B-layout": ["k:s", "n:c"], "C-layout": ["m:s", "n:s"],
               "mm-to": ["fma(A.VEC:bc_load, B.VEC:direct, AB.VEC){m=1, i=n, k*=1}"],
               "betascale-to": ["fmul(C.VEC:gather, beta.VEC:bc_load, C.VEC){m=1, i=n}"],
               "alphascale-to": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){m=1, i=n}"],
               "store-to": ["C.VEC:scatter"], "n": "2", "k": "2"}

    def test_fewer_registers_load_in_place(self):
        # A in 8 registers: each holds two tiles per iteration, so A cannot be
        # loaded an iteration ahead - its loads stay in the body. B still is.
        ctx, _ = run(m="4", **self.GENERAL)
        prog = program_builder(ctx, data_regs={"A": 4}).build()
        mm = prog.blocks[0]
        self.assertEqual([], loads(mm.prologue, "A"))
        self.assertEqual(4, len(loads(mm.prologue, "B")))
        self.assertEqual(8, len(loads(mm.body, "A")))
        self.assertEqual(8, len(loads(mm.epilogue, "A")))
        # no register loaded twice before its first use
        seen = set()
        for op in mm.body:
            if isinstance(op, ir_mem) and "A" == op.addr.component:
                seen.add(op.reg)
            if isinstance(op, ir_compute):
                for hw in op.reads:
                    r = op.regs[hw]
                    if "A" == r.owner:
                        self.assertIn(r, seen)
