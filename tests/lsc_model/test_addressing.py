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
        for spec in ("blocked", "blocked:0", "spiral", "rotate:2",
                     "phase+blocked", "phase+spiral", "phase+"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    addr_pattern.parse(spec)

    def split(self, spec, registers, phases, phase, n=8):
        p = addr_pattern.parse(spec)
        return [p.select(i, phase, registers, phases) for i in range(n)]

    def test_phase_plus_rotate(self):
        # 4 registers over 2 phases: 2 each, a load rotating 0,1 and a store 2,3
        self.assertEqual([0, 1, 0, 1, 0, 1, 0, 1], self.split("phase+rotate", 4, 2, 0))
        self.assertEqual([2, 3, 2, 3, 2, 3, 2, 3], self.split("phase+rotate", 4, 2, 1))
        # C-addr-regs: 6 over 2 phases: 3 each
        self.assertEqual([0, 1, 2, 0, 1, 2, 0, 1], self.split("phase+rotate", 6, 2, 0))
        self.assertEqual([3, 4, 5, 3, 4, 5, 3, 4], self.split("phase+rotate", 6, 2, 1))
        # one register a phase: what phase gives
        self.assertEqual([0] * 8, self.split("phase+rotate", 2, 2, 0))
        self.assertEqual([1] * 8, self.split("phase+rotate", 2, 2, 1))
        # one phase: the whole file rotates, as rotate does
        self.assertEqual([0, 1, 2, 3, 0, 1, 2, 3], self.split("phase+rotate", 4, 1, 0))

    def test_phase_plus_blocked(self):
        # 4 registers over 2 phases, 2 accesses a register: 0,0,1,1 and 2,2,3,3
        self.assertEqual([0, 0, 1, 1, 0, 0, 1, 1], self.split("phase+blocked:2", 4, 2, 0))
        self.assertEqual([2, 2, 3, 3, 2, 2, 3, 3], self.split("phase+blocked:2", 4, 2, 1))
        # an expression: blocked:n/R at n 8, R 4
        self.assertEqual(2, addr_pattern.parse("phase+blocked:n/R", dict(n=8, R=4)).block)

    def test_phase_plus_split_is_shared_out(self):
        # 3 registers over 2 phases: one each, the third to the first phase's
        # count and only reached when a third phase appears
        self.assertEqual([0] * 8, self.split("phase+rotate", 3, 2, 0))
        self.assertEqual([1] * 8, self.split("phase+rotate", 3, 2, 1))
        self.assertEqual([2] * 8, self.split("phase+rotate", 3, 2, 2))


    def test_blocked_expressions(self):
        # the kernel's sizes and its address registers: 2vx14, k unrolled 4, 2 registers
        values = dict(m=2, n=14, k=4, R=2)
        for spec, block in (("blocked:mn", 28), ("blocked:mn/R", 14), ("blocked:mnk/R", 56),
                            ("blocked:n", 14), ("blocked:2*n/R", 14), ("blocked:2n", 28),
                            ("blocked:(m+1)n", 42), ("blocked:7", 7)):
            with self.subTest(spec=spec):
                self.assertEqual(block, addr_pattern.parse(spec, values).block)
        # rounded up: 28 accesses over 3 registers, 10 a register
        self.assertEqual(10, addr_pattern.parse("blocked:mn/R", dict(values, R=3)).block)

    def test_functions(self):
        # min and max: a window kept to (max-imm-offset), a floor
        from ukrgen.lsc_model.addressing import arg_value, kernel_values
        values = kernel_values({"m": 2, "n": 14, "k": 4}, 8, 2)
        self.assertEqual({"m": 2, "n": 14, "k": 4, "e": 8, "R": 2}, values)
        self.assertEqual(112, arg_value("min(ne, 16e-1)", values))
        self.assertEqual(127, arg_value("min(2ne, 16e-1)", values))
        self.assertEqual(14, arg_value("max(n, mk)", values))
        self.assertEqual(28, arg_value("2max(m, n)", values))
        # spaces are stripped, so a space does not separate arguments: side by
        # side is a product, min(n e) is min(ne)
        self.assertEqual(112, arg_value("min(n e)", values))
        for expr in ("foo(1)", "min()", "n+", "min(n,,)"):
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                arg_value(expr, values)

    def test_blocked_refused(self):
        for spec in ("blocked:x", "blocked:0", "blocked:n/0", "blocked:n-14", "blocked:n**2", "blocked:"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                addr_pattern.parse(spec, dict(m=2, n=14, k=4, R=2))


if __name__ == "__main__":
    unittest.main()
