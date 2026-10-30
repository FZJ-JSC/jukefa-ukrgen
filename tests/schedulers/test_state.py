"""
Processor state as dependencies: what an operation reads and writes
(reads_state, writes_state - asmgen's signatures say) orders it like a
register - read after write, write after read, write after write - in both
dependency analyses; distance specs for it (RAW:state::::N)
"""
import unittest

from ukrgen.models.lsc.reg import lsc_reg_type
from ukrgen.schedulers.dependency import dependency_type as dept, get_dependencies
from ukrgen.schedulers.distance import distance_specification
from ukrgen.schedulers.list_scheduler import dependencies


class op_with_state:
    """an operation with state and no registers"""
    def __init__(self, reads=(), writes=()):
        self.reads, self.writes, self.indices, self.reg_types, self.rtypes, self.tiles = [], [], [], [], [], []
        self.reads_state, self.writes_state = frozenset(reads), frozenset(writes)


class test_state_dependencies(unittest.TestCase):
    def ops(self):
        # vsetvli, a vector operation, vsetvli again, another vector operation
        return [op_with_state(writes={"vlen"}), op_with_state(reads={"vlen"}),
                op_with_state(writes={"vlen"}), op_with_state(reads={"vlen"})]

    def test_list_scheduler(self):
        edges = {(e.src, e.dst, e.dep) for e in dependencies(self.ops(), loop=False)
                 if lsc_reg_type.state == e.key[0]}
        self.assertEqual({(0, 1, dept.RAW), (1, 2, dept.WAR), (0, 2, dept.WAW), (2, 3, dept.RAW)}, edges)

    def test_readers_not_ordered(self):
        self.assertEqual([], dependencies([op_with_state(reads={"vlen"}), op_with_state(reads={"vlen"})],
                                          loop=False))

    def test_pairwise(self):
        write, read = op_with_state(writes={"sm"}), op_with_state(reads={"sm"})
        deps = get_dependencies(write, read)
        self.assertTrue(deps[dept.RAW])
        self.assertFalse(get_dependencies(read, op_with_state(reads={"vlen"}))[dept.RAW])

    def test_distance(self):
        spec = distance_specification.from_string("RAW:state::::5")
        self.assertEqual(lsc_reg_type.state, spec.reg_type)
        self.assertEqual(5, spec.apply(op_with_state(writes={"vlen"}), op_with_state(reads={"vlen"})))
        self.assertEqual(0, spec.apply(op_with_state(reads={"vlen"}), op_with_state(reads={"vlen"})))
        # a data spec doesn't apply to state
        self.assertEqual(0, distance_specification.from_string("RAW:data::::5").apply(
            op_with_state(writes={"vlen"}), op_with_state(reads={"vlen"})))




class test_check_state(unittest.TestCase):
    """
    The state through a program: a state set once in the first block's
    prologue (a masked tail's mask) begins every later section; an
    operation's own reads (extra_reads_state) must be set; a section ends
    with the setup's states as they were
    """
    class reader:
        def __init__(self, *names):
            self.extra_reads_state = set(names)

        def state_sigs(self):
            return []

    class block:
        def __init__(self, prologue=(), body=()):
            self.prologue, self.body = list(prologue), list(body)
            self.epilogue, self.tail, self.subtail = [], [], []

    class program:
        def __init__(self, *blocks):
            self.blocks, self.cases = list(blocks), []
            # the entry and exit (the engine's switches): none here
            self.entry, self.exit = [], []

    def check(self, *blocks):
        from ukrgen.lsc_model.state import check_state
        return check_state(self.program(*blocks), {"vlen": "max"})

    def test_mask_set_once(self):
        from ukrgen.models.load_store_operations import lsc_state
        self.assertEqual([], self.check(self.block(prologue=[lsc_state({"mask(m)": "tail(m)"})],
                                                   body=[self.reader("mask(m)")])))

    def test_mask_unset(self):
        problems = self.check(self.block(body=[self.reader("mask(m)")]))
        self.assertTrue(any("reads mask(m) before it's set" in p for p in problems), problems)

    def test_setup_state_restored(self):
        from ukrgen.models.load_store_operations import lsc_state
        problems = self.check(self.block(body=[lsc_state({"vlen": "tail(m)"})]))
        self.assertTrue(any("ends with other state" in p for p in problems), problems)
        self.assertEqual([], self.check(self.block(body=[lsc_state({"vlen": "tail(m)"}),
                                                         lsc_state({"vlen": "max"})])))


if __name__ == "__main__":
    unittest.main()
