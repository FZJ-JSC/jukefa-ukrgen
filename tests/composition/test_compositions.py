"""
Tests for the microkernel compositions and the metadata derived from them
"""

import unittest

from ukrgen.matching.math import expression_node as node, operand_ref as ref, operation as op
from ukrgen.flow.stages.ukr import (
    ukr_composition_map,
    gemm_composition,
    mm_composition,
    pack_composition,
)
from ukrgen.flow.stages.ukr.ukr import (
    ukr_composition,
    component_description as component,
    component_init,
    storage_class as storage,
    sto_description as sto,
    sto_kind,
    block_description as block,
    operand_access as acc,
    read_access as R,
    write_access as W,
    scalar,
)


class test_compositions(unittest.TestCase):

    def test_all_validate(self):
        for name, comp in ukr_composition_map.items():
            with self.subTest(ukr=name):
                comp.validate()

    def test_gemm_dataflow(self):
        self.assertEqual({
            ("mm", "AB"): acc(R.ZERO, W.REGISTER),
            ("mm", "A"): acc(R.STREAM, None),
            ("mm", "B"): acc(R.STREAM, None),
            ("betascale", "C"): acc(R.LOAD, W.REGISTER),
            ("betascale", "beta"): acc(R.LOAD, None),
            ("alphascale", "C"): acc(R.RESIDENT, W.REGISTER),
            ("alphascale", "AB"): acc(R.RESIDENT, None),
            ("alphascale", "alpha"): acc(R.LOAD, None),
            ("store", "C"): acc(R.RESIDENT, W.MEMORY),
        }, gemm_composition.dataflow())

    def test_mm_dataflow(self):
        flow = mm_composition.dataflow()
        # C is overwritten: zero-initialised, not loaded
        self.assertEqual(acc(R.ZERO, W.REGISTER), flow[("mm", "C")])
        self.assertEqual(acc(R.RESIDENT, W.MEMORY), flow[("store", "C")])

    def test_pack_dataflow(self):
        flow = pack_composition.dataflow()
        self.assertEqual(acc(R.STREAM, None), flow[("pack", "X")])
        self.assertEqual(acc(R.LOAD, None), flow[("pack", "kappa")])
        self.assertEqual(acc(None, W.REGISTER), flow[("pack", "Y")])
        # stored inside the loop over n, which Y varies along
        self.assertEqual(acc(R.RESIDENT, W.MEMORY_STREAM), flow[("store", "Y")])

    def test_scalars(self):
        self.assertEqual({"beta"}, gemm_composition.get_sto("betascale").scalars)
        self.assertEqual({"alpha"}, gemm_composition.get_sto("alphascale").scalars)
        self.assertEqual({"kappa"}, pack_composition.get_sto("pack").scalars)
        self.assertEqual(frozenset(), gemm_composition.get_sto("mm").scalars)

    def test_accumulators(self):
        self.assertEqual({"AB"}, gemm_composition.accumulators("mm"))
        self.assertEqual({"C"}, mm_composition.accumulators("mm"))
        # C is read and written by alphascale, but not in a loop
        self.assertEqual(frozenset(), gemm_composition.accumulators("alphascale"))
        self.assertEqual(frozenset(), pack_composition.accumulators("pack"))

    def test_indices(self):
        mm = gemm_composition.get_sto("mm")
        self.assertEqual(("AB", "A", "B"), mm.operands)
        self.assertEqual({"AB": ("m", "n"), "A": ("m", "k"), "B": ("k", "n")},
                         mm.operand_indices)
        self.assertEqual({"k"}, mm.reduction_indices)
        self.assertEqual({"m", "n", "k"}, set(mm.indices))
        self.assertEqual(("k", "n"), mm.live_indices("B"))

    def test_data_types(self):
        self.assertEqual("C", gemm_composition.dt_source("alpha"))
        self.assertEqual("C", gemm_composition.dt_source("C"))
        self.assertEqual("Y", pack_composition.dt_source("kappa"))
        self.assertEqual(["A", "B", "AB", "C"], gemm_composition.get_typed_components())
        self.assertEqual(["A", "B", "AB", "C"], gemm_composition.get_parameterized_components())

    def test_store_io(self):
        store = gemm_composition.get_sto("store")
        self.assertEqual(("C",), store.operands)
        self.assertEqual((True, True), store.io("C"))
        self.assertEqual({}, store.operand_indices)


def _composition(components, stos, blocks):
    return type("adhoc", (ukr_composition,), {
        "get_components": classmethod(lambda cls: components),
        "get_sto_descriptions": classmethod(lambda cls: stos),
        "get_blocks": classmethod(lambda cls: blocks),
    })


_copy = sto(name="copy", kind=sto_kind.COMPUTE, generator="scale",
            req=node(op.MOVE, ref(name="Y", indices=("m", "n")),
                     node(op.MUL, ref(name="X", indices=("m", "n")), scalar("s"))))
_xys = [component(name="X", storage=storage.MEMORY),
        component(name="Y", storage=storage.MEMORY),
        component(name="s", storage=storage.MEMORY, dt_reference="Y")]


class test_validation(unittest.TestCase):

    def test_undeclared_operand(self):
        comp = _composition(_xys[:2], [_copy], [block(stos=("copy",))])
        with self.assertRaisesRegex(ValueError, "undeclared component s"):
            comp.validate()

    def test_store_without_value(self):
        store = sto(name="store", kind=sto_kind.STORE, store_components=("X",))
        comp = _composition(_xys, [_copy, store], [block(stos=("store", "copy"))])
        with self.assertRaisesRegex(ValueError, "stores X"):
            comp.validate()

    def test_unused_loop_index(self):
        comp = _composition(_xys, [_copy], [block(stos=("copy",), loop_index="k")])
        with self.assertRaisesRegex(ValueError, "loops over k"):
            comp.validate()

    def test_unplaced_sto(self):
        comp = _composition(_xys, [_copy], [])
        with self.assertRaisesRegex(ValueError, "exactly one block"):
            comp.validate()

    def test_dt_cycle(self):
        comps = [component(name="X", storage=storage.MEMORY, dt_reference="Y"),
                 component(name="Y", storage=storage.MEMORY, dt_reference="X")]
        comp = _composition(comps, [], [])
        with self.assertRaisesRegex(ValueError, "cycle"):
            comp.validate()

    def test_sto_shape(self):
        with self.assertRaises(ValueError):
            sto(name="bad", kind=sto_kind.COMPUTE, generator="mm")
        with self.assertRaises(ValueError):
            sto(name="bad", kind=sto_kind.STORE)
        with self.assertRaisesRegex(ValueError, "MOVE"):
            sto(name="bad", kind=sto_kind.COMPUTE, generator="mm",
                req=node(op.MUL, ref(name="X", indices=("m",)), ref(name="Y", indices=("m",))))

    def test_register_component_starts_at_zero(self):
        self.assertEqual(component_init.ZERO,
                         component(name="T", storage=storage.REGISTER).initial)
        self.assertEqual(component_init.LOAD,
                         component(name="T", storage=storage.MEMORY).initial)


if __name__ == "__main__":
    unittest.main()
