"""
Strided loads and stores: layouts, the strided resolutions and lane repeats
"""

import re
import unittest

from asmgen.asmblocks.op import register_type as rgt, operand_modifier as omod
from asmgen.registers import asm_data_type as adt

from ukrgen.flow.isa_map import make_generator
from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.layout import layout_stage
from ukrgen.flow.stages.solve import solve_stage, check_part_chain, to_io
from ukrgen.flow.stages.stage import stage_error
from ukrgen.flow.stages.ukr import gemm_composition
from ukrgen.support.data_move import dm_location as dml, dm_step, dm_repeat, orig_ref
from ukrgen.support.dm_solver import repeat_fits

STAGES = [setup_stage, datatype_stage, layout_stage, solve_stage]


def layout(indices, contiguous):
    return [f"{i}:{'c' if i == contiguous else 's'}" for i in indices]


def listing(isa, a="k", c="n", b="n"):
    params = {"isa": isa, "A-data-type": "FP64", "B-data-type": "FP64",
              "AB-data-type": "FP64", "C-data-type": "FP64",
              "A-layout": layout("mk", a), "B-layout": layout("kn", b),
              "C-layout": layout("mn", c), "list-to-candidates": True}
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    return stage_engine(STAGES, ctx, prolog=prolog).run().output


def tags(out, comp, sto, along="m"):
    """
    Resolutions of comp among the candidates of sto. Compute candidates are
    restricted to vectors along one index; store candidates cover whatever the
    implementations before them leave.
    """
    lines = [l for l in out.splitlines() if f"--{sto}-to" in l]
    if "store" != sto:
        # every operation of the candidate with vectors along that index
        other = {"m": "n", "n": "m"}[along]
        lines = [l for l in lines if f"i={along}" in l and f"i={other}" not in l]
    return set(re.findall(rf"{comp}\.VEC:(\w+)", "\n".join(lines)))


class test_strided(unittest.TestCase):

    def test_row_major_a_is_strided(self):
        # vectors run along m; row-major A is contiguous along k
        expected = {"sve": {"gather"}, "rvv": {"gather", "strided"},
                    "neon": {"lanes"}, "avx512": {"gather"}}
        for isa, resolutions in expected.items():
            with self.subTest(isa=isa):
                self.assertEqual(resolutions, tags(listing(isa), "A", "mm"))

    def test_contiguous_stays_direct(self):
        out = listing("sve", a="m", c="m")
        self.assertEqual({"direct"}, tags(out, "A", "mm"))
        # stores from implementations with vectors along m are contiguous; those
        # with vectors along n leave C to be scattered
        self.assertEqual({"direct", "scatter"}, tags(out, "C", "store"))

    def test_row_major_c_stores_strided(self):
        # vectors along m into a row-major C scatter; vectors along n store directly
        self.assertEqual({"direct", "scatter"}, tags(listing("sve"), "C", "store"))
        self.assertEqual({"direct", "scatter", "strided"}, tags(listing("rvv"), "C", "store"))

    def test_orientation_decides(self):
        # the same row-major A: strided for vectors along m, broadcast elements
        # for vectors along n - which needs no contiguous index at all
        out = listing("sve")
        self.assertEqual({"gather"}, tags(out, "A", "mm", along="m"))
        self.assertNotIn("gather", tags(out, "A", "mm", along="n"))
        self.assertIn("bc_load", tags(out, "A", "mm", along="n"))

    def test_lane_count_must_fit(self):
        step = dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC,
                       opd_mod_reqs={orig_ref(): {omod.ILANE}},
                       repeat=dm_repeat(lane_operand="adreg_lane"))
        def fits(isa, dt):
            gen = make_generator(isa)
            return any(repeat_fits(gen, s, step, dt) for s in gen.load.get_signatures()
                       if omod.ILANE in s.operands["adreg"].modifiers
                       and s.operands["adreg"].dt == dt)
        self.assertTrue(fits("neon", adt.FP64))      # 2 lanes, immediate 0..1
        self.assertFalse(fits("avx512", adt.FP64))   # 8 lanes, immediate 0..1
        self.assertFalse(fits("sve", adt.FP64))      # lane count known at run time only

    def test_general_strides(self):
        # contiguous along neither index: nothing can be loaded directly
        out = listing("sve", a=None, c=None)
        self.assertEqual({"gather"}, tags(out, "A", "mm"))
        self.assertEqual({"scatter"}, tags(out, "C", "store"))

    def test_scalar_reduced_any_layout(self):
        # B is broadcast one element at a time: that works for any layout. Only
        # taking lanes from a whole loaded vector needs a contiguous index.
        whole_vector = {"use_lane", "bc_lane"}
        contiguous = tags(listing("neon", b="n"), "B", "mm")
        strided = tags(listing("neon", b=None), "B", "mm")
        self.assertTrue(whole_vector & contiguous)
        self.assertFalse(whole_vector & strided)
        self.assertIn("bc_load", strided)
        self.assertEqual(contiguous - whole_vector, strided)

    def test_store_access_must_match(self):
        V = rgt.VEC
        ios = {
            "mm": to_io(reads={}, writes={"AB": V}),
            "betascale": to_io(reads={"C": V}, writes={"C": V}),
            "alphascale": to_io(reads={"AB": V, "C": V}, writes={"C": V},
                                stores={"C": dml.STRIDED_MEMORY}),
            "store": to_io(reads={"C": V}, writes={}, stores={"C": dml.MEMORY}),
        }
        self.assertEqual(["store stores C contiguous, but as alphascale leaves it "
                          "the store has to be strided"],
                         check_part_chain(gemm_composition, ios))


class test_layout_stage(unittest.TestCase):

    def stage(self):
        ctx = ukr_context()
        s = setup_stage(ctx)
        s.set_param("isa", "sve")
        s.set_param("ukr", "gemm")
        s.progress()
        return ctx, layout_stage(ctx)

    def test_parameters(self):
        ctx, layout = self.stage()
        # register-only AB and the scalars have no layout
        self.assertEqual({"A-layout", "B-layout", "C-layout"},
                         set(layout.get_parameter_names()))
        layout.set_param("A-layout", ["m:c", "k:s"])
        layout.set_param("B-layout", ["n:c", "k:s"])
        layout.set_param("C-layout", ["m:s", "n:s"])
        layout.progress()
        self.assertEqual({"A": "m", "B": "n", "C": None}, ctx.component_layouts)
        self.assertEqual({"m": "s", "n": "s"}, ctx.component_strides["C"])

    def test_invalid(self):
        _, layout = self.stage()
        for tokens, message in ((["m:c"], "missing k"),
                                (["m:c", "k:c"], "both m and k"),
                                (["m:c", "m:s", "k:s"], "m twice"),
                                (["m:x", "k:s"], "not <index>:c"),
                                (["m:c", "n:s"], "not <index>:c")):
            with self.subTest(tokens=tokens):
                with self.assertRaisesRegex(stage_error, message):
                    layout.parse("A", tokens)


if __name__ == "__main__":
    unittest.main()
