"""
A lane selection (ILANE, GLANE, BLOCKLANE) reads an element of its register:
an operand the matching left whole takes none. gemm's indexed fma lanes its
scalar operand, never the vector (B loaded whole, then one of its lanes used
for every n)
"""

import unittest

from asmgen.registers import asm_data_type as adt

from ukrgen.flow.isa_map import make_generator
from ukrgen.flow.stages.solve import default_registry
from ukrgen.flow.stages.ukr import gemm_composition
from ukrgen.matching.math import transformation as tf
from ukrgen.support.dm_solver import LANE_MODS
from ukrgen.support.op import op_support_builder


class test_lanes(unittest.TestCase):

    def test_whole_operands_take_no_lane(self):
        mm = gemm_composition.get_sto_descriptions()[0].req
        for isa in ("neon", "sve"):
            with self.subTest(isa=isa):
                osb = op_support_builder(gen=make_generator(isa))
                osb.determine_base_support()
                impls = osb.find_hw_implementations(
                    req=mm, registry=default_registry(),
                    io_dts={name: adt.FP64 for name in ("A", "B", "AB")})
                laned = 0
                for impl in impls:
                    for step, res in zip(impl.math_chain, impl.resolved_chain):
                        for sig in res.compute_sg.sigs:
                            for hw, tfs in step.transformations.items():
                                if sig.operands[hw].modifiers & LANE_MODS:
                                    laned += 1
                                    self.assertTrue(set(tfs) - {tf.NONE},
                                                    f"{hw} whole, but laned")
                # the lane forms are still there, for the scalars
                self.assertTrue(laned)


if __name__ == "__main__":
    unittest.main()
