"""
SME's engine as state: the program's entry switches streaming mode and ZA on
before every path, its exit off after them - written through asmgen's set
(ENGINE) where the setup wrote them, the same instructions in the same place
- the state check starting from the state before it; or the caller's
(--assume-state), no switch at all
"""

import unittest

from ukrgen.lsc_model.state import check_state


class test_engine_state(unittest.TestCase):

    def test_sme(self):
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        import os
        root = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "ukrconfig")
        cfg = configuration.from_files({("packm", "FP64"): os.path.join(root, "sme/fopa_bc_vindex/dpackm.yaml")})
        fam = cfg.families[0]
        fam.cases = [c for c in fam.cases if "ztrans" == c[0]][:1]
        built, skipped = build_packm(cfg.isa, cfg.name, fam)
        self.assertTrue(built, skipped)
        code = [l.strip() for l in asm_source(built[0]).splitlines()]
        # smstart first - it zeroes the vector and predicate registers - and
        # smstop once, after every path
        self.assertEqual(1, code.count("smstart"))
        self.assertEqual(1, code.count("smstop"))
        self.assertLess(code.index("smstart"), code.index("ptrue p0.d"))
        self.assertGreater(code.index("smstop"), next(i for i, l in enumerate(code) if l.endswith("_cases_end:")))

    def test_entry_exit(self):
        # the program's entry and exit: the engine on, off - the state check
        # starting from the setup's state without its switch
        import tests.specializers.test_signature as t
        ctx, res = t.mm(**{"isa": "sme", "ukr": "pack", "X-data-type": "FP64", "Y-data-type": "FP64",
                        "pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.TILE:>slice_vec_row){m=1, i=n}"],
                        "copy-tileop": ["move(X.VEC:direct, Y.TILE:>slice_vec_row){m=1, i=n}"],
                        "store-tileop": ["Y.TILE:slices_col"], "X-layout": ["n:c", "m:s"],
                        "Y-layout": ["m:c", "n:p"], "sme-F64F64": "on", "m": "1", "n": "1"})
        program = ctx.programs[0]
        self.assertTrue(program.entry and program.exit)
        self.assertEqual({"sm": "1", "za": "1"}, program.entry[0].values)
        self.assertEqual({"sm": "0", "za": "0"}, program.exit[0].values)
        self.assertEqual([], check_state(program, {"sm": "0", "za": "0"}))

    def test_assumed(self):
        # --assume-state sm=1 za=1 (a list, or a config's mapping): the caller
        # keeps the engine on - no switch, no saves of what it would clobber
        from ukrgen.injectors.blis.families import configuration, build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        import os
        root = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "ukrconfig")
        for assume in (["sm=1", "za=1"], {"sm": 1, "za": 1}):
            with self.subTest(assume=assume):
                cfg = configuration.from_files({("packm", "FP64"): os.path.join(root, "sme/fopa_bc_vindex/dpackm.yaml")})
                fam = cfg.families[0]
                fam.cases = [(c[0], c[1], dict(c[2], **{"assume-state": assume})) + tuple(c[3:])
                             for c in fam.cases if "ztrans" == c[0]][:1]
                built, skipped = build_packm(cfg.isa, cfg.name, fam)
                self.assertTrue(built, skipped)
                code = [l.strip() for l in asm_source(built[0]).splitlines()]
                self.assertNotIn("smstart", code)
                self.assertNotIn("smstop", code)
                self.assertFalse([l for l in code if l.startswith(("str d", "stp d"))])


if __name__ == "__main__":
    unittest.main()
