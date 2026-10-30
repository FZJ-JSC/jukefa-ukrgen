"""
The plain move shapes - a vector's copy, a tile's: a move solves a
requirement that is one, and is no step of a chain
"""

import unittest

from ukrgen.flow.stages.ukr import gemm_composition
from ukrgen.matching.math import (
    expression_node as node,
    operand_ref as ref,
    operation as op,
    solve_requirement,
    HW_FADD_AST,
    HW_FMUL_AST,
    HW_FMA_AST,
    HW_FDOTA_AST,
    HW_FOPA_AST,
    HW_MMA_AST,
    HW_MOVE_AST,
    HW_MOVE_TILE_AST,
)

ARITH = [HW_FADD_AST, HW_FMUL_AST, HW_FMA_AST, HW_FDOTA_AST, HW_FOPA_AST, HW_MMA_AST]
MOVES = [HW_MOVE_AST, HW_MOVE_TILE_AST]


class test_move_matching(unittest.TestCase):

    def test_copy(self):
        # Y = X: a move of vectors along either index, or of a tile
        req = node(op.MOVE, ref(name="Y", indices=("m", "n")), ref(name="X", indices=("m", "n")))
        chains = solve_requirement(req, ARITH + MOVES)
        self.assertTrue(chains)
        for chain in chains:
            self.assertEqual(1, len(chain))
            self.assertIn(chain[0].hw_ast, MOVES)
            self.assertEqual({"bdreg": "Y", "adreg": "X"}, chain[0].name_mapping)
        maps = [chain[0].index_mapping for chain in chains]
        for index_map in ({"i": "m"}, {"i": "n"}, {"i": "m", "j": "n"}):
            self.assertIn(index_map, maps)

    def test_no_move_in_chains(self):
        # inside a chain a move would only copy a temporary: gemm's
        # requirements solve as they did without the move shapes
        for sto in gemm_composition.get_sto_descriptions():
            if sto.req is None:
                continue
            with self.subTest(sto=sto.name):
                chains = solve_requirement(sto.req, ARITH + MOVES)
                self.assertEqual(len(solve_requirement(sto.req, ARITH)), len(chains))
                self.assertFalse([chain for chain in chains
                                  for step in chain if step.hw_ast in MOVES])


if __name__ == "__main__":
    unittest.main()
