"""
In-register transposes from asmgen's permutes: the fewest rounds per ISA
and type, each network checked again by simulating it on a block
"""
import unittest

from asmgen.asmblocks.neon import neon
from asmgen.asmblocks.sve import sve
from asmgen.asmblocks.avx import fma256, avx512
from asmgen.asmblocks.op.opmove import permuted
from asmgen.registers import asm_data_type as adt, adt_size

from ukrgen.support.transpose import transpose_network


def simulate(net, lanes, ebits):
    regs = [[r * lanes + c for c in range(lanes)] for r in range(lanes)]
    for rnd in net.rounds:
        nxt = [list(r) for r in regs]
        for i in range(lanes):
            j = i ^ rnd.distance
            if i < j:
                for k, which in ((i, "first"), (j, "second")):
                    p = rnd.params(which)
                    nxt[k] = permuted(p["pattern"], regs[i], regs[j], element_bits=ebits,
                                      bits=p["bits"], segment=p["segment"])
        regs = nxt
    return regs


class test_transpose(unittest.TestCase):
    def test_rounds(self):
        for gen, dt, rounds in ((neon, adt.FP64, 1), (neon, adt.FP32, 2), (fma256, adt.FP64, 2),
                                (fma256, adt.FP32, 3), (avx512, adt.FP64, 3), (avx512, adt.FP32, 4)):
            with self.subTest(gen=gen.__name__, dt=dt.name):
                g = gen()
                net = transpose_network(g, dt)
                self.assertIsNotNone(net)
                self.assertEqual(rounds, len(net.rounds))
                lanes = g.simd_size // adt_size(dt)
                regs = simulate(net, lanes, 8 * adt_size(dt))
                for col, reg in enumerate(net.columns):
                    self.assertEqual([r * lanes + col for r in range(lanes)], regs[reg])

    def test_amds(self):
        # AVX-512's 8x8 doubles: in-lane unpacks, then 128-bit blocks unzipped twice
        net = transpose_network(avx512(), adt.FP64)
        self.assertEqual([("zip_lo", 64, 128), ("uzp_even", 128, None), ("uzp_even", 128, None)],
                         [(r.params("first")["pattern"], r.params("first")["bits"], r.params("first")["segment"])
                          for r in net.rounds])

    def test_none_where_vla(self):
        self.assertIsNone(transpose_network(sve(), adt.FP64))


if __name__ == "__main__":
    unittest.main()
