"""
Tests for the dimension and STO stages
"""

import unittest

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.solve import solve_stage
from ukrgen.flow.stages.dimension import dimension_stage
from ukrgen.flow.stages.sto import sto_stage, fmt_dim
from ukrgen.flow.stages.stage import stage_error

STAGES = [setup_stage, datatype_stage, solve_stage, dimension_stage, sto_stage]


def run(params):
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    return ctx, stage_engine(STAGES, ctx, prolog=prolog).run()


def gemm(**extra):
    p = {"isa": "sve", "ukr": "gemm", "A-data-type": "FP64", "B-data-type": "FP64",
         "AB-data-type": "FP64", "C-data-type": "FP64",
         "mm-to": ["0"], "betascale-to": ["0"], "alphascale-to": ["0"], "store-to": ["0"],
         "m": "2", "n": "3", "k": "2"}
    p.update(extra)
    return p


class test_sto_stage(unittest.TestCase):

    def test_tilings(self):
        ctx, res = run(gemm())
        self.assertTrue(res.completed)
        self.assertEqual(1, len(ctx.stos))
        stos = ctx.stos[0]
        self.assertEqual(2 * 3 * 2, len(stos["mm"].ops))
        self.assertEqual(("k", "m", "n"), stos["mm"].order)
        self.assertEqual(2 * 3, len(stos["betascale"].ops))
        # the store tiles C as alphascale left it: vectors along m
        self.assertEqual("V", fmt_dim(stos["store"].tiles["C"].dima))
        self.assertEqual({(m, n) for m in range(2) for n in range(3)},
                         {op.coord("C") for op in stos["store"].ops})
        # beta is a scalar: one coordinate for every operation
        self.assertEqual({()}, {op.coord("beta") for op in stos["betascale"].ops})

    def test_print_stos(self):
        _, res = run(gemm(**{"print-stos": True}))
        self.assertFalse(res.completed)
        self.assertIn("mm, inside the loop over k: 12 operations", res.output)
        self.assertIn("beta()", res.output)

    def test_order(self):
        ctx, _ = run(gemm(order="mnk"))
        self.assertEqual(("m", "n", "k"), ctx.stos[0]["mm"].order)
        self.assertEqual(("m", "n"), ctx.stos[0]["betascale"].order)
        with self.assertRaisesRegex(stage_error, "--order must list"):
            run(gemm(order="mn"))

    def test_bad_size(self):
        with self.assertRaisesRegex(stage_error, "--n must be a positive integer"):
            run(gemm(n="0"))

    def test_parts_need_partition(self):
        with self.assertRaisesRegex(stage_error, "partition"):
            run(gemm(**{"mm-to": ["0", "1"]}))

    def test_pack(self):
        ctx, res = run({"isa": "sve", "ukr": "pack", "X-data-type": "FP64",
                        "Y-data-type": "FP64", "pack-to": ["0"], "store-to": ["0"],
                        "m": "3", "n": "2"})
        self.assertTrue(res.completed)
        stos = ctx.stos[0]
        self.assertEqual(("n", "m"), stos["pack"].order)   # the loop index outermost
        self.assertEqual(6, len(stos["pack"].ops))
        self.assertEqual({()}, {op.coord("kappa") for op in stos["pack"].ops})
        self.assertEqual(6, len(stos["store"].ops))


if __name__ == "__main__":
    unittest.main()
