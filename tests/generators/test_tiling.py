"""
Tests for the projection-based tiling generator
"""

import unittest

from ukrgen.generators.tiling import generate_tiling, split_levels
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

    # two-level orders (the old mm generator's MmNnKk): an uppercase index its
    # registers, the lowercase the lanes within one

    def test_split_levels(self):
        self.assertEqual([("k", None), ("n", "reg"), ("m", None), ("n", "lane")],
                         split_levels(("k", "N", "m", "n")))
        self.assertEqual([("k", None), ("m", None), ("n", None)], split_levels(("k", "m", "n")))

    def _mn(self, ops):
        return [op.coord("AB") for op in ops]

    def test_two_levels_map_back(self):
        # B's register holds two columns: kNmn multiplies per B register, per A
        # vector, per lane - n = 2 N + lane; the same points as kmn's
        mm = gemm_composition.get_sto("mm")
        ops = generate_tiling(order=("k", "N", "m", "n"), counts={"m": 3, "n": 8, "k": 1},
                              operands=mm.operand_indices, factors={"n": 2})
        mn = self._mn(ops)
        self.assertEqual([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (0, 2), (0, 3)], mn[:8])
        plain = generate_tiling(order=("k", "m", "n"), counts={"m": 3, "n": 8, "k": 1},
                                operands=mm.operand_indices)
        self.assertEqual(sorted(self._mn(plain)), sorted(mn))
        self.assertEqual(24, len(mn))

    def test_two_levels_from_lanes(self):
        # an operand used a lane at a time (lane_axes) gives the same levels
        mm = gemm_composition.get_sto("mm")
        args = dict(order=("k", "N", "m", "n"), counts={"m": 2, "n": 4, "k": 1}, operands=mm.operand_indices)
        self.assertEqual(self._mn(generate_tiling(factors={"n": 2}, **args)),
                         self._mn(generate_tiling(lanes={"B": ("n", 2)}, **args)))

    def test_two_levels_without_lanes(self):
        # where no operand's lanes run along n (a store of C) the uppercase
        # iterates once, the lowercase the whole index in its place: kNmn is kmn
        mm = gemm_composition.get_sto("mm")
        args = dict(counts={"m": 2, "n": 3, "k": 1}, operands=mm.operand_indices)
        self.assertEqual(self._mn(generate_tiling(order=("k", "m", "n"), **args)),
                         self._mn(generate_tiling(order=("k", "N", "m", "n"), **args)))

    def test_two_levels_past_the_count(self):
        # 5 columns, 2 a register: the third register's second lane is past
        # the count - skipped
        mm = gemm_composition.get_sto("mm")
        ops = generate_tiling(order=("k", "N", "m", "n"), counts={"m": 2, "n": 5, "k": 1},
                              operands=mm.operand_indices, factors={"n": 2})
        mn = self._mn(ops)
        self.assertEqual(10, len(mn))
        self.assertEqual({(m, n) for m in range(2) for n in range(5)}, set(mn))
        self.assertEqual([(0, 4), (1, 4)], mn[-2:])

