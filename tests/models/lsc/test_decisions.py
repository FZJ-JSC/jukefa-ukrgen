"""
The operations generated for every path: the allocation takes a decision, and
`decide` keeps the branch it took (docs/REGISTER_ALLOCATION.md: decisions)
"""

import unittest

from ukrgen.components.tile import vla_vector_tile as vtile
from ukrgen.models.lsc.decisions import decide
from ukrgen.models.lsc.addressing import offset_db
from ukrgen.models.lsc.ir import ir_block, ir_program
from ukrgen.models.lsc.offset_polynomial import offset_polynomial as offpoly
from ukrgen.models.lsc.operations import lsc_load, lsc_loop


def program(*ops, section="body") -> ir_program:
    """A program of one block holding the operations"""
    block = ir_block("A")
    block.sections[section] = list(ops)
    return ir_program(blocks=[block], offsets=offset_db(), strides={}, addr_setup={}, registers={})


def load(decision=None) -> lsc_load:
    """A load, its presence depending on the decision where it has one"""
    op = lsc_load("C", 0, 1, vtile, set())
    op.decision = decision
    return op


class test_decide(unittest.TestCase):

    def test_an_unconditional_operation_is_kept(self):
        # most operations: the instruction is emitted whatever was decided
        op = load()
        ir = program(op)
        self.assertEqual(0, decide(ir, set()))
        self.assertEqual([op], ir.blocks[0].sections["body"])

    def test_a_decision_taken_keeps_its_operation(self):
        op = load("offset:ga")
        ir = program(op)
        self.assertEqual(0, decide(ir, {"offset:ga"}))
        self.assertEqual([op], ir.blocks[0].sections["body"])

    def test_a_decision_left_drops_its_operation(self):
        kept, dropped = load(), load("offset:gb")
        ir = program(kept, dropped)
        self.assertEqual(1, decide(ir, set()))
        self.assertEqual([kept], ir.blocks[0].sections["body"])

    def test_the_program_records_what_was_taken(self):
        ir = program(load("offset:ga"))
        decide(ir, {"offset:ga", "tail:m:mask"})
        self.assertEqual(frozenset({"offset:ga", "tail:m:mask"}), ir.decisions)

    def test_every_section_is_pruned(self):
        block = ir_block("A")
        block.sections["prologue"] = [load("offset:ga")]
        block.sections["body"] = [load("offset:ga")]
        block.sections["subtail"] = [load("offset:ga")]
        ir = ir_program(blocks=[block], offsets=offset_db(), strides={}, addr_setup={},
                        registers={})
        self.assertEqual(3, decide(ir, set()))
        self.assertEqual([], block.ops())

    def test_a_loops_operations_are_pruned_too(self):
        # a loop's body is where most of them are; what it reads follows
        kept, dropped = load(), load("offset:ga")
        loop = lsc_loop(block=[kept, dropped], subtiling=None, walks=[])
        reads = len(loop.reads)
        ir = program(loop)
        self.assertEqual(1, decide(ir, set()))
        self.assertEqual([kept], loop.block)
        self.assertLess(len(loop.reads), reads)


if __name__ == "__main__":
    unittest.main()
