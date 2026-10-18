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


class test_lanes(unittest.TestCase):

    def test_lane_positions(self):
        # B used one element at a time out of registers holding two along n
        ops = generate_tiling(order=("k", "n"), counts={"k": 1, "n": 4},
                              operands={"B": ("k", "n")}, lanes={"B": ("n", 2)},
                              io={"B": (True, False)}, opstr="fma")
        self.assertEqual([(0, 0), (0, 0), (0, 1), (0, 1)], [op.coord("B") for op in ops])
        self.assertEqual([(None, 0), (None, 1), (None, 0), (None, 1)],
                         [op.lane("B") for op in ops])
        self.assertIn("B(0,1.el[1])", str(ops[3]))

    def test_rendering_does_not_move_operations(self):
        from ukrgen.components.operation import operation
        from ukrgen.components.tile import tile, dimension_properties as dimp, dimension_type as dimt
        one = dimp(dt=dimt.fixed, size=1)
        vec = dimp(dt=dimt.fixed, size=2)
        # gemm-shaped, B by lane: the old rendering adds the subindex to C's offset
        op = operation(tiles=[tile(vec, one), tile(one, vec), tile(vec, one)],
                       tile_offsets=[[0, 0], [0, 0], [0, 0]], subindices=[0, 1, 0], opstr="fma")
        self.assertEqual(str(op), str(op))
        self.assertEqual([[0, 0], [0, 0], [0, 0]], op.tile_offsets)
