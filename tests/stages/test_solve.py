"""
Tests for the solve stage: candidate listing and --<sto>-to selection
"""

import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.solve import solve_stage, produced_rtype
from ukrgen.flow.stages.stage import stage_error


def run(params):
    """
    Run setup, datatype and solve with the given parameter values
    """
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    res = stage_engine([setup_stage, datatype_stage, solve_stage], ctx, prolog=prolog).run()
    return ctx, res


def gemm(isa, dt="FP64", **extra):
    return dict({"isa": isa, "ukr": "gemm", "A-data-type": dt, "B-data-type": dt,
                 "AB-data-type": dt, "C-data-type": dt}, **extra)


class test_solve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # one listing, reused: solving is the slow part
        cls.ctx, cls.listing = run(gemm("sve", **{"list-to-candidates": True}))

    def test_listing_exits_early(self):
        self.assertFalse(self.listing.completed)
        self.assertEqual("solve_stage", self.listing.stage)
        for sto in ("mm", "betascale", "alphascale", "store"):
            self.assertIn(f"--{sto}-to", self.listing.output)
        self.assertIn('--store-to "C.VEC:direct"', self.listing.output)
        self.assertIn("inside the loop over k", self.listing.output)

    def test_scalars_are_broadcast(self):
        # beta is a scalar requirement operand: it only ever arrives broadcast
        lines = [l for l in self.listing.output.splitlines() if "--betascale-to" in l]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"beta\.VEC:bc_")

    def test_select_by_index_and_string(self):
        ctx, res = run(gemm("sve", **{
            "mm-to": ["0"],
            "betascale-to": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC:>direct){i=m, n=1}"],
            "alphascale-to": ["0"],
            "store-to": ["0"]}))
        self.assertTrue(res.completed)
        self.assertEqual(["fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC:>direct){i=m, n=1}"],
                         ctx.to_choices["betascale"])
        self.assertEqual(["C.VEC:direct"], ctx.to_choices["store"])
        self.assertEqual(1, len(ctx.to_choices["mm"]))

    def test_several_to_for_fusion(self):
        ctx, res = run(gemm("sve", **{"mm-to": ["0", "1"], "betascale-to": ["0"],
                                      "alphascale-to": ["0"], "store-to": ["0"]}))
        self.assertTrue(res.completed)
        self.assertEqual(2, len(ctx.to_choices["mm"]))

    def test_missing_selection_lists_candidates(self):
        with self.assertRaisesRegex(stage_error, r"--mm-to is required(.|\n)*\[0\]"):
            run(gemm("sve"))

    def test_typo_suggests_candidates(self):
        with self.assertRaisesRegex(stage_error, "Closest candidates"):
            run(gemm("sve", **{"mm-to": [
                "fma(A.VEC:direct, B.VEC:bc_lod, AB.VEC:direct>direct){i=m, n=1, k*=1}"]}))

    def test_store_needs_one_candidate(self):
        with self.assertRaisesRegex(stage_error, "exactly one"):
            run(gemm("sve", **{"mm-to": ["0"], "betascale-to": ["0"], "alphascale-to": ["0"],
                               "store-to": ["0", "0"]}))

    def test_produced_rtype(self):
        ctx, _ = run(gemm("sve", **{"mm-to": ["0"], "betascale-to": ["0"],
                                    "alphascale-to": ["0"], "store-to": ["0"]}))
        impl = next(iter(ctx.to_candidates["alphascale"].values()))
        self.assertEqual(rgt.VEC, produced_rtype(impl, "C"))
        self.assertIsNone(produced_rtype(impl, "alpha"))

    def test_unsupported_data_types(self):
        # UINT64 can be loaded on NEON, but no arithmetic operation takes it
        with self.assertRaisesRegex(stage_error, "no implementation"):
            run(gemm("neon", dt="UINT64", **{"mm-to": ["0"]}))


class test_solve_pack(unittest.TestCase):

    def test_pack_candidates(self):
        ctx, res = run({"isa": "sve", "ukr": "pack", "X-data-type": "FP64",
                        "Y-data-type": "FP64", "list-to-candidates": True})
        out = res.output
        self.assertIn("inside the loop over n", out)
        pack = [l for l in out.splitlines() if "--pack-to" in l]
        self.assertTrue(pack)
        # Y is only written: no load of the destination
        for line in pack:
            self.assertIn("Y.VEC:>", line)
        self.assertIn('--store-to "Y.VEC:direct"', out)


if __name__ == "__main__":
    unittest.main()
