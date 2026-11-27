"""
The signatures' register operands bound into the operations: a masked access
carries its mask as a slot - its register type, the operand's name - so that
the passes after it can see the value (docs/REGISTER_ALLOCATION.md: the
signatures' operands in the IR)
"""

import unittest

from asmgen.asmblocks.op import operand_role as orl, register_type as rgt

from ukrgen.components.tile import vla_vector_tile as vtile
from ukrgen.irmod.lsc.bind import bind_mask, mask_operand
from ukrgen.models.lsc.operations import lsc_load


class _shape:
    """A signature operand: its register type and its role"""

    def __init__(self, rtype, orole):
        self.rtype = rtype
        self.orole = orole


class _sig:
    """A signature: its operands and what it clobbers"""

    def __init__(self, operands, clobber=()):
        self.operands = operands
        self.clobber_list = list(clobber)


def load() -> lsc_load:
    """A load of a vector, its address in a general register"""
    return lsc_load("C", 0, 1, vtile, set())


def data_only() -> _sig:
    """A signature with no mask"""
    return _sig({"adreg": _shape(rgt.VEC, orl.DATA),
                 "agreg": _shape(rgt.GP, orl.ADDRESS)})


def masked(clobber=()) -> _sig:
    """A signature masking with `amreg`"""
    return _sig({"adreg": _shape(rgt.VEC, orl.DATA),
                 "agreg": _shape(rgt.GP, orl.ADDRESS),
                 "amreg": _shape(rgt.MASK, orl.MASK)}, clobber=clobber)


class test_bind(unittest.TestCase):

    def test_a_masked_access_carries_its_mask(self):
        # the slot after the data one, the mask's own register type and the
        # operand's name - not read yet: what reads it is the step after this
        op = load()
        self.assertTrue(bind_mask(op, sigs=[masked()]))
        self.assertEqual(3, len(op.indices))
        self.assertEqual(rgt.MASK, op.rtypes[-1])
        self.assertNotIn(len(op.indices) - 1, op.reads)
        self.assertEqual("amreg", op.hw_operands[-1])
        self.assertEqual("mask", op.indices[-1].component)

    def test_a_live_binding_reads_its_mask(self):
        # phase (b): the slot the passes after this one see
        op = load()
        self.assertTrue(bind_mask(op, sigs=[masked()], live=True))
        self.assertIn(len(op.indices) - 1, op.reads)
        self.assertNotIn(len(op.indices) - 1, op.writes)

    def test_a_clobbered_mask_is_written_too(self):
        # AVX's gathers clear the mask they read: read and written by the same
        # instruction, so that nothing is scheduled across it
        op = load()
        self.assertTrue(bind_mask(op, sigs=[masked(clobber=["amreg"])], live=True))
        self.assertIn(len(op.indices) - 1, op.reads)
        self.assertIn(len(op.indices) - 1, op.writes)

    def test_an_unmasked_access_is_left_alone(self):
        op = load()
        indices = list(op.indices)
        self.assertFalse(bind_mask(op, sigs=[data_only()]))
        self.assertEqual(indices, op.indices)

    def test_signatures_disagreeing_on_the_mask_bind_nothing(self):
        # one form masked, one not: whichever the emitter takes, the slot would
        # be wrong - so none is added
        sigs = [masked(), data_only()]
        self.assertIsNone(mask_operand(sigs))
        op = load()
        self.assertFalse(bind_mask(op, sigs=sigs))

    def test_the_slot_is_bound_once(self):
        op = load()
        self.assertTrue(bind_mask(op, sigs=[masked()]))
        self.assertFalse(bind_mask(op, sigs=[masked()]))
        self.assertEqual(1, sum(1 for slot in op.hw_operands if "amreg" == slot))


if __name__ == "__main__":
    unittest.main()
