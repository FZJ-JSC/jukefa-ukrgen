"""
Register-resident operands resolve in every registry
"""

import unittest

from asmgen.registers import asm_data_type as adt

from ukrgen.flow.isa_map import make_generator
from ukrgen.flow.stages.ukr import mm_composition
from ukrgen.support.data_move import resolution_registry
from ukrgen.support.dm_resolutions.direct import direct_provider
from ukrgen.support.dm_resolutions.scalar_reduce import scalar_reduce_provider
from ukrgen.support.encoding import encode_all
from ukrgen.support.op import op_support_builder


class test_resident(unittest.TestCase):

    def test_chains_survive_without_extra_providers(self):
        # A registry built from the movement providers alone, as callers did
        # before residency existed: the temporary between fmul and fadd is in
        # a register and must still resolve.
        registry = resolution_registry()
        scalar_reduce_provider().register_resolutions(registry)
        direct_provider().register_resolutions(registry)

        osb = op_support_builder(gen=make_generator("sve"))
        osb.determine_base_support()
        req = mm_composition.get_sto("mm").req
        impls = osb.find_hw_implementations(
            req=req, registry=registry, io_dts={op: adt.FP64 for op in ("A", "B", "C")})
        chains = [e for e in encode_all(impls, req) if e.startswith("fmul")]
        self.assertTrue(chains)
        for enc in chains:
            self.assertIn("fadd", enc)
            self.assertNotIn("T0.VEC:", enc)    # resident: moves nothing


if __name__ == "__main__":
    unittest.main()
