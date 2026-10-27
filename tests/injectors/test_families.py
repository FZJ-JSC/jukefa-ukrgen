"""
blisgen's kernel families: every size a family's choices build, with what
BLIS needs of each kernel, and the sizes skipped with the flow's reason
"""

import os
import tempfile
import unittest

from ukrgen.injectors.blis.families import family, configuration, build_gemm, parse_sizes
from tests.stages.test_sto import CASE_TOS

# vectors along m, B broadcast; A and B packed as BLIS packs them
VM = {"mm-tileop": ["fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"],
      "betascale-tileop": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"],
      "alphascale-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
      "store-tileop": ["C.VEC:direct"],
      "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"], "C-layout": ["m:c", "n:s"]}
VM.update(CASE_TOS)

# vectors along n, A broadcast, C row-major (its vectors along n contiguous):
# the 8x3v kind of kernel; the epilogue streams C, scheduled (--mru)
VN = {"mm-tileop": ["fma(A.VEC:bc_load, B.VEC:direct, AB.VEC){m=1, i=n, k*=1}"],
      "betascale-tileop": ["fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){m=1, i=n}"],
      "alphascale-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){m=1, i=n}"],
      "store-tileop": ["C.VEC:direct"],
      "alphamul-tileop": ["fmul(AB.VEC, alpha.VEC:bc_load, C.VEC){m=1, i=n}"],
      "add-tileop": ["fadd(AB.VEC, C.VEC:direct, C.VEC){m=1, i=n}"],
      "alphaadd-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC:direct){m=1, i=n}"],
      "betaadd-tileop": ["fma(C.VEC:direct, beta.VEC:bc_load, AB.VEC){m=1, i=n}"],
      "store_ab-tileop": ["AB.VEC:direct"],
      "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"], "C-layout": ["n:c", "m:s"],
      "mru": True}


# RVV: the broadcast operand an FP scalar the vector-scalar form takes
# (vfmacc.vf), alpha and beta too - the FP registers a file of their own
def _epilogue(tiling):
    return {"betascale-tileop": [f"fmul[bdreg:VF](C.VEC:direct, beta.FP:use_scalar, C.VEC){{{tiling}}}"],
            "alphascale-tileop": [f"fma[bdreg:VF](AB.VEC, alpha.FP:use_scalar, C.VEC){{{tiling}}}"],
            "store-tileop": ["C.VEC:direct"],
            "alphamul-tileop": [f"fmul[bdreg:VF](AB.VEC, alpha.FP:use_scalar, C.VEC){{{tiling}}}"],
            "add-tileop": [f"fadd(AB.VEC, C.VEC:direct, C.VEC){{{tiling}}}"],
            "alphaadd-tileop": [f"fma[bdreg:VF](AB.VEC, alpha.FP:use_scalar, C.VEC:direct){{{tiling}}}"],
            "betaadd-tileop": [f"fma[bdreg:VF](C.VEC:direct, beta.FP:use_scalar, AB.VEC){{{tiling}}}"],
            "store_ab-tileop": ["AB.VEC:direct"], "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"]}


VNF = dict(_epilogue("m=1, i=n"), **{"C-layout": ["n:c", "m:s"], "mm-tileop": [
    "fma[bdreg:VF](B.VEC:direct, A.FP:use_scalar, AB.VEC){m=1, i=n, k*=1}"]})
VMF = dict(_epilogue("i=m, n=1"), **{"C-layout": ["m:c", "n:s"], "mm-tileop": [
    "fma[bdreg:VF](A.VEC:direct, B.FP:use_scalar, AB.VEC){i=m, n=1, k*=1}"]})


