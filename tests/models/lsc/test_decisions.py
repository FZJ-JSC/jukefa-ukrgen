"""
The operations generated for every path: the allocation takes a decision, and
`decide` keeps the branch it took (docs/REGISTER_ALLOCATION.md: decisions)
"""

import unittest

from ukrgen.components.tile import vla_vector_tile as vtile
from ukrgen.models.lsc import allocation
from ukrgen.models.lsc.decision import decision
from ukrgen.models.lsc.allocator_decisions import decide, plan
from ukrgen.models.lsc.addressing import offset_db
from ukrgen.models.lsc.ir import ir_block, ir_program
from ukrgen.models.lsc.offset_polynomial import offset_polynomial as offpoly
from ukrgen.models.lsc.operations import lsc_load, lsc_loop


def program(*ops, section="body") -> ir_program:
    """A program of one block holding the operations"""
    block = ir_block("A")
    block.sections[section] = list(ops)
    return ir_program(blocks=[block], offsets=offset_db(), strides={}, addr_setup={}, registers={})


def load(branch: decision | None = None) -> lsc_load:
    """
    A load, its presence depending on the branch where it has one
    :param branch: the decision it is emitted for, None where unconditional
    :return: the load
    """
    op = lsc_load("C", 0, 1, vtile, set())
    op.decision = branch
    return op


def offset(poly: str = "2*cs", comp: str = "C") -> decision:
    """
    An offset's register being taken
    :param poly: the polynomial's text
    :param comp: the component
    :return: the branch
    """
    return decision("offset", (poly, comp))


class test_decide(unittest.TestCase):

    def test_an_unconditional_operation_is_kept(self):
        # most operations: the instruction is emitted whatever was decided
        op = load()
        ir = program(op)
        self.assertEqual(0, decide(ir, set()))
        self.assertEqual([op], ir.blocks[0].sections["body"])

    def test_a_decision_taken_keeps_its_operation(self):
        op = load(offset("ga"))
        ir = program(op)
        self.assertEqual(0, decide(ir, {offset("ga")}))
        self.assertEqual([op], ir.blocks[0].sections["body"])

    def test_a_decision_left_drops_its_operation(self):
        # the question answered the other way: its operations go
        kept, dropped = load(), load(offset("gb"))
        ir = program(kept, dropped)
        self.assertEqual(1, decide(ir, {offset("gb").alternative}))
        self.assertEqual([kept], ir.blocks[0].sections["body"])

    def test_a_question_with_no_answer_is_an_error(self):
        # dropping both branches would be a kernel that silently does less
        with self.assertRaises(ValueError):
            decide(program(load(offset("ga"))), set())

    def test_the_offsets_plan_is_the_decisions_taken(self):
        # the candidates are the speller's: a name, its rank and its key - the
        # plan the emitter reserves registers by is the ones taken, in rank
        ir = program(load(offset()))
        ir.offset_candidates = {offset(): 0, offset("rs", "A"): 1}
        decide(ir, {offset(), offset("rs", "A").alternative})
        self.assertEqual({("2*cs", "C"): 0}, plan(ir, ir.decisions))
        self.assertEqual({}, plan(ir, {offset().alternative, offset("rs", "A").alternative}))

    def test_the_program_records_what_was_taken(self):
        ir = program(load(offset("ga")))
        decide(ir, {offset("ga"), decision("tail", ("m",), "mask")})
        self.assertEqual(frozenset({offset("ga"), decision("tail", ("m",), "mask")}), ir.decisions)

    def test_every_section_is_pruned(self):
        block = ir_block("A")
        block.sections["prologue"] = [load(offset("ga"))]
        block.sections["body"] = [load(offset("ga"))]
        block.sections["subtail"] = [load(offset("ga"))]
        ir = ir_program(blocks=[block], offsets=offset_db(), strides={}, addr_setup={},
                        registers={})
        self.assertEqual(3, decide(ir, {offset("ga").alternative}))
        self.assertEqual([], block.ops())

    def test_a_loops_operations_are_pruned_too(self):
        # a loop's body is where most of them are; what it reads follows
        kept, dropped = load(), load(offset("ga"))
        loop = lsc_loop(block=[kept, dropped], subtiling=None, walks=[])
        reads = len(loop.reads)
        ir = program(loop)
        self.assertEqual(1, decide(ir, {offset("ga").alternative}))
        self.assertEqual([kept], loop.block)
        self.assertLess(len(loop.reads), reads)


class test_offsets(unittest.TestCase):
    """What the allocation takes of the offsets' two spellings"""

    def program(self, budget: int) -> ir_program:
        ir = program()
        ir.offset_candidates = {offset(): 0, offset("rs", "A"): 1}
        ir.offset_registers = budget
        return ir

    def test_the_budget_takes_the_best(self):
        # the rank's first, the rest spelled plain - one name of each pair,
        # so exactly one of the two survives `decide`
        self.assertEqual({offset(), offset("rs", "A").alternative},
                         allocation.offsets(self.program(1)))

    def test_no_budget_takes_none(self):
        self.assertEqual({offset().alternative, offset("rs", "A").alternative},
                         allocation.offsets(self.program(0)))

    def test_a_budget_past_the_candidates_takes_them_all(self):
        self.assertEqual({offset(), offset("rs", "A")}, allocation.offsets(self.program(9)))


if __name__ == "__main__":
    unittest.main()
