"""
Tests for the stage engine's early exit
"""

import unittest

from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.stage import stage, early_exit
from ukrgen.flow.ukr_context import ukr_context


class _record(stage):
    ran = []
    def progress(self):
        _record.ran.append(type(self).__name__)
        return []

class _first(_record): pass
class _after(_record): pass

class _spawned(_record): pass
class _spawner(_record):
    def progress(self):
        super().progress()
        return [_spawned]

class _tool(_record):
    def progress(self):
        super().progress()
        raise early_exit("listing", code=3)


class test_stage_engine(unittest.TestCase):

    def setUp(self):
        _record.ran = []

    def test_completes(self):
        res = stage_engine([_first, _spawner, _after], ukr_context()).run()
        self.assertTrue(res.completed)
        # spawned stages run before the next listed stage
        self.assertEqual(["_first", "_spawner", "_spawned", "_after"], _record.ran)

    def test_early_exit_stops_the_run(self):
        res = stage_engine([_first, _tool, _after], ukr_context()).run()
        self.assertFalse(res.completed)
        self.assertEqual("_tool", res.stage)
        self.assertEqual("listing", res.output)
        self.assertEqual(3, res.code)
        self.assertEqual(["_first", "_tool"], _record.ran)


if __name__ == "__main__":
    unittest.main()