class test_families(unittest.TestCase):

    def test_sizes(self):
        self.assertEqual([1, 2, 3], parse_sizes("1..3"))
        self.assertEqual([4], parse_sizes(4))
        self.assertEqual([2, 5], parse_sizes([2, 5]))

    def test_imm_expression(self):
        # max-imm-offset as the flow evaluates it (isa_specialize): the
        # kernel's sizes and its element size e - as blocked:'s expressions
        from ukrgen.lsc_model.addressing import arg_value, kernel_values
        imm = lambda expr, m, n, k, dt: arg_value(str(expr), kernel_values({"m": m, "n": n, "k": k},
                                                                          {"FP32": 4, "FP64": 8}[dt]))
        # one k step of the scalar side's walk: 14 and 12 floats, 14 doubles
        self.assertEqual(56, imm("ne", 2, 14, 2, "FP32"))
        self.assertEqual(48, imm("ne", 2, 12, 2, "FP32"))
        self.assertEqual(112, imm("ne", 2, 14, 2, "FP64"))
        self.assertEqual(48, imm("me", 12, 3, 2, "FP32"))
        # a step plus one element: the bump lands between steps, not inside one
        self.assertEqual(60, imm("ne+e", 2, 14, 2, "FP32"))
        self.assertEqual(52, imm("ne+e", 2, 12, 2, "FP32"))
        self.assertEqual(120, imm("ne+e", 2, 14, 2, "FP64"))
        # past the K1's and K3's window an offset costs microops: the config's
        # expression keeps within it
        self.assertEqual(63, imm("min(ne, 16e-1)", 1, 28, 1, "FP32"))
        self.assertEqual(127, imm("min(ne, 16e-1)", 2, 20, 1, "FP64"))
        self.assertEqual(56, imm("min(ne, 16e-1)", 2, 14, 2, "FP32"))
        # a number is a number, whichever way the config spells it
        self.assertEqual(63, imm(63, 2, 14, 2, "FP32"))
        self.assertEqual(127, imm("127", 2, 14, 2, "FP64"))
        with self.assertRaises(ValueError):
            imm("nz", 2, 14, 2, "FP32")

    def test_gemm_sizes(self):
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": "1..2", "n": "1..2", "default": {"FP64": "2x2"}})
        self.assertEqual({"FP64": (2, 2)}, fam.default)
        built, skipped = build_gemm("neon", "ukrgen_neon", fam)
        self.assertEqual(4, len(built), skipped)
        k = next(k for k in built if (2, 2) == k.size)
        # NEON's vectors hold two doubles: two of them along m
        self.assertEqual(("4", "2"), (k.mr, k.nr))
        self.assertEqual("bli_dgemm_ukrgen_neon_vm_4x2", k.symbol)
        self.assertEqual("col", k.c_layout)
        # packed A and B: no strides of theirs
        self.assertEqual(["k", "base(A)", "base(B)", "base(C)", "base(alpha)", "base(beta)",
                          "stride(C,n)"], k.params)

    def test_vla_sizes(self):
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [2], "n": [3]})
        built, skipped = build_gemm("sve", "ukrgen_sve", fam)
        self.assertEqual(1, len(built), skipped)
        self.assertEqual(("2*VL", "3"), (built[0].mr, built[0].nr))
        self.assertEqual("bli_dgemm_ukrgen_sve_vm_2vx3", built[0].symbol)

    def test_skipped(self):
        # 16 vectors of accumulators, times 3: more than the register file
        fam = family.from_yaml("gemm", {"family": "vm", "dtypes": ["FP64"], "params": VM,
                                        "m": [16], "n": [3]})
        built, skipped = build_gemm("neon", "ukrgen_neon", fam)
        self.assertEqual([], built)
        self.assertEqual(1, len(skipped))
        self.assertIn("registers", skipped[0][2])

    def test_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "fam.yaml")
            with open(path, "w") as f:
                f.write("isa: neon\ngemm:\n  - family: vm\n    dtypes: [FP32, FP64]\n"
                        "    m: 1..2\n    n: 1..4\n    default: {FP64: 2x4}\n")
            cfg = configuration.load(path)
        self.assertEqual(("neon", "ukrgen_neon"), (cfg.isa, cfg.name))
        self.assertEqual(["vm"], [f.name for f in cfg.families])
        self.assertEqual([1, 2, 3, 4], cfg.families[0].sizes["n"])

    def test_keys(self):
        fam = family.from_yaml("gemm", {"family": "vn", "unroll": 2, "loop-order": "mnk",
                                        "schedule": ["RAW:data::::2"], "max-data-regs": {"A": 2},
                                        "max-preload": {"B": 1}, "max-addr-regs": {"C": 2},
                                        "addr-pattern": {"C": "phase"},
                                        "params": {"order": "nmk"}})
        self.assertEqual({"k": "2", "order": "nmk", "distances": ["RAW:data::::2"],
                          "A-max-data-regs": "2", "B-max-preload": "1", "C-addr-regs": "2",
                          "C-addr-pattern": "phase"}, fam.params)
        pack = family.from_yaml("packm", {"family": "pk", "unroll": 4, "cases": [
            {"kind": "vec", "m": "1..2", "max-preload": {"X": 1}}]})
        self.assertEqual({"n": "4"}, pack.params)
        self.assertEqual(("vec", [1, 2], {"X-max-preload": "1"}), pack.cases[0])

    def test_register_limits(self):
        import re
        def loop_registers(**extra):
            fam = family.from_yaml("gemm", {"family": "vn", "dtypes": ["FP64"], "params": VN,
                                            "m": [8], "n": [3], **extra})
            built, skipped = build_gemm("sve", "ukrgen_sve", fam)
            body = built[0].program.blocks[0].sections["body"]
            return len({x for l in body if l.startswith("ld1rd") for x in re.findall(r"\{z(\d+)\.", l)})
        # A's broadcasts: a ring of what the loop's accumulators and B's
        # minimal ring leave - the epilogue's registers are freed A and B's
        # once the loop is done - at most 1 asked, the minimal 1 without preload
        self.assertEqual(5, loop_registers())
        self.assertEqual(1, loop_registers(**{"max-data-regs": {"A": 1}}))
        self.assertEqual(1, loop_registers(**{"max-preload": {"A": 0}}))

    def test_split_ratios(self):
        from ukrgen.injectors.blis.families import parse_ratios, split_combos
        # whole ratios either way, each once: 2:2 is 1:1, 2:3 neither way whole
        self.assertEqual([(1, 1), (1, 2), (1, 3), (2, 1)], parse_ratios("1..2:1..3"))
        self.assertEqual([(1, 1), (3, 1)], parse_ratios(["1:1", "3:1", "2:2"]))
        fam = family.from_yaml("gemm", {"family": "sf", "split": "m", "n": [4],
                                        "split-ratios": "1..2:1..3",
                                        "parts": [{"preset": "gemm_fopa_bc_vindex", "m": [2, 3]},
                                                  {"preset": "gemm_fma_bc"}]})
        # 2vx4v + {2, 4, 6, 1}x4v; 3v: 3, 6, 9 - 3:2 isn't whole
        self.assertEqual([(2, 2), (2, 4), (2, 6), (2, 1), (3, 3), (3, 6), (3, 9)], split_combos(fam))
        # without ratios: every combination
        plain = family.from_yaml("gemm", {"family": "sf", "split": "m", "n": [4],
                                          "parts": [{"m": [1, 2]}, {"m": [1, 2]}]})
        self.assertEqual([(1, 1), (1, 2), (2, 1), (2, 2)], split_combos(plain))
        with self.assertRaisesRegex(ValueError, "relate two parts"):
            family.from_yaml("gemm", {"family": "sf", "split": "m", "split-ratios": "1:1",
                                      "parts": [{"m": 1}, {"m": 1}, {"m": 1}]})

    def test_min_inflight(self):
        # at least 8 vectors an iteration: 2 vectors unrolled 4, 4 twice, 8 once;
        # an unroll the registers can't hold halved (x86's 1-vector case)
        from ukrgen.injectors.blis.families import build_packm
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "min-inflight": 8,
                                         "cases": [{"kind": "vec", "m": [2, 4, 8], "params": vec}]})
        self.assertEqual(8, fam.min_inflight)
        built, skipped = build_packm("sve", "ukrgen_sve", fam)
        self.assertEqual(3, len(built), skipped)
        for k in built:
            body = k.program.blocks[0].sections["body"]
            self.assertEqual(8, sum(l.startswith("ld1d") for l in body), k.symbol)
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64"], "min-inflight": 8,
                                         "cases": [{"kind": "vec", "m": [1], "params": vec}]})
        built, skipped = build_packm("avx256", "ukrgen_avx2", fam)
        self.assertEqual(1, len(built), skipped)

    def test_parallel_build(self):
        # each size one run of the flow, independent: built across processes
        # alike - the kernels' assembly rendered there, their programs kept there
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import asm_source
        vec = {"pack-tileop": ["fmul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
               "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"], "Y-layout": ["m:c", "n:s"]}
        fam = family.from_yaml("packm", {"family": "p", "dtypes": ["FP64", "FP32"], "min-inflight": 8,
                                         "cases": [{"kind": "vec", "m": [1, 2], "params": vec}]})
        seq, skipped_seq = build_packm("sve", "ukrgen_sve", fam, jobs=1)
        par, skipped_par = build_packm("sve", "ukrgen_sve", fam, jobs=2)
        self.assertEqual(4, len(par))
        self.assertEqual([k.symbol for k in seq], [k.symbol for k in par])
        self.assertEqual([asm_source(k) for k in seq], [asm_source(k) for k in par])
        self.assertTrue(all(k.program is None and k.asm for k in par))
        self.assertEqual(skipped_seq, skipped_par)

    def test_few_general_registers(self):
        # vectors along m, C column-major with a run-time stride: x86's 16
        # general registers keep two column pointers, one walks the rest
        import copy
        cfg = configuration.from_files({("gemm", "FP64"): os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "ukrconfig/avx512/fma_bc_vindex/dgemm.yaml")})
        vm = next(f for f in cfg.families if "vm" == f.name)
        for m, n in ((3, 8), (1, 14)):
            f = copy.deepcopy(vm)
            f.sizes = {"m": [m], "n": [n]}
            built, skipped = build_gemm("avx512", "ukrgen_avx512", f)
            self.assertEqual(1, len(built), skipped)


