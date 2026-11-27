"""
The machinery's registers as values: an `lsc_set` writes a mask or an index
vector, and the analysis and the allocation treat it as any other value
"""

import unittest

from asmgen.asmblocks.op import register_type as rgt

from ukrgen.models.lsc import allocation
from ukrgen.models.lsc.addressing import offset_db, offpoly
from ukrgen.models.lsc.ir import ir_block, ir_program
from ukrgen.models.lsc.operations import (lsc_set, set_index, set_mask_alltrue,
                                           set_mask_tail)
from ukrgen.models.lsc.offset_polynomial import offset_polynomial as offpoly


def program_with(*ops) -> ir_program:
    """
    A program of one straight-line block holding the operations
    :param ops: the operations
    :return: the IR, its offsets and tables empty
    """
    block = ir_block(name="mm")
    block.body = list(ops)
    return ir_program(blocks=[block], offsets=offset_db(), strides={},
                      addr_setup={}, registers={})


class test_set(unittest.TestCase):

    def test_a_mask_is_a_value(self):
        # a set's mask: a value of the mask file, live where it is set - what
        # the renamer and the allocation see, the payload being the emitter's
        program = program_with(lsc_set("mask", 0, rgt.MASK, set_mask_alltrue()))
        resources = allocation.resources(pools={"mreg": 1})
        problem = allocation.analyse(program, resources)
        key = ("mask", 0, rgt.MASK)
        self.assertIn(key, problem.values)
        entry = problem.values[key]
        self.assertEqual("mreg", entry.tag)
        self.assertIsNotNone(entry.register_class)
        self.assertEqual(1, entry.register_class.size)
        self.assertTrue(entry.ranges)
        self.assertEqual(1, problem.pressure("mreg"))

    def test_the_allocation_places_a_mask(self):
        program = program_with(lsc_set("mask", 0, rgt.MASK, set_mask_alltrue()))
        resources = allocation.resources(pools={"mreg": 1})
        problem = allocation.analyse(program, resources)
        result = allocation.allocate(problem, resources)
        self.assertEqual(("mreg", 0), result.number(("mask", 0, rgt.MASK)))
        self.assertEqual([], result.unfitted)
        self.assertEqual([], allocation.validate(problem, result, resources))

    def test_a_tail_mask_carries_its_count(self):
        # the count it masks to is a parameter's, and the element type its lanes'
        from asmgen.registers import asm_data_type as adt
        payload = set_mask_tail("tail(m)", adt.FP64)
        op = lsc_set("mask(m)", 0, rgt.MASK, payload)
        self.assertEqual("tail(m)", payload.count)
        self.assertEqual(adt.FP64, payload.dt)
        self.assertEqual("mask(m)0 <- set(set_mask_tail)", str(op))

    def test_an_index_vector_carries_its_stride(self):
        # the emitter reads the stride off the payload: a constant here, a
        # run-time stride register or an expression of them in a real kernel
        stride = offpoly.factor("stride(A,k)", 2) + offpoly.const(8)   # a sum, unequal rows
        payload = set_index("index(A)", stride)
        op = lsc_set("index(A)", 0, rgt.VEC, payload)
        self.assertEqual("index(A)", payload.component)
        self.assertEqual(stride, payload.stride)
        self.assertEqual(offpoly.const(8), payload.stride - offpoly.factor("stride(A,k)", 2))
        self.assertEqual("index(A)0 <- set(set_index)", str(op))

    def test_the_writes_are_names_the_ops_can_read(self):
        # the value flows from the set to its readers by name and type: an
        # operation reading it keeps it live
        program = program_with(lsc_set("mask", 0, rgt.MASK, set_mask_alltrue()))
        body = program.blocks[0].sections["body"]
        self.assertEqual([0], body[0].writes)
        self.assertEqual([], body[0].reads)
        self.assertEqual([rgt.MASK], body[0].rtypes)


if __name__ == "__main__":
    unittest.main()
