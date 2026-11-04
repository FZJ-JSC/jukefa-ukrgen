"""
The analysis pass's register classes against what the emitter allocates
(docs/REGISTER_ALLOCATION.md step 3)
"""

import unittest

from asmgen.registers import adt_size

import ukrgen.emitters.allocation as A
from ukrgen.lsc_model.classes import register_class_of


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
                cls = register_class_of(key, e.program.groups, e.dts, e.bounds)
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
                elif cls.element is not None and cls.element != adt_size(e.dts[(key[0], key[1])]):
                    wrong.append((key, "element", cls.element))
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


if __name__ == "__main__":
    unittest.main()
