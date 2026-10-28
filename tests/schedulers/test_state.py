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


if __name__ == "__main__":
    unittest.main()
