"""
Tests for the solve stage: candidate listing and --<sto>-to selection
"""

import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.solve import (
    solve_stage, produced_rtype, consumed_rtype, check_part_chain, to_io)
from ukrgen.flow.stages.ukr import gemm_composition
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


CASE_TOS = {
    # gemm's epilogue cases, all with vectors along m like the main loop
    "alphamul-tileop": ["fmul(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
    "add-tileop": ["fadd(AB.VEC, C.VEC:direct, C.VEC){i=m, n=1}"],
    "alphaadd-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC:direct){i=m, n=1}"],
    "betaadd-tileop": ["fma(C.VEC:direct, beta.VEC:bc_load, AB.VEC){i=m, n=1}"],
    "store_ab-tileop": ["AB.VEC:direct"],
}


def gemm(isa, dt="FP64", **extra):
    return dict({"isa": isa, "ukr": "gemm", "A-data-type": dt, "B-data-type": dt,
                 "AB-data-type": dt, "C-data-type": dt, **CASE_TOS}, **extra)


class test_solve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # one listing, reused: solving is the slow part
        cls.ctx, cls.listing = run(gemm("sve", **{"list-tileop-candidates": True}))

    def test_listing_exits_early(self):
        self.assertFalse(self.listing.completed)
        self.assertEqual("solve_stage", self.listing.stage)
        for sto in ("mm", "betascale", "alphascale", "store"):
            self.assertIn(f"--{sto}-tileop", self.listing.output)
        self.assertIn('--store-tileop "C.VEC:direct"', self.listing.output)
        self.assertIn("inside the loop over k", self.listing.output)

    def test_scalars_are_broadcast(self):
        # beta is a scalar requirement operand: it only ever arrives broadcast
        lines = [l for l in self.listing.output.splitlines() if "--betascale-tileop" in l]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"beta\.VEC:bc_")

    def candidates(self, sto):
        return [l for l in self.listing.output.splitlines() if f"--{sto}-tileop" in l]

    def test_accumulator_resident(self):
        # AB is zeroed and accumulated in registers: never loaded or stored
        for line in self.candidates("mm"):
            self.assertNotIn("AB.VEC:", line)
            self.assertIn("AB.VEC", line)

    def test_temporaries_resident(self):
        # T0 between fmul and fadd only exists in registers
        chains = [l for sto in ("mm", "alphascale") for l in self.candidates(sto) if "T0" in l]
        self.assertTrue(chains)
        for line in chains:
            self.assertNotIn("T0.VEC:", line)

    def test_loaded_then_resident(self):
        # betascale loads C from memory and leaves the result in registers for
        # alphascale, which reads both C and AB where they were left
        for line in self.candidates("betascale"):
            self.assertRegex(line, r"C\.VEC:\w")
        for line in self.candidates("alphascale"):
            self.assertNotIn("AB.VEC:", line)
            self.assertNotRegex(line, r"C\.VEC:")

    def test_select_by_index_and_string(self):
        ctx, res = run(gemm("sve", **{
            "mm-tileop": ["0"],
            "betascale-tileop": ["mul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"],
            "alphascale-tileop": ["0"],
            "store-tileop": ["0"]}))
        self.assertTrue(res.completed)
        self.assertEqual(1, len(ctx.to_parts))
        part = ctx.to_parts[0]
        self.assertEqual("mul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}",
                         part["betascale"].encoding)
        self.assertEqual("C.VEC:direct", part["store"].encoding)

    def test_parts(self):
        # two mm implementations make two parts; a single value serves both
        ctx, res = run(gemm("sve", **{"mm-tileop": ["0", "1"], "betascale-tileop": ["0"],
                                      "alphascale-tileop": ["0"], "store-tileop": ["0", "0"]}))
        self.assertTrue(res.completed)
        self.assertEqual(2, len(ctx.to_parts))
        self.assertNotEqual(ctx.to_parts[0]["mm"].encoding, ctx.to_parts[1]["mm"].encoding)
        self.assertEqual(ctx.to_parts[0]["alphascale"].encoding,
                         ctx.to_parts[1]["alphascale"].encoding)

    def test_part_count_mismatch(self):
        with self.assertRaisesRegex(stage_error, "--mm-tileop has 2 values for 3 parts"):
            run(gemm("sve", **{"mm-tileop": ["0", "1"], "betascale-tileop": ["0"],
                               "alphascale-tileop": ["0", "1", "2"], "store-tileop": ["0"]}))

    def test_missing_selection_lists_candidates(self):
        with self.assertRaisesRegex(stage_error, r"--mm-tileop is required(.|\n)*\[0\]"):
            run(gemm("sve"))

    def test_typo_suggests_candidates(self):
        with self.assertRaisesRegex(stage_error, "Closest candidates"):
            run(gemm("sve", **{"mm-tileop": [
                "fma(A.VEC:direct, B.VEC:bc_lod, AB.VEC:direct>direct){i=m, n=1, k*=1}"]}))

    def test_produced_rtype(self):
        ctx, _ = run(gemm("sve", **{"mm-tileop": ["0"], "betascale-tileop": ["0"],
                                    "alphascale-tileop": ["0"], "store-tileop": ["0"]}))
        impl = next(iter(ctx.to_candidates["alphascale"].values()))
        self.assertEqual(rgt.VEC, produced_rtype(impl, "C"))
        self.assertIsNone(produced_rtype(impl, "alpha"))
        self.assertEqual(rgt.VEC, consumed_rtype(impl, "AB"))
        self.assertEqual(rgt.VEC, consumed_rtype(impl, "C"))

    def test_unsupported_data_types(self):
        # UINT64 can be loaded on NEON, but no arithmetic operation takes it
        with self.assertRaisesRegex(stage_error, "no implementation"):
            run(gemm("neon", dt="UINT64", **{"mm-tileop": ["0"]}))


