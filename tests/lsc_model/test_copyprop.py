"""
Copy propagation (irmod copyprop): a copy (kappa == 1's, Y = X) renamed away -
its destination's reads its source's - only where that reads the same values,
and no other move touched (lane moves, broadcasts, slices' inserts)
"""

import types
import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.irmod.lsc.copyprop import copyprop, copyprop_tiles
from ukrgen.models.load_store_operations import lsc_move
from ukrgen.models.lsc.index import lsc_reg_index

V, T = rgt.VEC, rgt.TILE
X0, Y0, X1 = lsc_reg_index("X", [0]), lsc_reg_index("Y", [0]), lsc_reg_index("X", [1])


class op:
    """an access: a memory operand (no register type), a register"""
    def __init__(self, reg, writes, rtype=V):
        self.indices, self.rtypes = ["mem", reg], [None, rtype]
        self.reads, self.writes = ([0], [1]) if writes else ([0, 1], [])
        self.properties, self.reg_types = {}, []


def copy(src=X0, dst=Y0, rtype=V, tagged=True):
    move = lsc_move(src, dst, [], sigs=None, rtypes=[rtype, rtype])
    if tagged:
        move.add_property("copy_sto", "copy")
    return move


def program(body):
    block = types.SimpleNamespace(prologue=[], body=body, epilogue=[], tail=[], subtail=[])
    return types.SimpleNamespace(blocks=[block], cases=[], groups={})


def run(body, tiles=False):
    p = program(body)
    return (copyprop_tiles if tiles else copyprop)(None).apply(p), p.blocks[0].body


def regs(ops):
    return [str(o.indices[1].component) + str(o.indices[1].indices[0]) for o in ops if not isinstance(o, lsc_move)]


class test_copyprop(unittest.TestCase):

    def test_renamed(self):
        # load X0, Y0 = X0, store Y0: the store reads X0, the move gone
        changed, body = run([op(X0, True), copy(), op(Y0, False)])
        self.assertEqual(1, changed)
        self.assertFalse([o for o in body if isinstance(o, lsc_move)])
        self.assertEqual(["X0", "X0"], regs(body))

    def test_source_written_first(self):
        # X0 loaded anew before Y0 is stored: the copy kept
        changed, body = run([op(X0, True), copy(), op(X0, True), op(Y0, False)])
        self.assertEqual(0, changed)
        self.assertEqual(["X0", "X0", "Y0"], regs(body))

    def test_read_before(self):
        # Y0 read before the copy - an earlier iteration's: kept
        changed, body = run([op(Y0, False), op(X0, True), copy(), op(Y0, False)])
        self.assertEqual(0, changed)

    def test_other_moves_untouched(self):
        # a move not a copy (a lane move, a broadcast, a slice's insert) stays
        changed, body = run([op(X0, True), copy(tagged=False), op(Y0, False)])
        self.assertEqual(0, changed)
        self.assertEqual(1, len([o for o in body if isinstance(o, lsc_move)]))
        self.assertEqual(["X0", "Y0"], regs(body))

    def test_in_a_loop(self):
        # a slice loop's row (load, copy, insert): renamed in its block
        from ukrgen.models.load_store_operations import lsc_loop
        loop = lsc_loop(block=[op(X0, True), copy(), op(Y0, False)], subtiling=None, walks=[])
        changed, body = run([loop])
        self.assertEqual(1, changed)
        self.assertEqual(["X0", "X0"], regs(loop.block))
        self.assertNotIn(("Y", 0, V), [(i.component, i.indices[0], r) for i, r in zip(loop.indices, loop.rtypes) if r is not None])

    def test_read_after_its_loop(self):
        # the destination read after the loop - the last row's: kept
        from ukrgen.models.load_store_operations import lsc_loop
        loop = lsc_loop(block=[op(X0, True), copy(), op(Y0, False)], subtiling=None, walks=[])
        changed, body = run([loop, op(Y0, False)])
        self.assertEqual(0, changed)

    def test_tile_kept_refused(self):
        # no instruction copies a tile into another
        with self.assertRaisesRegex(ValueError, "a tile.s copy kept"):
            run([op(X0, True, T), copy(rtype=T), op(X0, True, T), op(Y0, False, T)], tiles=True)

    def test_tiles_theirs(self):
        # copyprop leaves a tile's copy to copyprop_tiles, and that a vector's
        changed, body = run([op(X0, True, T), copy(rtype=T), op(Y0, False, T)])
        self.assertEqual(0, changed)
        changed, body = run([op(X0, True), copy(), op(Y0, False)], tiles=True)
        self.assertEqual(0, changed)
        changed, body = run([op(X0, True, T), copy(rtype=T), op(Y0, False, T)], tiles=True)
        self.assertEqual(1, changed)


