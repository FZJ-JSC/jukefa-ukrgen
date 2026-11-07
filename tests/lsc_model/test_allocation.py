"""
The register allocation stage's analysis (docs/REGISTER_ALLOCATION.md: the
first of the two passes) and the allocation it feeds - the values, their
classes, what each file needs where, the renames a renamer can't make, and the
numbers the allocation gives them
"""

import unittest

import tests.specializers.test_sme_run as sme
from ukrgen.lsc_model import allocation


#: the loop over slices unrolled into explicit copies: enough values in one
#: section for a file's names to matter
UNROLL = {"pre-specialize-irmods": ["fuse_slices", "forward_slices", "hoist_slices",
                                    "unroll_loops", "hoist"],
          "unroll_loops-factor": "2", "unroll_loops-registers": "2"}


def problem_and_resources(pools=None):
    """An SME gemm's programs analysed, its files' sizes as the emitter has them"""
    ctx, _ = sme.run(**UNROLL)
    gen = ctx.gen
    sizes = {"vreg": gen.max_vregs(), "greg": gen.max_gregs()}
    if pools is not None:
        sizes = {**sizes, **pools}
    res = allocation.resources(pools=sizes)
    problem = allocation.allocation_problem()
    for one in ctx.programs:
        res.groups = one.groups
        part = allocation.analyse(one, res)
        problem.values.update(part.values)
        problem.demands += part.demands
        problem.deferred += part.deferred
    return problem, res


class test_analysis(unittest.TestCase):

    def test_values(self):
        problem, _ = problem_and_resources()
        self.assertTrue(problem.values)
        # a loop over slices' sections are places of their own
        self.assertTrue(any("<slices>" in d.where for d in problem.demands))
        for key, entry in problem.values.items():
            self.assertTrue(entry.ranges, key)
            self.assertIsNotNone(entry.tag, key)

    def test_demand(self):
        problem, _ = problem_and_resources()
        vregs = [d for d in problem.demands if d.tag == "vreg"]
        self.assertTrue(vregs)
        for d in vregs:
            # a file's names are at least what is live at once of it
            self.assertLessEqual(d.live, d.names, d)
        # what fits is reported fitting - the emitter builds this kernel
        self.assertEqual([], [d for d in vregs if not d.fits])

    def test_short(self):
        # a file too small for a section says so, with where - the emitter's
        # "no vector register left", answered before it is emitted
        problem, _ = problem_and_resources(pools={"vreg": 2})
        short = [d for d in problem.demands if d.tag == "vreg" and not d.fits]
        self.assertTrue(short)
        self.assertIn("SHORT", problem.report())

    def test_deferred(self):
        # the renames a renamer can't make carry what they need; this kernel's
        # few (none: whole vectors moved out of whole tiles) say nothing
        problem, _ = problem_and_resources()
        for entry in problem.deferred:
            self.assertTrue(entry.why and entry.requires, entry)


class test_allocation(unittest.TestCase):

    def test_places_the_vector_values(self):
        problem, res = problem_and_resources()
        result = allocation.allocate(problem, res)
        placed = [k for k in problem.values if problem.values[k].tag == "vreg"]
        self.assertTrue(placed)
        for key in placed:
            self.assertIsNotNone(result.number(key), key)
        # no two values live at once share a register, within the file, aligned
        self.assertEqual([], allocation.validate(problem, result, res))

    def test_reports_what_it_cannot_place(self):
        # two registers for a section of more names: reported with what it
        # would need, never silently shared
        problem, res = problem_and_resources(pools={"vreg": 2})
        result = allocation.allocate(problem, res)
        self.assertTrue(result.unfitted)
        self.assertTrue(any("vreg" in why for _, why in result.unfitted), result.report())
