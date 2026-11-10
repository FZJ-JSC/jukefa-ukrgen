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
    problem = allocation.allocation_problem()
    for pos, one in enumerate(ctx.programs):
        # the machine's files and the values' data types, as the emitter has them
        res = allocation.resources.of(one, gen, ctx.component_dts)
        if pools is not None:
            res.pools.update(pools)
        part = allocation.analyse(one, res)
        problem.values.update(part.values)
        problem.demands += part.demands
        problem.deferred += part.deferred
    return problem, res, ctx


class test_analysis(unittest.TestCase):

    def test_values(self):
        problem, _, _ = problem_and_resources()
        self.assertTrue(problem.values)
        # a loop over slices' sections are places of their own
        self.assertTrue(any("<slices>" in d.where for d in problem.demands))
        for key, entry in problem.values.items():
            self.assertTrue(entry.ranges, key)
            self.assertIsNotNone(entry.tag, key)

    def test_demand(self):
        problem, _, _ = problem_and_resources()
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
        problem, _, _ = problem_and_resources(pools={"vreg": 2})
        short = [d for d in problem.demands if d.tag == "vreg" and not d.fits]
        self.assertTrue(short)
        self.assertIn("SHORT", problem.report())

    def test_deferred(self):
        # the renames a renamer can't make carry what they need; this kernel's
        # few (none: whole vectors moved out of whole tiles) say nothing
        problem, _, _ = problem_and_resources()
        for entry in problem.deferred:
            self.assertTrue(entry.why and entry.requires, entry)


class test_allocation(unittest.TestCase):

    def test_places_every_value(self):
        # vectors and the tiles' own file - its pool asmgen's tag by data type
        problem, res, ctx = problem_and_resources()
        self.assertIn("treg64", res.pools)
        result = allocation.allocate(problem, res)
        self.assertTrue(problem.values)
        self.assertEqual([], result.unfitted)
        for key in problem.values:
            self.assertIsNotNone(result.number(key), key)
        # no two values live at once share a register, within the file, aligned
        self.assertEqual([], allocation.validate(problem, result, res))

    def test_fixed_rings(self):
        # the model's rings: a component's slots a block of the file of their
        # own, the slot's number the block's base plus the slot - claimed
        # before any flexible value, and no two components sharing a register
        problem, res, ctx = problem_and_resources()
        result = allocation.allocate(problem, res)
        bases, held = {}, {}
        for key, entry in problem.values.items():
            if entry.fixed is None or entry.fixed.ring is None:
                continue
            tag, number = result.number(key)
            ring = entry.fixed.ring
            base = number - entry.fixed.slot
            self.assertEqual(base, bases.setdefault(ring, base), f"{ring} not one block")
            held.setdefault(ring, set()).add((tag, number))
        # the kernel's own rings - the analysis' source - and a slot marked from
        # each (nothing marked is the analysis' fixed allocations missing)
        declared = {comp for one in ctx.programs for comp in one.registers}
        self.assertTrue(declared, "the kernel declares no rings")
        self.assertEqual(declared, set(held),
                         f"rings {sorted(declared)} declared, {sorted(held)} marked: "
                         f"the analysis' fixed allocations")
        rings = list(held.values())
        for pos, one in enumerate(rings):
            for other in rings[pos + 1:]:
                self.assertEqual(set(), one & other, f"{sorted(one)} {sorted(other)}")
        # and the analysis says why each is where it is
        self.assertTrue(any("ring" in entry.why for entry in problem.deferred))

    def test_reports_what_it_cannot_place(self):
        # two registers for a section of more names: reported with what it
        # would need, never silently shared
        problem, res, _ = problem_and_resources(pools={"vreg": 2})
        result = allocation.allocate(problem, res)
        self.assertTrue(result.unfitted)
        self.assertTrue(any("vreg" in why for _, why in result.unfitted), result.report())

    def test_the_machinery_keeps_its_numbers(self):
        # the machinery's own numbers are no value's: RVV's mask is vector 0,
        # the tracker sharing the two, so nothing is placed there and validate
        # keeps it clear
        problem, res, _ = problem_and_resources()
        res.reserved = {"vreg": {0}}
        result = allocation.allocate(problem, res)
        self.assertEqual([], result.unfitted)
        for key in problem.values:
            placed = result.number(key)
            if placed is not None and "vreg" == placed[0]:
                self.assertNotEqual(0, placed[1], key)
        self.assertEqual([], allocation.validate(problem, result, res))
