"""
SME: outer products accumulating into a ZA tile, the tile moved slice by
slice
"""

import unittest

import tests.specializers.test_signature as t

FOPA = "fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"


def listing(**extra):
    saved, t.STAGES = t.STAGES, t.STAGES[:5]
    try:
        ctx, res = t.mm(isa="sme", **extra, **{"list-tileop-candidates": True, "mm-tileop": None})
    finally:
        t.STAGES = saved
    return (res.output or "").splitlines()


class test_sme(unittest.TestCase):

    def test_outer_product_needs_f64f64(self):
        # FP64 outer products are FEAT_SME_F64F64's: offered only with it on
        self.assertFalse(any(FOPA in l for l in listing()))
        self.assertTrue(any(FOPA in l for l in listing(**{"sme-F64F64": "on"})))

    def test_tile_slice_stores(self):
        stores = [l.split('"')[1] for l in listing(**{"sme-F64F64": "on"}) if "--store-tileop" in l]
        self.assertIn("C.TILE:slices_col", stores)
        self.assertIn("C.TILE:slices_row", stores)


    def test_vector_ops_on_a_tile(self):
        # gemm with AB in a tile: alpha's fmul stays on the tile, each slice
        # moved through a vector (slice_vec) - AB and C tiles in the encoding
        saved, t.STAGES = t.STAGES, t.STAGES[:5]
        try:
            ctx, res = t.mm(isa="sme", ukr="gemm", **{
                "sme-F64F64": "on", "AB-data-type": "FP64", "list-tileop-candidates": True,
                "mm-tileop": ["fopa(A.VEC:direct, B.VEC:direct, AB.TILE){i=m, j=n, k*=1}"],
                "store_ab-tileop": None, "store-tileop": None})
        finally:
            t.STAGES = saved
        alphamul = [l.split('"')[1] for l in (res.output or "").splitlines() if "--alphamul-tileop" in l]
        self.assertTrue(any(c.startswith("mul(AB.TILE:slice_vec_col") and "C.TILE:>slice_vec_col" in c
                            for c in alphamul), alphamul[:3])


if __name__ == "__main__":
    unittest.main()


class test_split(unittest.TestCase):
    """
    A microtile split between implementations along one index: the parts one
    after another along it, covering the same elements along every other
    """

    FOPA = "fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"

    def stos(self, **extra):
        saved, t.STAGES = t.STAGES, t.STAGES[:6]
        try:
            ctx, res = t.mm(isa="sme", **{"sme-F64F64": "on", "C-layout": ["n:c", "m:s"],
                                          "print-stos": True, **extra})
        finally:
            t.STAGES = saved
        return [{str(tl.part_offset) for tl in part.values()} for part in ctx.stos]

    def test_m(self):
        # 2v rows of outer products, then 2 rows of fmas: part 2 from 2v
        offsets = self.stos(**{"mm-tileop": [self.FOPA, "fma(A.VEC:bc_load, B.VEC:direct, C.VEC){m=1, i=n, k*=1}"],
                               "store-tileop": ["C.TILE:slices_row", "C.VEC:direct"],
                               "m": ["2", "2"], "n": ["4"]})
        self.assertIn("VL", next(iter(offsets[1])))

    def test_n(self):
        offsets = self.stos(**{"mm-tileop": [self.FOPA, "fma(A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"],
                               "store-tileop": ["C.TILE:slices_row", "C.VEC:vla_lanes"],
                               "m": ["2"], "n": ["4", "2"]})
        self.assertIn("'n'", next(iter(offsets[1])))

    def test_must_line_up(self):
        from ukrgen.flow.stages.stage import stage_error
        with self.assertRaisesRegex(stage_error, "the parts cover n differently"):
            self.stos(**{"mm-tileop": [self.FOPA, "fma(A.VEC:direct, B.VEC:bc_load, C.VEC){i=m, n=1, k*=1}"],
                         "store-tileop": ["C.TILE:slices_row", "C.VEC:vla_lanes"],
                         "m": ["2", "2"], "n": ["4"]})
        with self.assertRaisesRegex(stage_error, "split along one index"):
            self.stos(**{"mm-tileop": [self.FOPA, "fma(A.VEC:bc_load, B.VEC:direct, C.VEC){m=1, i=n, k*=1}"],
                         "store-tileop": ["C.TILE:slices_row", "C.VEC:direct"],
                         "m": ["2", "2"], "n": ["4", "3"]})
