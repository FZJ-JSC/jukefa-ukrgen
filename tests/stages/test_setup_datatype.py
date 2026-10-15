"""
Tests for the setup and datatype stages
"""

import unittest

from asmgen.registers import asm_data_type as adt

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage, dt_names
from ukrgen.flow.stages.isaparam import isaparam_stage
from ukrgen.flow.stages.ukr import gemm_composition


def _setup(isa, ukr="gemm"):
    ctx = ukr_context()
    s = setup_stage(ctx)
    s.set_param("isa", isa)
    s.set_param("ukr", ukr)
    return ctx, s.progress()


class test_setup(unittest.TestCase):

    def test_allocates_generator_and_composition(self):
        ctx, spawned = _setup("sve")
        self.assertIs(gemm_composition, ctx.composition)
        self.assertTrue(hasattr(ctx.gen, "fma"))
        self.assertEqual([], spawned)

    def test_isa_parameters_spawn_stage(self):
        _, spawned = _setup("rvv")
        self.assertEqual([isaparam_stage], spawned)


class test_datatype(unittest.TestCase):

    def test_aliases_accepted(self):
        names = dt_names({adt.DOUBLE, adt.SINGLE})
        self.assertIn("FP64", names)
        self.assertIn("DOUBLE", names)
        self.assertIn("FP32", names)

    def test_parameters_and_references(self):
        ctx, _ = _setup("sve")
        s = datatype_stage(ctx)
        # alpha and beta take C's type and get no parameter
        self.assertEqual({"A-data-type", "B-data-type", "AB-data-type", "C-data-type"},
                         set(s.get_parameter_names()))
        self.assertIn("FP64", s.get_param("A-data-type").choices)

        for comp in ("A", "B", "AB"):
            s.set_param(f"{comp}-data-type", "FP64")
        s.set_param("C-data-type", "SINGLE")
        s.progress()

        self.assertEqual(adt.FP64, ctx.component_dts["A"])
        self.assertEqual(adt.FP32, ctx.component_dts["C"])
        self.assertEqual(adt.FP32, ctx.component_dts["alpha"])
        self.assertEqual(adt.FP32, ctx.component_dts["beta"])

    def test_every_isa_offers_its_data_types(self):
        from ukrgen.flow.isa_map import asmgen_map
        for isa in asmgen_map:
            with self.subTest(isa=isa):
                ctx, _ = _setup(isa)
                choices = datatype_stage(ctx).get_param("A-data-type").choices
                self.assertIn("SINGLE", choices)
                self.assertIn("FP32", choices)

if __name__ == "__main__":
    unittest.main()
