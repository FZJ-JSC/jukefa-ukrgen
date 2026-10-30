"""
A copy, Y = X: asmgen's plain vector copy, never its other moves (permutes,
lane moves, broadcasts, rotations, shifts); on SME a tile's identity, rows or
columns loaded straight into the tile's slices
"""

import unittest

from asmgen.registers import asm_data_type as adt

from ukrgen.flow.isa_map import make_generator
from ukrgen.matching.math import (
    expression_node as node,
    operand_ref as ref,
    operation as op,
)
from ukrgen.support.data_move import resolution_registry, dm_location as dml
from ukrgen.support.dm_resolutions.direct import direct_provider
from ukrgen.support.dm_resolutions.scalar_reduce import scalar_reduce_provider
from ukrgen.support.encoding import encode_all
from ukrgen.support.op import op_support_builder

COPY = node(op.MOVE, ref(name="Y", indices=("m", "n")), ref(name="X", indices=("m", "n")))
VEC_COPIES = {"move(X.VEC:direct, Y.VEC){i=m, n=1}", "move(X.VEC:direct, Y.VEC){m=1, i=n}"}
TILE_COPIES = {"move(X.TILE:slices_row, Y.TILE){i=m, j=n}", "move(X.TILE:slices_col, Y.TILE){i=m, j=n}"}


def copies(isa):
    """
    The copy's candidates, X loaded from memory, Y left in registers
    """
    registry = resolution_registry()
    scalar_reduce_provider().register_resolutions(registry)
    direct_provider().register_resolutions(registry)
    osb = op_support_builder(gen=make_generator(isa))
    osb.determine_base_support()
    impls = osb.find_hw_implementations(
        req=COPY, registry=registry, io_dts={"X": adt.FP64, "Y": adt.FP64},
        io_locs={"Y": (dml.MEMORY, dml.REGISTER)})
    return set(encode_all(impls, COPY))


class test_copy_candidates(unittest.TestCase):

    def test_vector_copies(self):
        for isa in ("neon", "sve", "rvv", "avx256", "avx512"):
            with self.subTest(isa=isa):
                # one form of the move only: no discriminant, no tiles
                self.assertEqual(VEC_COPIES, copies(isa))

    def test_za_copies(self):
        found = copies("sme")
        self.assertTrue(VEC_COPIES <= found, found)
        self.assertTrue(TILE_COPIES <= found, found)
        self.assertFalse([e for e in found if "[" in e], found)


if __name__ == "__main__":
    unittest.main()
