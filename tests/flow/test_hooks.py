"""
Hooks around the flow's stages: parsing, the order they run in, a warning
for one whose stage never ran, and changes a later stage sees.
"""
import os
import tempfile
import unittest

from ukrgen.flow import hooks
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.stage import stage
from ukrgen.flow.ukr_context import ukr_context

SCRIPT = '''
def note(ctx, stage, tag="x"):
    ctx.log.append(f"{tag}:{type(stage).__name__}")

def double(ctx, stage):
    ctx.value *= 2
'''


class first_stage(stage):
    def progress(self):
        self.context.log.append("first")
        self.context.value = 3
        return [spawned_stage]


class spawned_stage(stage):
    def progress(self):
        self.context.log.append("spawned")
        return []


class last_stage(stage):
    def progress(self):
        self.context.log.append(f"last saw {self.context.value}")
        return []


class test_hooks(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.script = os.path.join(self.dir, "h.py")
        with open(self.script, "w") as f:
            f.write(SCRIPT)

    def ctx(self, *specs):
        ctx = ukr_context()
        ctx.log, ctx.value = [], 0
        ctx.hooks = [hooks.parse(s) for s in specs]
        return ctx

    def test_parse(self):
        h = hooks.parse(f"after schedule_stage {self.script} note tag=a b=c")
        self.assertEqual(("after", "schedule", "note", {"tag": "a", "b": "c"}),
                         (h.when, h.stage, h.function, h.args))
        self.assertEqual("hook", hooks.parse(f"before emit {self.script}").function)
        self.assertEqual({"tag": "1"}, hooks.parse(f"before emit {self.script} tag=1").args)
        for bad in (f"during emit {self.script}", "after emit", f"after emit {self.script} f x",
                    "after emit /no/such/script.py"):
            with self.assertRaises(ValueError, msg=bad):
                hooks.parse(bad)

    def test_order_and_spawned_stages(self):
        ctx = self.ctx(f"before first {self.script} note tag=b", f"after first {self.script} note tag=a",
                       f"after spawned {self.script} note tag=s", f"before last {self.script} note tag=L")
        self.assertTrue(stage_engine([first_stage, last_stage], ctx).run().completed)
        self.assertEqual(["b:first_stage", "first", "a:first_stage", "spawned", "s:spawned_stage",
                          "L:last_stage", "last saw 3"], ctx.log)

    def test_a_change_later_stages_see(self):
        ctx = self.ctx(f"after first {self.script} double")
        stage_engine([first_stage, last_stage], ctx).run()
        self.assertIn("last saw 6", ctx.log)

    def test_a_hook_never_run_is_reported(self):
        import contextlib
        import io
        ctx = self.ctx(f"after no_such {self.script} note")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            stage_engine([first_stage, last_stage], ctx).run()
        self.assertIn("never ran", err.getvalue())
        self.assertIn("first, spawned, last", err.getvalue())

    def test_a_missing_function(self):
        ctx = self.ctx(f"after first {self.script} nothing_here")
        with self.assertRaises(ValueError):
            stage_engine([first_stage, last_stage], ctx).run()


if __name__ == "__main__":
    unittest.main()
