"""
List scheduling under distances and register budgets
"""

import re
import shutil
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
from ukrgen.flow.stages.irmods import pre_specialize_irmod_stage, post_specialize_irmod_stage
from ukrgen.flow.stages.scheduling import schedule_stage
from ukrgen.flow.stages.emit import emit_stage
from ukrgen.models.load_store_operations import lsc_load, lsc_transformation
from ukrgen.schedulers.dependency import dependency_type as dept
from ukrgen.schedulers.distance import distance_specification
from ukrgen.schedulers.list_scheduler import list_scheduler, dependencies

from tests.specializers.test_signature import assembles

STAGES = [setup_stage, datatype_stage, layout_stage, solve_stage, dimension_stage, sto_stage,
          model_stage, pre_specialize_irmod_stage, isa_specialize_stage,
          post_specialize_irmod_stage, schedule_stage, emit_stage]

GEMM_NEON = {
    "isa": "neon", "ukr": "gemm", "A-data-type": "FP64", "B-data-type": "FP64",
    "AB-data-type": "FP64", "C-data-type": "FP64",
    "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"], "C-layout": ["m:c", "n:s"],
    "mm-tileop": ["fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"],
    "betascale-tileop": ["mul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"],
    "alphascale-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
    "store-tileop": ["C.VEC:direct"],
    "alphamul-tileop": ["mul(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
    "add-tileop": ["add(AB.VEC, C.VEC:direct, C.VEC){i=m, n=1}"],
    "alphaadd-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC:direct){i=m, n=1}"],
    "betaadd-tileop": ["fma(C.VEC:direct, beta.VEC:bc_load, AB.VEC){i=m, n=1}"],
    "store_ab-tileop": ["AB.VEC:direct"],
    "m": "4", "n": "2", "k": "1", "A-data-regs": "4", "B-data-regs": "2", "C-data-regs": "8"}


def run(**extra):
    params = dict(GEMM_NEON, **extra)
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    return ctx, stage_engine(STAGES, ctx, prolog=prolog).run()


def specs(*texts):
    return [distance_specification.from_string(t) for t in texts]


class test_dependencies(unittest.TestCase):

    def test_lane_reads_depend_on_the_load(self):
        ctx, _ = run(**{"mm-tileop": ["fma[bdreg:ILANE](A.VEC:direct, B.VEC:use_lane, AB.VEC)"
                                  "{i=m, n=1, k*=1}"], "no-preload": True})
        body = ctx.programs[0].blocks[0].body
        edges = dependencies(body, loop=False)
        for j, op in enumerate(body):
            if isinstance(op, lsc_transformation) and any(len(i.indices) > 1 for i in op.indices):
                srcs = {e.src for e in edges if e.dst == j and dept.RAW == e.dep}
                self.assertTrue(any(isinstance(body[s], lsc_load) for s in srcs))


class test_distances(unittest.TestCase):

    def body(self):
        ctx, _ = run(**{"no-preload": True})
        return ctx.programs[0].blocks[0].body

    def test_reached_or_reported(self):
        body = self.body()
        order, report = list_scheduler(specs("raw:data::ld:fma:3"))(body)
        self.assertEqual(sorted(map(id, body)), sorted(map(id, order)))
        pos = {id(op): t for t, op in enumerate(order)}
        for e in dependencies(body, loop=False):
            # every dependency still in order
            self.assertLess(pos[id(body[e.src])], pos[id(body[e.dst])])
        self.assertEqual([3], report.requested)

    def test_never_fails(self):
        order, report = list_scheduler(specs("raw:data::ld:fma:50"))(self.body())
        self.assertTrue(report.warnings())
        self.assertLess(report.achieved[0], 50)

    def test_loop_carried(self):
        # the accumulator chain runs from one iteration into the next
        ctx, _ = run()
        body = ctx.programs[0].blocks[0].body
        self.assertTrue(any(e.carried for e in dependencies(body, loop=True)))
        _, report = list_scheduler(specs("raw:data::fma:fma:4"))(body, loop=True)
        self.assertNotEqual(float("inf"), report.achieved[0])


class test_register_budget(unittest.TestCase):

    def test_epilogue_within_budget(self):
        # 32 vector registers less 18 reserved: 14 for the epilogue's 8 AB, 8 C
        # and the scalars - C has to take AB's registers as they die
        ctx, res = run(mru=True, **{"mru-reserve": "18"})
        self.assertTrue(res.completed, res.output)
        default = ctx.emitted[0].cases[-1][2][0].sections["body"]
        regs = {r for line in default for r in re.findall(r"\bv(\d+)\.", line)}
        self.assertLessEqual(len(regs), 14)
        if shutil.which("aarch64-linux-gnu-as"):
            ok, err = assembles(ctx.emitted[0].instructions())
            self.assertTrue(ok, err)

    def test_print_schedule(self):
        _, res = run(distances=["raw:data::ld:fma:3"], **{"print-schedule": True})
        self.assertFalse(res.completed)
        self.assertIn("reached", res.output)


if __name__ == "__main__":
    unittest.main()
