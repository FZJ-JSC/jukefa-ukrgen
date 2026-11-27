"""
Resolutions for a SCALAR_REDUCE operand: one element that a floating-point
register of its own holds, or one lane of a vector register

SCALAR_REDUCE says the requirement's operand is one element - it says nothing
about the register the instruction takes it in. A scalar instruction takes an
FP register, a vector-scalar form an FP register, a broadcast or a lane access
a vector register. So a resolution is filed under the register type its steps
take the operand in, and the lookup asks for every type such an element
arrives in (dm_solver.key_rtypes).
"""

import unittest

from asmgen.asmblocks.op import operand_modifier as omod
from asmgen.asmblocks.op import register_type as rgt

from ukrgen.flow.stages.solve import default_registry
from ukrgen.matching.math import transformation as tf
from ukrgen.support.data_move import (
    dm_direction as dmd,
    dm_location as dml,
    get_op_rtype_req,
    orig_ref,
    tfr_key,
)
from ukrgen.support.dm_solver import key_rtypes


class test_scalar_resolutions(unittest.TestCase):

    def setUp(self):
        self.registry = default_registry()

    def scalar_reduce_keys(self, loc=dml.MEMORY):
        """every key a scalar-reduced operand's resolutions are filed under"""
        return {key: rslns for key, rslns in self.registry.tfr_map.items()
                if tf.SCALAR_REDUCE in key.tfs and loc == key.loc}

    def tags(self, tfs, rtype, ddir, loc=dml.MEMORY):
        """the resolutions registered for one key"""
        key = tfr_key(tfs=frozenset(tfs), rtype=rtype, ddir=ddir, loc=loc)
        return [rsln.unique_tag for rsln in self.registry.tfr_map.get(key, [])]

    def resolution(self, tfs, rtype, ddir, tag, loc=dml.MEMORY):
        """one resolution registered for one key, by its tag"""
        key = tfr_key(tfs=frozenset(tfs), rtype=rtype, ddir=ddir, loc=loc)
        return next(rsln for rsln in self.registry.tfr_map[key]
                    if rsln.unique_tag == tag)

    def test_filed_under_the_type_their_steps_take(self):
        """
        A resolution's key is the register type its steps take the operand in.
        A lane of a vector register is a VEC key whatever the requirement says
        about the element - filing it under FP would be a different claim than
        the instruction makes.
        """
        for key, rslns in self.scalar_reduce_keys().items():
            for rsln in rslns:
                if not rsln.steps:
                    continue    # a resident one: its key's type is the statement
                with self.subTest(tag=rsln.unique_tag, ddir=key.ddir.name):
                    self.assertEqual(get_op_rtype_req(rsln.steps), key.rtype)

    def test_the_lookup_covers_every_type_an_element_arrives_in(self):
        """
        Both kinds are looked up - the scalar instruction's FP one and the
        lane's VEC one - and an operand no transformation leaves one element is
        looked up under its own type alone
        """
        self.assertEqual((rgt.VEC, rgt.FP), key_rtypes(rgt.VEC, {tf.SCALAR_REDUCE}))
        self.assertEqual((rgt.VEC,), key_rtypes(rgt.VEC, {tf.NONE}))
        self.assertEqual((rgt.VEC,), key_rtypes(rgt.VEC, set()))
        for rtype in key_rtypes(rgt.VEC, {tf.SCALAR_REDUCE}):
            with self.subTest(rtype=rtype.name):
                self.assertTrue([rslns for key, rslns in self.scalar_reduce_keys().items()
                                 if rtype == key.rtype and dmd.IN == key.ddir])

    def test_the_scalar_entry(self):
        """
        scalar_direct: a scalar instruction's operand, loaded into its own
        floating-point register and stored from it, no modifier and no
        temporary
        """
        for ddir in (dmd.IN, dmd.OUT):
            with self.subTest(ddir=ddir.name):
                self.assertIn("scalar_direct", self.tags({tf.SCALAR_REDUCE}, rgt.FP, ddir))

        load = self.resolution({tf.SCALAR_REDUCE}, rgt.FP, dmd.IN, "scalar_direct")
        self.assertEqual(1, len(load.steps))
        self.assertEqual("load", load.steps[0].op)
        self.assertEqual(orig_ref(), load.steps[0].dest)
        self.assertEqual(rgt.FP, load.steps[0].dest_rtype)
        self.assertEqual(set(), load.op_mod_reqs)
        self.assertEqual(set(), load.opd_mod_reqs)

        store = self.resolution({tf.SCALAR_REDUCE}, rgt.FP, dmd.OUT, "scalar_direct")
        self.assertEqual(1, len(store.steps))
        self.assertEqual("store", store.steps[0].op)
        self.assertEqual([orig_ref()], store.steps[0].src)
        self.assertEqual([rgt.FP], store.steps[0].src_rtypes)

    def test_the_scalar_entry_forbids_the_vector_forms(self):
        """
        A scalar instruction takes the register itself: the forms that name a
        part of one are other resolutions' - VF's is use_scalar, a lane's
        use_lane or bc_*, a slice's the tile ones. Without the forbidding set
        scalar_direct matched RVV's vf signatures, whose scalar operand is an
        FP register with VF on its shape, and offered 228 candidates on RVV's
        gemm that are vector instructions.
        """
        for ddir in (dmd.IN, dmd.OUT):
            rsln = self.resolution({tf.SCALAR_REDUCE}, rgt.FP, ddir, "scalar_direct")
            with self.subTest(ddir=ddir.name):
                self.assertIn(omod.VF, rsln.forbidden_opd_mods)
                self.assertIn(omod.ILANE, rsln.forbidden_opd_mods)
                self.assertIn(omod.BCAST, rsln.forbidden_opd_mods)

    def test_the_scalar_entry_for_a_strided_memory(self):
        """
        One element serves any layout, so the provider registers the same move
        for memory contiguous along none of the operand's indices
        """
        self.assertIn("scalar_direct",
                      self.tags({tf.SCALAR_REDUCE}, rgt.FP, dmd.IN, dml.STRIDED_MEMORY))

    def test_the_vector_scalar_form_takes_a_scalar_register(self):
        """
        use_scalar is the VF form's: its one step loads the element into an FP
        register, so it belongs to the FP key and not the vector one
        """
        self.assertIn("use_scalar", self.tags({tf.SCALAR_REDUCE}, rgt.FP, dmd.IN))
        self.assertNotIn("use_scalar", self.tags({tf.SCALAR_REDUCE}, rgt.VEC, dmd.IN))
        self.assertIn("use_scalar", self.tags({tf.SCALAR_REDUCE}, rgt.FP, dmd.OUT))

    def test_the_lane_forms_stay_vector(self):
        """
        A broadcast or a lane access loads a whole register and uses one
        element of it, so it keeps the vector key
        """
        for tag in ("bc_load", "bc_lane", "bc_lanes", "bc_scalar", "bc_block",
                    "use_lane", "scalar_to_lane"):
            with self.subTest(tag=tag, ddir="IN"):
                self.assertIn(tag, self.tags({tf.SCALAR_REDUCE}, rgt.VEC, dmd.IN))
                self.assertNotIn(tag, self.tags({tf.SCALAR_REDUCE}, rgt.FP, dmd.IN))
        for tag in ("use_lane", "lane_to_scalar"):
            with self.subTest(tag=tag, ddir="OUT"):
                self.assertIn(tag, self.tags({tf.SCALAR_REDUCE}, rgt.VEC, dmd.OUT))

    def test_resident_in_a_floating_point_register(self):
        """
        An operand that is one element and already in an FP register moves
        nothing. The vector type's own resident entry is not registered: it
        would say a whole register is one element of the requirement, which is
        a family of 1-element microtiles built from vector instructions -
        Neon's gemm grew from 704 candidates to 2332 when it was.
        """
        for ddir in (dmd.IN, dmd.OUT):
            with self.subTest(ddir=ddir.name):
                self.assertIn("resident",
                              self.tags({tf.SCALAR_REDUCE}, rgt.FP, ddir, dml.REGISTER))
                self.assertNotIn("resident",
                                 self.tags({tf.SCALAR_REDUCE}, rgt.VEC, ddir, dml.REGISTER))


if __name__ == "__main__":
    unittest.main()
