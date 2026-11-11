"""
The analysis pass's register classes against what the emitter allocates
(docs/REGISTER_ALLOCATION.md step 3)
"""

import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.models.lsc import classes

import ukrgen.emitters.allocation as A
from ukrgen.models.lsc.classes import register_class_of


class test_register_classes(unittest.TestCase):
    def check(self, path, kind, dt, family=None, sizes=None):
        import copy
        from ukrgen.injectors.blis.families import configuration, build_gemm
        seen, wrong = [], []
        take = A.register_allocator.take

        def checked(alloc, idx, rtype):
            e = alloc.e
            key = (idx.component, idx.indices[0], rtype)
            fresh = key not in e.phys
            reg = take(alloc, idx, rtype)
            if fresh and key in e.numbers:
                cls = register_class_of(key, e.program.groups, e.dts, e.bounds, e.gen.treg_tag)
                tag, number = e.numbers[key]
                seen.append(key)
                if cls is None or cls.tag != tag:
                    wrong.append((key, "tag", cls, tag))
                elif cls.allowed is not None and number not in cls.allowed:
                    wrong.append((key, "allowed", cls.allowed, number))
                elif cls.size > 1:
                    first = key[1] - key[1] % cls.align if cls.align > 1 else None
                    if first is not None:
                        start = e.numbers.get((key[0], first, rtype), (tag, None))[1]
                        if start is None or start % cls.align:
                            wrong.append((key, "align", cls.align, start))
            return reg
        A.register_allocator.take = checked
        try:
            c = configuration.from_files({(kind, dt): path})
            fam = copy.deepcopy(next(f for f in c.families if family is None or family == f.name))
            if sizes:
                fam.sizes = sizes
            built, _ = build_gemm(c.isa, c.name, fam)
        finally:
            A.register_allocator.take = take
        self.assertTrue(built)
        self.assertTrue(seen)
        self.assertEqual([], wrong)

    def test_sme_tiles(self):
        self.check("ukrconfig/sme/fopa_bc_vindex/dgemm.yaml", "gemm", "FP64", sizes={"m": [2], "n": [2]})

    def test_rvv_groups(self):
        self.check("ukrconfig/rvv/fma_vf_m2/dgemm.yaml", "gemm", "FP64", family="vm", sizes={"m": [2], "n": [4]})

    def test_sve_neon_x86(self):
        for path, family, sizes in (("ukrconfig/sve/fma_bc_vindex/dgemm.yaml", "vm", {"m": [2], "n": [4]}),
                                    ("ukrconfig/neon/fma_lane/dgemm.yaml", "vm", {"m": [2], "n": [4]}),
                                    ("ukrconfig/avx2/fma_bc_blocks/dgemm.yaml", "vm", {"m": [2], "n": [4]})):
            with self.subTest(config=path):
                self.check(path, "gemm", "FP64", family=family, sizes=sizes)

    def test_an_address_register_is_a_file_too(self):
        # SME's slice index lives in w12-w15: a general register whose class
        # says so, the allocation's to place within
        key = ("C", 0, rgt.GP)
        klass = classes.register_class_of(key, {}, {}, {key: [12, 13, 14, 15]})
        self.assertIsNotNone(klass)
        self.assertEqual("greg", klass.tag)
        self.assertEqual((12, 13, 14, 15), klass.allowed)
        # one no signature limits: any general register
        unlimited = classes.register_class_of(key, {}, {}, {})
        self.assertEqual("greg", unlimited.tag)
        self.assertIsNone(unlimited.allowed)


if __name__ == "__main__":
    unittest.main()


class test_units(unittest.TestCase):
    """Units, fit and compatibility by the tracker's knowledge (asmgen's): no ISA's layout in ukrgen"""
    def setUp(self):
        from ukrgen.flow.isa_map import make_generator
        self.rt = make_generator("sme").get_reg_tracker()

    def test_tiles(self):
        from ukrgen.models.lsc.classes import register_class, units, fits, compatible
        d, s, h = register_class("treg64"), register_class("treg32"), register_class("treg16")
        self.assertTrue(units(s, 0, self.rt) & units(h, 0, self.rt))
        self.assertTrue(units(s, 1, self.rt) & units(d, 5, self.rt))
        self.assertFalse(units(s, 0, self.rt) & units(s, 1, self.rt))
        self.assertFalse(units(s, 1, self.rt) & units(h, 0, self.rt))
        self.assertFalse(units(d, 0, self.rt) & units(d, 1, self.rt))
        self.assertTrue(fits(s, 3, self.rt))
        self.assertFalse(fits(s, 5, self.rt))
        self.assertTrue(fits(d, 7, self.rt))
        self.assertTrue(compatible(s, d, self.rt))

    def test_groups_and_files(self):
        from ukrgen.models.lsc.classes import register_class, units, fits, compatible
        g = register_class("vreg", size=2, align=2)
        self.assertEqual({("vreg", 4), ("vreg", 5)}, units(g, 4, self.rt))
        self.assertFalse(fits(g, 3, self.rt))
        v, f = register_class("vreg"), register_class("freg")
        self.assertTrue(units(v, 3, self.rt) & units(f, 3, self.rt))
        self.assertTrue(compatible(v, f, self.rt))
        self.assertFalse(compatible(v, g, self.rt))
        self.assertFalse(fits(register_class("vreg", allowed=(1, 2)), 3, self.rt))

    def test_an_address_register_is_a_file_too(self):
        # SME's slice index lives in w12-w15: a general register whose class
        # says so, the allocation's to place within
        key = ("C", 0, rgt.GP)
        klass = classes.register_class_of(key, {}, {}, {key: [12, 13, 14, 15]})
        self.assertIsNotNone(klass)
        self.assertEqual("greg", klass.tag)
        self.assertEqual((12, 13, 14, 15), klass.allowed)
        # one no signature limits: any general register
        unlimited = classes.register_class_of(key, {}, {}, {})
        self.assertEqual("greg", unlimited.tag)
        self.assertIsNone(unlimited.allowed)


if __name__ == "__main__":
    unittest.main()
