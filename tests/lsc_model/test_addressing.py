"""
Symbolic offsets, layout strides, the offset database and address patterns
"""

import unittest

from ukrgen.lsc_model.addressing import sym, layout_strides, offset_db, addr_pattern


class test_sym(unittest.TestCase):

    def test_arithmetic(self):
        vl = sym.factor("VL")
        self.assertEqual("2*VL + 3", str(vl * 2 + 3))
        self.assertEqual(sym.factor("VL", 6), (vl * 2) * 3)
        self.assertEqual("VL*stride(C,n)", str(vl * sym.factor("stride(C,n)")))
        self.assertTrue((vl - vl).is_zero())


class test_strides(unittest.TestCase):

    def test_packed_panel(self):
        # BLIS A panel: m contiguous, k-columns MR = 2 vectors apart
        ext = {"m": sym.factor("VL", 2), "k": sym.const(4)}
        self.assertEqual({"m": sym.const(1), "k": sym.factor("VL", 2)},
                         layout_strides("A", {"m": "c", "k": "p"}, ["m", "k"], ext))

    def test_general_strides(self):
        strides = layout_strides("C", {"m": "s", "n": "s"}, [], {})
        self.assertEqual("stride(C,m)", str(strides["m"]))
        self.assertEqual("stride(C,n)", str(strides["n"]))


class test_offset_db(unittest.TestCase):

    def test_dedup_and_shift(self):
        db = offset_db()
        a = db.add("A", {"m": sym.factor("VL"), "k": sym.const(0)})
        self.assertEqual(a, db.add("A", {"m": sym.factor("VL")}))
        b = db.shifted(a, "k", sym.const(1))
        self.assertEqual("A[k:1,m:VL]", str(db[b]))
        strides = {"m": sym.const(1), "k": sym.factor("VL", 2)}
        self.assertEqual(sym.factor("VL", 3), db.elements_offset(b, strides))


class test_patterns(unittest.TestCase):

    def seq(self, spec, registers=3, n=8, phase=0):
        p = addr_pattern.parse(spec)
        return [p.select(i, phase, registers) for i in range(n)]

    def test_rotate(self):
        self.assertEqual([0, 1, 2, 0, 1, 2, 0, 1], self.seq("rotate"))

    def test_blocked(self):
        self.assertEqual([0, 0, 1, 1, 2, 2, 0, 0], self.seq("blocked:2"))

    def test_phase(self):
        self.assertEqual([1] * 8, self.seq("phase", registers=2, phase=1))
        self.assertEqual([0] * 8, self.seq("phase", registers=2, phase=2))

    def test_invalid(self):
        for spec in ("blocked", "blocked:0", "spiral", "rotate:2"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    addr_pattern.parse(spec)


if __name__ == "__main__":
    unittest.main()
