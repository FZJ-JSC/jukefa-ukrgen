"""
Extents as dimensions, counts as their quotients: fixed counts unroll, vla
ones (fractions of a vector length) loop
"""

import unittest
from fractions import Fraction

from ukrgen.components.tile import (
    dimension_properties as dimp, dimension_type as dimt, tile, subtiling,
)

V = lambda n: dimp(dt=dimt.vla, size=n)
F = lambda n: dimp(dt=dimt.fixed, size=n)


class test_dimensions(unittest.TestCase):

    def test_quotients(self):
        self.assertEqual(V(Fraction(1, 4)), V(1) / F(4))       # VL/4 times
        self.assertTrue((V(1) / F(4)).runtime)
        self.assertEqual(F(1), V(1) / V(1))
        self.assertEqual(F(4), F(8) / F(2))
        with self.assertRaises(ValueError):
            F(4) / V(1)

    def test_unrolls(self):
        # a vector holds a multiple of 16 bytes: of doubles, 2
        self.assertEqual([1, 2], (V(1) / F(1)).count_unrolls(2))
        self.assertEqual([], (V(1) / F(4)).count_unrolls(2))   # VL/4 needn't be whole
        self.assertEqual([1, 2, 4], (V(1) / F(1)).count_unrolls(4))
        self.assertEqual([1, 2, 4, 8], F(8).count_unrolls(0))

    def test_subtiling(self):
        one = F(1)
        vec, elem = tile(V(1), one), tile(one, one)
        count = elem.count_in(vec)
        self.assertEqual((V(1), one), count)
        vec.nested = subtiling(shape=elem, count=count[0], unroll=2, registers=2)
        self.assertTrue(vec.nested.loop)
        lanes = tile(F(2), one)
        lanes.nested = subtiling(shape=elem, count=elem.count_in(lanes)[0])
        self.assertFalse(lanes.nested.loop)


if __name__ == "__main__":
    unittest.main()