class test_part_chain(unittest.TestCase):
    """
    Register type agreement within one part, with register types set by hand:
    the solver offers no outer product on SME yet, so no candidate leaves AB in
    ZA to test against.
    """

    T, V = rgt.TILE, rgt.VEC

    def ios(self, mm_ab, alpha_ab, store_c, alpha_c=None):
        alpha_c = alpha_c or self.V
        return {
            "mm": to_io(reads={}, writes={"AB": mm_ab}),
            "betascale": to_io(reads={"C": self.V}, writes={"C": self.V}),
            "alphascale": to_io(reads={"AB": alpha_ab, "C": self.V}, writes={"C": alpha_c}),
            "store": to_io(reads={"C": store_c}, writes={}),
        }

    def test_consistent(self):
        self.assertEqual([], check_part_chain(gemm_composition, self.ios(self.V, self.V, self.V)))
        # an outer-product part whose epilogue takes AB from ZA
        self.assertEqual([], check_part_chain(gemm_composition, self.ios(self.T, self.T, self.V)))

    def test_scale_reads_wrong_register_type(self):
        problems = check_part_chain(gemm_composition, self.ios(self.T, self.V, self.V))
        self.assertEqual(["case otherwise: alphascale reads AB from VEC, but mm leaves it "
                          "in TILE"], problems)

    def test_store_follows_last_writer(self):
        # alphascale leaves C in ZA: the store must take it from there
        problems = check_part_chain(gemm_composition,
                                    self.ios(self.T, self.T, self.V, alpha_c=self.T))
        self.assertEqual(["case otherwise: store reads C from VEC, but alphascale leaves it "
                          "in TILE"], problems)

    def test_loaded_operands_unchecked(self):
        # betascale loads C from memory: nothing earlier left it anywhere
        ios = self.ios(self.V, self.V, self.V)
        ios["betascale"] = to_io(reads={"C": self.T}, writes={"C": self.V})
        self.assertEqual([], check_part_chain(gemm_composition, ios))


class test_solve_pack(unittest.TestCase):

    def test_pack_candidates(self):
        ctx, res = run({"isa": "sve", "ukr": "pack", "X-data-type": "FP64",
                        "Y-data-type": "FP64", "list-tileop-candidates": True})
        out = res.output
        self.assertIn("inside the loop over n", out)
        pack = [l for l in out.splitlines() if "--pack-tileop" in l]
        self.assertTrue(pack)
        # Y is only written, and stays in registers for the store STO
        for line in pack:
            self.assertNotIn("Y.VEC:", line)
        self.assertIn('--store-tileop "Y.VEC:direct"', out)


if __name__ == "__main__":
    unittest.main()
