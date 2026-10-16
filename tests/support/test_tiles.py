"""
Tests for tiles inferred from chosen implementations
"""

import unittest

from asmgen.registers import asm_data_type as adt

from ukrgen.components.tile import dimension_properties as dimp, dimension_type as dimt
from ukrgen.flow.isa_map import make_generator
from ukrgen.flow.stages.solve import default_registry
from ukrgen.flow.stages.ukr import gemm_composition
from ukrgen.support.op import op_support_builder
from ukrgen.support.encoding import encode_all
from ukrgen.support.data_move import dm_location as dml
from ukrgen.support.tiles import index_extents, operand_tiles, ONE

VLA = dimp(dt=dimt.vla, size=1, sdt=dimt.vla, sd_size=1)


def candidates(isa, sto_name, dt=adt.FP64):
    gen = make_generator(isa)
    osb = op_support_builder(gen=gen)
    osb.determine_base_support()
    sto = gemm_composition.get_sto(sto_name)
    impls = osb.find_hw_implementations(
        req=sto.req, registry=default_registry(),
        io_dts={op: dt for op in sto.operands},
        io_locs={"AB": (dml.REGISTER, dml.REGISTER)})
    return gen, sto, dict(zip(encode_all(impls, sto.req), impls))


class test_tiles(unittest.TestCase):

    def test_sve_fma(self):
        gen, sto, cands = candidates("sve", "mm")
        impl = cands["fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"]
        self.assertEqual({"m": VLA}, index_extents(gen, impl))
        tiles = operand_tiles(gen, impl, sto.req)
        self.assertEqual((VLA, ONE), (tiles["A"].dima, tiles["A"].dimb))     # A[m,k]
        self.assertEqual((ONE, ONE), (tiles["B"].dima, tiles["B"].dimb))     # broadcast
        self.assertEqual((VLA, ONE), (tiles["AB"].dima, tiles["AB"].dimb))   # AB[m,n]

    def test_neon_fixed_width(self):
        # fixed-width vectors: two FP64 elements along m. (Vectors along n need
        # the rank-1 matcher or TRANSPOSE resolutions; neither is in yet.)
        gen, sto, cands = candidates("neon", "mm")
        two = dimp(dt=dimt.fixed, size=2, sdt=dimt.fixed, sd_size=2)
        impl = cands["fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"]
        self.assertEqual({"m": two}, index_extents(gen, impl))
        tiles = operand_tiles(gen, impl, sto.req)
        self.assertEqual((two, ONE), (tiles["AB"].dima, tiles["AB"].dimb))

    def test_scalar_operand(self):
        gen, sto, cands = candidates("sve", "betascale")
        impl = next(iter(cands.values()))
        tiles = operand_tiles(gen, impl, sto.req)
        self.assertEqual((ONE, ONE), (tiles["beta"].dima, tiles["beta"].dimb))


if __name__ == "__main__":
    unittest.main()
