"""
The resolutions a scalar instruction's operands need: one element that is
entered into, and left in, a floating-point register

Nothing looks them up yet - a scalar-reduced operand is still typed VEC
(dm_solver's deduce_operand_rtype reads the untransformed hardware AST) - so
every existing kernel's candidate set is unchanged by their registration. What
they are for is the key such an operand gets once the type comes from its
transformations, and the last test here pins where they must not be
registered: under the vector register type, where a resident entry would say a
whole register is one element of the requirement.
"""

import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.flow.stages.solve import default_registry
from ukrgen.matching.math import transformation as tf
from ukrgen.support.data_move import (
    dm_direction as dmd,
    dm_location as dml,
    orig_ref,
    tfr_key,
)


class test_scalar_resolutions(unittest.TestCase):

    def setUp(self):
        self.registry = default_registry()

    def tags(self, tfs, rtype, ddir, loc=dml.MEMORY):
        """the resolutions registered for one key"""
        key = tfr_key(tfs=frozenset(tfs), rtype=rtype, ddir=ddir, loc=loc)
        return [rsln.unique_tag for rsln in self.registry.tfr_map.get(key, [])]

    def resolution(self, tfs, rtype, ddir, tag, loc=dml.MEMORY):
        """one resolution registered for one key, by its tag"""
        key = tfr_key(tfs=frozenset(tfs), rtype=rtype, ddir=ddir, loc=loc)
        return next(rsln for rsln in self.registry.tfr_map[key]
                    if rsln.unique_tag == tag)

    def test_direct_entry(self):
        """
        A floating-point scalar is loaded and stored directly: no VF form and
        no broadcast, which is what use_scalar and bc_* ask of a vector
        operation's scalar operand
        """
        for ddir in (dmd.IN, dmd.OUT):
            with self.subTest(ddir=ddir.name):
                self.assertIn("scalar_direct", self.tags({tf.SCALAR_REDUCE}, rgt.FP, ddir))

    def test_direct_steps(self):
        """
        IN loads into the operand's own floating-point register, OUT stores
        from it: one element, no temporary and no modifier
        """
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

    def test_direct_entry_for_a_strided_memory(self):
        """
        One element serves any layout, so the provider registers the same move
        for memory contiguous along none of the operand's indices
        """
        self.assertIn("scalar_direct",
                      self.tags({tf.SCALAR_REDUCE}, rgt.FP, dmd.IN, dml.STRIDED_MEMORY))

    def test_resident(self):
        """
        A scalar-reduced operand already in a floating-point register moves
        nothing: the operation reads or writes it where it is
        """
        for ddir in (dmd.IN, dmd.OUT):
            with self.subTest(ddir=ddir.name):
                self.assertIn("resident",
                              self.tags({tf.SCALAR_REDUCE}, rgt.FP, ddir, dml.REGISTER))

    def test_not_under_the_vector_type(self):
        """
        Neither belongs to a vector register: there a scalar-reduced operand is
        one the operation broadcasts into a register (bc_load, bc_lane,
        use_scalar), and a resident entry would instead say the whole register
        holds one element - an accumulator a vector operation fills lane by
        lane. Registering both under VEC took Neon's gemm from 704 candidates
        to 2332 before this test existed.
        """
        for ddir in (dmd.IN, dmd.OUT):
            with self.subTest(ddir=ddir.name):
                self.assertNotIn("scalar_direct", self.tags({tf.SCALAR_REDUCE}, rgt.VEC, ddir))
                self.assertNotIn("resident",
                                 self.tags({tf.SCALAR_REDUCE}, rgt.VEC, ddir, dml.REGISTER))
        # the vector-keyed resolutions are the ones that need an instruction form
        self.assertIn("use_scalar", self.tags({tf.SCALAR_REDUCE}, rgt.VEC, dmd.IN))


if __name__ == "__main__":
    unittest.main()
