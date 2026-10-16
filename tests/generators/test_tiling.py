"""
Tests for the projection-based tiling generator
"""

import unittest

from ukrgen.generators.tiling import generate_tiling
from ukrgen.flow.stages.ukr import gemm_composition, pack_composition


class test_tiling(unittest.TestCase):

    def test_mm_projection(self):
        mm = gemm_composition.get_sto("mm")
        ops = generate_tiling(order=("k", "m", "n"), counts={"m": 2, "n": 3, "k": 1},
                              operands=mm.operand_indices)
        self.assertEqual(6, len(ops))
        op = ops[4]                          # k=0, m=1, n=1
        self.assertEqual((1, 1), op.coord("AB"))
        self.assertEqual((1, 0), op.coord("A"))   # A[m,k]
        self.assertEqual((0, 1), op.coord("B"))   # B[k,n]

    def test_scalar_projects_to_nothing(self):
        beta = gemm_composition.get_sto("betascale")
        ops = generate_tiling(order=("m", "n"), counts={"m": 2, "n": 2},
                              operands=beta.operand_indices)
        self.assertEqual({()}, {op.coord("beta") for op in ops})
        self.assertEqual(4, len({op.coord("C") for op in ops}))

    def test_offset_by_index_name(self):
        # the same operations one loop iteration later: only k moves
        mm = gemm_composition.get_sto("mm")
        base = generate_tiling(order=("k", "m"), counts={"m": 2, "k": 1, "n": 1},
                               operands={"A": ("m", "k")})
        later = generate_tiling(order=("k", "m"), counts={"m": 2, "k": 1, "n": 1},
                                operands={"A": ("m", "k")}, offset={"k": 1})
        self.assertEqual([(0, 0), (1, 0)], [op.coord("A") for op in base])
        self.assertEqual([(0, 1), (1, 1)], [op.coord("A") for op in later])

    def test_pack_needs_no_square_tile(self):
        # packing used to require n == k; now any m x n panel tiles
        pack = pack_composition.get_sto("pack")
        ops = generate_tiling(order=("n", "m"), counts={"m": 3, "n": 5},
                              operands=pack.operand_indices)
        self.assertEqual(15, len(ops))
        self.assertEqual({()}, {op.coord("kappa") for op in ops})

    def test_stray_index(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            generate_tiling(order=("m",), counts={"m": 1}, operands={"A": ("m", "k")})


if __name__ == "__main__":
    unittest.main()