class test_family_schedule(unittest.TestCase):
    def test_refused_when_read(self):
        # a schedule entry wrong is wrong for every size: refused reading the
        # family, its name and the entry said, not each size skipped
        from ukrgen.injectors.blis.families import family
        entry = {"family": "vn", "m": [4], "n": "1..2", "schedule": ["RAW:data:freg:::", "WAR:data::::8"]}
        with self.assertRaises(ValueError) as caught:
            family.from_yaml("gemm", entry)
        self.assertIn("family vn", str(caught.exception))
        self.assertIn("RAW:data:freg:::", str(caught.exception))
        entry["schedule"] = ["RAW:data:freg:::8", "WAR:data::::8"]
        self.assertEqual("vn", family.from_yaml("gemm", entry).name)


class test_packm_dispatch_choices(unittest.TestCase):
    """
    A packm family's dispatch - which cases it tries, in which order - and
    its cases' names (two of a kind side by side): the family's to choose,
    for tuning
    """
    TRANS = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"],
             "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:p"], "X-data-regs": "4", "Y-data-regs": "8"}
    GATHER = {"pack-tileop": ["mul(X.VEC:gather, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
              "store-tileop": ["Y.VEC:direct"], "X-layout": ["n:c", "m:s"], "Y-layout": ["m:c", "n:s"]}

    def family(self, **extra):
        from ukrgen.injectors.blis.families import family
        return family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], **extra, "cases": [
            {"kind": "gather", "m": [1], "params": self.GATHER},
            {"kind": "trans", "name": "trans_shuffle", "m": [8],
             "params": dict(self.TRANS, **{"store-tileop": ["Y.VEC:shuffle"]})},
            {"kind": "trans", "name": "trans_scatter", "m": [8],
             "params": dict(self.TRANS, **{"store-tileop": ["Y.VEC:scatter"]})}]})

    def test_names_and_kinds(self):
        fam = self.family()
        self.assertEqual({"gather": "gather", "trans_shuffle": "trans", "trans_scatter": "trans"}, fam.case_kinds)
        from ukrgen.injectors.blis.families import family
        with self.assertRaises(ValueError):
            self.family(dispatch=["trans", "gather"])        # no case named trans
        with self.assertRaises(ValueError):
            family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], "cases": [
                {"kind": "vec", "name": "x", "m": [1]}, {"kind": "trans", "name": "x", "m": [4]}]})

    def test_vec_rest(self):
        # the rows a vec case packs beyond its own: the family's
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch
        self.assertEqual(4, self.family(**{"vec-rest": 4}).vec_rest)
        with self.assertRaises(ValueError):
            self.family(**{"vec-rest": -1})
        built, _ = build_packm("avx512", "ukrgen_avx512", self.family(dispatch=["gather"]))
        self.assertIn("cdim - done <= 4 )", packm_dispatch("ukrgen_avx512", "FP64", built, rest=4))
        self.assertIn("cdim - done <= 16 )", packm_dispatch("ukrgen_avx512", "FP64", built))

    def test_lmul(self):
        # RVV's LMUL by size: a number where it divides (1 elsewhere; a trans
        # case's every size), or a map; only 1, 2, 4, 8
        from ukrgen.injectors.blis.families import family, lmul_for, build_packm
        self.assertEqual([1, 2, 1, 2, 1, 2], [lmul_for(2, m, "vec") for m in range(1, 7)])
        self.assertEqual([1, 4, 2], [lmul_for({2: 4, 3: 2}, m, "vec") for m in (1, 2, 3)])
        self.assertEqual(2, lmul_for(2, 3, "trans"))
        self.assertIsNone(lmul_for(None, 3, "vec"))
        with self.assertRaises(ValueError):
            family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], "cases": [{"kind": "vec", "m": [1], "lmul": 3}]})
        fam = family.from_yaml("packm", {"family": "pk", "dtypes": ["FP64"], "lmul": 2, "cases": [
            {"kind": "vec", "m": [2], "params": {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){i=m, n=1}"],
                                                 "store-tileop": ["Y.VEC:direct"], "X-layout": ["m:c", "n:s"],
                                                 "Y-layout": ["m:c", "n:p"], "rvv-LMUL": "1"}}]})
        self.assertEqual({"vec": 2}, fam.case_lmul)        # the family's, for its cases
        built, skipped = build_packm("rvv", "ukrgen_rvv", fam)
        self.assertEqual([], built)
        self.assertIn("lmul 2 and rvv-LMUL 1", str(skipped[0][2]))

    def test_unknown_keys_refused(self):
        # a key a family's YAML doesn't know - a flow parameter beside m: -
        # refused, pointing to params:, not dropped without a word
        from ukrgen.injectors.blis.families import family
        trans = {"pack-tileop": ["mul(X.VEC:direct, kappa.VEC:bc_load, Y.VEC){m=1, i=n}"]}
        for entry in ({"family": "pk", "dtypes": ["FP64"],
                       "cases": [{"kind": "trans", "m": [4], "pre-specialize-irmods": ["+structfuse"], "params": trans}]},
                      {"family": "pk", "dtypes": ["FP64"], "pre-specialize-irmods": ["+structfuse"],
                       "cases": [{"kind": "trans", "m": [4], "params": trans}]}):
            with self.subTest(entry=sorted(entry)), self.assertRaises(ValueError) as caught:
                family.from_yaml("packm", entry)
            self.assertIn("no key pre-specialize-irmods", str(caught.exception))
            self.assertIn("params:", str(caught.exception))

    def test_order_and_what_is_built(self):
        from ukrgen.injectors.blis.families import build_packm
        from ukrgen.injectors.blis.cgen import packm_dispatch
        # AVX-512: both trans strategies of 8 rows beside each other, gather
        fam = self.family()
        built, skipped = build_packm("avx512", "ukrgen_avx512", fam)
        self.assertEqual(["gather", "trans_scatter", "trans_shuffle"], sorted({k.case for k in built}), skipped)
        self.assertEqual({"trans"}, {k.kind for k in built if k.case.startswith("trans")})
        default = packm_dispatch("ukrgen_avx512", "FP64", built)
        self.assertLess(default.index("gathered into vectors"), default.index("trans_shuffle: a full panel"))
        chosen = packm_dispatch("ukrgen_avx512", "FP64", built, ["trans_shuffle", "gather", "trans_scatter"])
        self.assertLess(chosen.index("trans_shuffle: a full panel"), chosen.index("gathered into vectors"))
        self.assertLess(chosen.index("gathered into vectors"), chosen.index("trans_scatter: a full panel"))
        # the cases the dispatch doesn't name: not built
        built, _ = build_packm("avx512", "ukrgen_avx512", self.family(dispatch=["trans_shuffle", "gather"]))
        self.assertEqual(["gather", "trans_shuffle"], sorted({k.case for k in built}))




if __name__ == "__main__":
    unittest.main()