class test_copyprop_kernels(unittest.TestCase):

    def kernels(self, isa, irmods=None):
        from ukrgen.injectors.blis.families import family, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        vec = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
               "copy-tileop": ["move(X.VEC:direct, Y.VEC){i=m, n=1}"], "store-tileop": ["Y.VEC:direct"],
               "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        if irmods:
            vec["pre-specialize-irmods"] = irmods
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"],
                                         "cases": [{"kind": "vec", "m": [2], "params": vec}]})
        built, skipped = build_packm(isa, f"ukrgen_{isa}", fam)
        self.assertEqual([], skipped)
        text = asm_source(built[0]).splitlines()
        a = next(i for i, l in enumerate(text) if l.endswith("_case0:"))
        b = next(i for i, l in enumerate(text) if l.endswith("_case1:"))
        return text[a:b], text[b:]

    def test_copy_free_multiply_unchanged(self):
        # the copy's case moves nothing - its source loaded straight into the
        # destination (the builder), copyprop or not; the multiply's - kappa
        # broadcast, its moves - as without copyprop
        for isa, mov in (("neon", "mov v"), ("rvv", "vmv.v.v")):
            with self.subTest(isa=isa):
                copy_case, multiply = self.kernels(isa)
                kept_copy, kept_multiply = self.kernels(isa, ["-copyprop"])
                self.assertFalse([l for l in copy_case if l.strip().startswith(mov)], copy_case)
                self.assertFalse([l for l in kept_copy if l.strip().startswith(mov)], kept_copy)
                self.assertEqual(kept_multiply, multiply)

    def test_rvv_groups_and_rotations(self):
        # the tuner's: trans's rows into structfuse's group (segment stores),
        # vec3v's through rotating registers - copyprop renamed neither; loaded
        # into the destination, no vmv.v.v left
        import os
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        root = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "ukrconfig")
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(root, "rvv/k3-x100/dpackm.yaml")})
        checked = 0
        for fam in cfg.families:
            built, skipped = build_packm(cfg.isa, cfg.name, fam)
            for k in built:
                if not k.symbol.endswith(("trans14", "trans4", "vec3v", "vec7v")):
                    continue
                text = asm_source(k).splitlines()
                a = next(i for i, l in enumerate(text) if l.endswith("_case0:"))
                b = next(i for i, l in enumerate(text) if l.endswith("_case1:"))
                self.assertFalse([l for l in text[a:b] if l.strip().startswith("vmv.v.v")], k.symbol)
                checked += 1
        self.assertEqual(4, checked)

    def test_za_copy_no_mova(self):
        # ZA (packm_za): kappa 1 loads rows straight into the tile's slices -
        # no vector, no mova; the multiply's rows through vectors, movas
        import os
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        root = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "ukrconfig")
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(root, "sme/fopa_bc_vindex/dpackm.yaml")})
        fam = cfg.families[0]
        fam.cases = [c for c in fam.cases if "ztrans" == c[0]]
        built, skipped = build_packm(cfg.isa, cfg.name, fam)
        self.assertTrue(built, skipped)
        for k in built[:2]:
            text = asm_source(k).splitlines()
            a = next(i for i, l in enumerate(text) if l.endswith("_case0:"))
            b = next(i for i, l in enumerate(text) if l.endswith("_case1:"))
            starts = lambda part, t: [l for l in part if l.strip().startswith(t)]
            self.assertFalse(starts(text[a:b], "mova"), k.symbol)
            self.assertTrue(starts(text[a:b], "ld1d {za"), k.symbol)
            self.assertTrue(starts(text[b:], "mova"), k.symbol)


if __name__ == "__main__":
    unittest.main()
