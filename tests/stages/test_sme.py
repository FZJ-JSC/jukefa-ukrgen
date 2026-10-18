"""
SME: outer products accumulating into a ZA tile, the tile moved slice by
slice
"""

import unittest

import specializers.test_signature as t

FOPA = "fopa(A.VEC:direct, B.VEC:direct, C.TILE){i=m, j=n, k*=1}"


def listing(**extra):
    saved, t.STAGES = t.STAGES, t.STAGES[:5]
    try:
        ctx, res = t.mm(isa="sme", **extra, **{"list-to-candidates": True, "mm-to": None})
    finally:
        t.STAGES = saved
    return (res.output or "").splitlines()


class test_sme(unittest.TestCase):

    def test_outer_product_needs_f64f64(self):
        # FP64 outer products are FEAT_SME_F64F64's: offered only with it on
        self.assertFalse(any(FOPA in l for l in listing()))
        self.assertTrue(any(FOPA in l for l in listing(**{"sme-F64F64": "on"})))

    def test_tile_slice_stores(self):
        stores = [l.split('"')[1] for l in listing(**{"sme-F64F64": "on"}) if "--store-to" in l]
        self.assertIn("C.TILE:slices_col", stores)
        self.assertIn("C.TILE:slices_row", stores)


if __name__ == "__main__":
    unittest.main()
