"""
Building LSC IR from tiled STOs
"""

import unittest

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.layout import layout_stage
from ukrgen.flow.stages.solve import solve_stage
from ukrgen.flow.stages.dimension import dimension_stage
from ukrgen.flow.stages.sto import sto_stage
from ukrgen.flow.stages.model import model_stage
from ukrgen.flow.stages.stage import stage_error
from ukrgen.lsc_model.builder import program_builder, addressing_plan, model_error
from ukrgen.lsc_model.addressing import addr_pattern
from ukrgen.models.load_store_operations import (
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation)

TO_STAGES = [setup_stage, datatype_stage, layout_stage, solve_stage, dimension_stage, sto_stage]

FMA_M = "fma(A.VEC:direct, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"
BETA = "fmul(C.VEC:direct, beta.VEC:bc_load, C.VEC){i=m, n=1}"
ALPHA = "fma(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"


CASE_TOS = {
    # gemm's epilogue cases, all with vectors along m like the main loop
    "alphamul-tileop": ["fmul(AB.VEC, alpha.VEC:bc_load, C.VEC){i=m, n=1}"],
    "add-tileop": ["fadd(AB.VEC, C.VEC:direct, C.VEC){i=m, n=1}"],
    "alphaadd-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC:direct){i=m, n=1}"],
    "betaadd-tileop": ["fma(C.VEC:direct, beta.VEC:bc_load, AB.VEC){i=m, n=1}"],
    "store_ab-tileop": ["AB.VEC:direct"],
}


def run(stages=TO_STAGES, **extra):
    params = {"isa": "sve", "ukr": "gemm",
              "A-data-type": "FP64", "B-data-type": "FP64", "AB-data-type": "FP64",
              "C-data-type": "FP64", "A-layout": ["m:c", "k:p"], "B-layout": ["n:c", "k:p"],
              "C-layout": ["m:c", "n:s"], "mm-tileop": [FMA_M], "betascale-tileop": [BETA],
              "alphascale-tileop": [ALPHA], "store-tileop": ["C.VEC:direct"],
              "m": "2", "n": "2", "k": "1",
              "A-data-regs": "2", "B-data-regs": "2", "C-data-regs": "4", **CASE_TOS}
    params.update(extra)
    def prolog(s):
        for p in s.get_parameter_names():
            if p in params:
                s.set_param(p, params[p])
    ctx = ukr_context()
    return ctx, stage_engine(stages, ctx, prolog=prolog).run()


def addr_comp(op):
    return op.indices[0].component


def addr_reg(op):
    return op.indices[0].indices[0]


def data(op):
    return (op.indices[1].component, op.indices[1].indices[0])


def read_regs(op):
    return {(op.indices[i].component, op.indices[i].indices[0]) for i in op.reads}


def loads(ops, comp=None):
    return [op for op in ops if isinstance(op, lsc_load)
            and (comp is None or comp == addr_comp(op))]


class test_builder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx, _ = run()

    def build(self, **kw):
        kw.setdefault("addressing", {"C": addressing_plan(2, addr_pattern.parse("phase"))})
        return program_builder(self.ctx, **kw).build()

    def test_preload(self):
        prog = self.build()
        mm = prog.blocks[0]
        # the prologue zeroes the accumulators and loads the first iteration
        self.assertEqual(4, sum(isinstance(op, lsc_zero) for op in mm.prologue))
        self.assertEqual(4, len(loads(mm.prologue)))
        # the body loads the next iteration into each register right after
        # this iteration last reads it
        for pos, op in enumerate(mm.body):
            if isinstance(op, lsc_load):
                later = mm.body[pos + 1:]
                self.assertFalse(any(isinstance(c, lsc_transformation) and data(op) in read_regs(c)
                                     for c in later), f"{data(op)} read after its reload")
                # the next iteration: one step further along k
                self.assertEqual("1", str(prog.offsets[op.offset].along("k")))
        # the last iteration loads nothing
        self.assertEqual([], loads(mm.epilogue))
        self.assertEqual(4, len(mm.epilogue))

    def test_no_preload(self):
        mm = self.build(preload=False).blocks[0]
        self.assertEqual(4, len(loads(mm.body)))
        self.assertEqual([], mm.epilogue)

    def test_tail(self):
        # with an unroll of 1 the loop already steps by one operation
        self.assertEqual([], self.build().blocks[0].tail)
        ctx, _ = run(k="2")
        mm = program_builder(ctx).build().blocks[0]
        self.assertEqual(4, len(loads(mm.tail)))
        self.assertEqual(4, sum(isinstance(op, lsc_transformation) for op in mm.tail))
        # an FMA covers one element of k: no subtail, no constraint on k
        self.assertEqual([], mm.subtail)
        self.assertIsNone(mm.requires_multiple)

    def test_subtail(self):
        # No implementation offered yet covers more than one element of k, so
        # pretend the main one covers VL of them
        import copy
        from ukrgen.components.tile import dimension_properties as dimp, dimension_type as dimt
        ctx, _ = run(k="2")
        ctx.stos[0]["mm"].extents["k"] = dimp(dt=dimt.vla, size=1)
        mm = program_builder(ctx).build().blocks[0]
        self.assertEqual("VL", str(mm.requires_multiple))
        self.assertIn("k must be a multiple of VL", program_builder(ctx).build().render())
        # with a subtail implementation: one element of k at a time, no constraint
        sub = copy.copy(ctx.stos[0]["mm"])
        sub.ops = sub.regenerate(counts={"k": 1})
        ctx.subtail_stos = [{"mm": sub}]
        ctx.subtail_parts = [{"mm": ctx.to_parts[0]["mm"]}]
        mm = program_builder(ctx).build().blocks[0]
        self.assertIsNone(mm.requires_multiple)
        self.assertEqual("1", str(mm.subtail_step))
        self.assertEqual(4, sum(isinstance(op, lsc_transformation) for op in mm.subtail))
        self.assertEqual(4, len(loads(mm.subtail)))

    def test_c_phases(self):
        prog = self.build()
        epi = prog.cases[-1].blocks[0].body
        self.assertEqual({0}, {addr_reg(op) for op in loads(epi, "C")})
        self.assertEqual({1}, {addr_reg(op) for op in epi if isinstance(op, lsc_store)})
        # both start at C's base: the stores need no rewinding
        self.assertEqual(prog.addr_setup[("C", 0)], prog.addr_setup[("C", 1)])

    def test_scalars_loaded_once(self):
        epi = self.build().cases[-1].blocks[0].body
        self.assertEqual(1, len(loads(epi, "beta")))
        self.assertEqual(1, len(loads(epi, "alpha")))

    def test_strides(self):
        prog = self.build()
        self.assertEqual("2*VL", str(prog.strides["A"]["k"]))
        self.assertEqual("stride(C,n)", str(prog.strides["C"]["n"]))

    def test_fewer_data_registers(self):
        # one register for A: reloaded whenever another tile is needed
        mm = self.build(preload=False, data_regs={"A": 1}).blocks[0]
        self.assertEqual(2, len(loads(mm.body, "A")))
        self.assertEqual({0}, {data(op)[1] for op in loads(mm.body, "A")})
        with self.assertRaises(model_error):
            self.build(data_regs={"AB": 2})

    def test_unroll(self):
        # --k unrolls: an iteration covers --k operations' extents along k, and
        # streamed operands advance by as much
        ctx, _ = run(k="3")
        prog = program_builder(ctx).build()
        mm = prog.blocks[0]
        self.assertEqual(3, mm.unroll)
        self.assertEqual("3", str(mm.step))
        self.assertEqual("1", str(mm.tail_step))
        self.assertEqual("3", str(prog.offsets[mm.advance["A"]].along("k")))
        # preloads reach one whole iteration ahead
        ahead = [op for op in mm.body if isinstance(op, lsc_load)]
        self.assertEqual({"3", "4", "5"},
                         {str(prog.offsets[op.offset].along("k")) for op in ahead})

    def test_rotating_registers(self):
        prog = self.build(addressing={"A": addressing_plan(2, addr_pattern.parse("rotate"))})
        self.assertEqual([0, 1], [addr_reg(op) for op in loads(prog.blocks[0].prologue, "A")])


class test_builder_resolutions(unittest.TestCase):

    def test_chain_temporaries(self):
        ctx, res = run(**{"mm-tileop": [
            "fmul(A.VEC:direct, B.VEC:bc_load, T0.VEC){i=m, n=1, k*=1} ; "
            "fadd(AB.VEC, T0.VEC, AB.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed)
        mm = program_builder(ctx, preload=False).build().blocks[0]
        ops = [op for op in mm.body if isinstance(op, lsc_transformation)]
        self.assertEqual(["fmul", "fadd"] * 4, [op.op for op in ops])
        self.assertIn("T0", {i.component for op in ops for i in op.indices})

    def test_scalar_broadcast_via_register(self):
        # bc_scalar: load B's element into a scalar register, then broadcast it
        ctx, res = run(**{"mm-tileop": ["fma(A.VEC:direct, B.VEC:bc_scalar, AB.VEC){i=m, n=1, k*=1}"]})
        mm = program_builder(ctx, preload=False).build().blocks[0]
        moves = [op for op in mm.body if isinstance(op, lsc_move)]
        self.assertEqual(2, len(moves))
        self.assertEqual({"S"}, {op.indices[0].component for op in moves})

    def test_lanes_resolution(self):
        # NEON, row-major A: vectors along m loaded lane by lane
        ctx, res = run(isa="neon", **{"A-layout": ["m:s", "k:c"],
                                      "mm-tileop": ["fma(A.VEC:lanes, B.VEC:bc_load, AB.VEC){i=m, n=1, k*=1}"]})
        self.assertTrue(res.completed, res.output)
        mm = program_builder(ctx, preload=False).build().blocks[0]
        a = loads(mm.body, "A")
        self.assertEqual([0, 1, 0, 1], [op.properties.get("lane") for op in a])
        self.assertEqual({"lanes"}, {op.rsln for op in a})

    def test_lane_fma(self):
        # each element is loaded into the lane the FMA uses it from; lanefuse
        # makes the two lanes of a register one load, as B is contiguous
        from ukrgen.irmod.lsc import lanefuse
        from ukrgen.models.load_store_operations import ldst_modifier
        ctx, res = run(isa="neon", n="4", m="1", **{
            "mm-tileop": ["fma[bdreg:ILANE](A.VEC:direct, B.VEC:use_lane, AB.VEC){i=m, n=1, k*=1}"]})
        prog = program_builder(ctx, preload=False).build()
        mm = prog.blocks[0]
        self.assertEqual([0, 1, 0, 1], [op.properties.get("lane") for op in loads(mm.body, "B")])
        computes = [op for op in mm.body if isinstance(op, lsc_transformation)]
        self.assertEqual([0, 1, 0, 1],
                         [op.indices[op.hw_operands.index("bdreg")].indices[1] for op in computes])
        lanefuse(ctx).apply(prog)
        fused = loads(prog.blocks[0].body, "B")
        self.assertEqual(2, len(fused))
        self.assertFalse(any(ldst_modifier.lane in op.mods for op in fused))


class test_model_stage(unittest.TestCase):

    def test_print_ir(self):
        ctx, res = run(stages=TO_STAGES + [model_stage], **{"print-ir": True})
        self.assertFalse(res.completed)
        self.assertIn("block mm, loop over k by 1 per iteration (unrolled 1x)\n", res.output)
        self.assertIn("a1 of C starts at C[]", res.output)

    def test_programs(self):
        ctx, res = run(stages=TO_STAGES + [model_stage],
                       **{"A-addr-regs": "2", "A-addr-pattern": "blocked:2"})
        self.assertTrue(res.completed)
        self.assertEqual(1, len(ctx.programs))
        self.assertEqual({0}, {addr_reg(op) for op in loads(ctx.programs[0].blocks[0].prologue, "A")})

    def test_subtail_not_needed(self):
        # the main FMA already covers one element of k
        with self.assertRaisesRegex(stage_error, "--mm-subtail-tileop: not needed"):
            run(**{"mm-subtail-tileop": [FMA_M]})

    def test_invalid_pattern(self):
        with self.assertRaisesRegex(stage_error, "--A-addr-pattern"):
            run(stages=TO_STAGES + [model_stage], **{"A-addr-pattern": "spiral"})


if __name__ == "__main__":
    unittest.main()


class test_register_pressure(unittest.TestCase):

    GENERAL = {"A-layout": ["m:c", "k:s"], "B-layout": ["k:s", "n:c"], "C-layout": ["m:s", "n:s"],
               "mm-tileop": ["fma(A.VEC:bc_load, B.VEC:direct, AB.VEC){m=1, i=n, k*=1}"],
               "betascale-tileop": ["fmul(C.VEC:gather, beta.VEC:bc_load, C.VEC){m=1, i=n}"],
               "alphascale-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC){m=1, i=n}"],
               "store-tileop": ["C.VEC:scatter"], "n": "2", "k": "2",
               # the epilogue cases, also with vectors along n
               "alphamul-tileop": ["fmul(AB.VEC, alpha.VEC:bc_load, C.VEC){m=1, i=n}"],
               "add-tileop": ["fadd(AB.VEC, C.VEC:gather, C.VEC){m=1, i=n}"],
               "alphaadd-tileop": ["fma(AB.VEC, alpha.VEC:bc_load, C.VEC:gather){m=1, i=n}"],
               "betaadd-tileop": ["fma(C.VEC:gather, beta.VEC:bc_load, AB.VEC){m=1, i=n}"],
               "store_ab-tileop": ["AB.VEC:scatter"]}

    def test_fewer_registers_load_in_place(self):
        # A in 4 registers, two tiles each an iteration: each register's first
        # load is the next iteration's, an iteration ahead (the prologue the
        # first's), its second stays in place. B is all ahead.
        ctx, _ = run(m="4", **self.GENERAL)
        prog = program_builder(ctx, data_regs={"A": 4}).build()
        mm = prog.blocks[0]
        self.assertEqual(4, len(loads(mm.prologue, "A")))
        self.assertEqual(4, len(loads(mm.prologue, "B")))
        self.assertEqual(8, len(loads(mm.body, "A")))
        self.assertEqual(4, len(loads(mm.epilogue, "A")))
        # every register read loaded before - by the prologue or the body
        seen = {data(op) for op in mm.prologue if isinstance(op, lsc_load) and "A" == addr_comp(op)}
        for op in mm.body:
            if isinstance(op, lsc_load) and "A" == addr_comp(op):
                seen.add(data(op))
            if isinstance(op, lsc_transformation):
                for r in read_regs(op):
                    if "A" == r[0]:
                        self.assertIn(r, seen)


class test_old_ir_compatibility(unittest.TestCase):

    def test_distance_scheduler(self):
        # the dependency scheduler takes the model's operations as they are,
        # including moves between scratch and data registers
        from ukrgen.schedulers.distance import distance_specification
        from ukrgen.schedulers.simple_dependency_scheduler import simple_dependency_scheduler
        ctx, _ = run(**{"mm-tileop": ["fma(A.VEC:direct, B.VEC:bc_scalar, AB.VEC){i=m, n=1, k*=1}"]})
        mm = program_builder(ctx).build().blocks[0]
        specs = [distance_specification.from_string(s)
                 for s in ("raw:data::ld:fma:3", "raw:data::mv:fma:2")]
        out = simple_dependency_scheduler(specs)(list(mm.body), loop=True)
        self.assertEqual(sorted(map(id, mm.body)), sorted(map(id, out)))
        # a broadcast's move into B0 comes after the last read of B0's old value
        moves = [i for i, op in enumerate(out) if isinstance(op, lsc_move)]
        self.assertTrue(moves)

    def test_epilogue_owns_its_operations(self):
        # schedulers rename registers in place: body and epilogue must not
        # share operations or register indices
        mm = program_builder(run()[0]).build().blocks[0]
        body = {id(op) for op in mm.body} | {id(i) for op in mm.body for i in op.indices}
        epi = {id(op) for op in mm.epilogue} | {id(i) for op in mm.epilogue for i in op.indices}
        self.assertFalse(body & epi)

    def test_data_registers_fitted(self):
        # not given: the model fits them to the register file
        ctx, res = run(stages=TO_STAGES + [model_stage], **{"C-data-regs": None})
        self.assertTrue(ctx.programs)


class test_register_rings(unittest.TestCase):

    def test_ring_follows_first_use(self):
        # A in 4 registers for 8 tiles (m=4, k=2): the tiles of one step of k
        # get one register each, instead of alternating between two
        ctx, _ = run(m="4", **test_register_pressure.GENERAL)
        mm = program_builder(ctx, data_regs={"A": 4}).build().blocks[0]
        # the first step's tiles in the prologue (an iteration ahead), the
        # second's in place - the last iteration (epilogue) shows them alone
        self.assertEqual([0, 1, 2, 3], [data(op)[1] for op in loads(mm.prologue, "A")])
        self.assertEqual([0, 1, 2, 3], [data(op)[1] for op in loads(mm.epilogue, "A")])
        self.assertEqual([0, 0, 1, 1, 2, 2, 3, 3], sorted(data(op)[1] for op in loads(mm.body, "A")))


class test_branches(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ctx, _ = run()
        # C's default as the model stage sets it: two registers, by phase
        cls.prog = program_builder(ctx, addressing={
            "C": addressing_plan(2, addr_pattern.parse("phase"))}).build()
        cls.cases = {c.label: c for c in cls.prog.cases}

    def ops(self, label):
        return [op for b in self.cases[label].blocks for op in b.body]

    def test_cases(self):
        self.assertEqual(["beta==0 and alpha==1", "beta==0", "beta==1 and alpha==1",
                          "beta==1", "alpha==1", "otherwise"], [c.label for c in self.prog.cases])
        self.assertEqual({"beta": 0, "alpha": 1}, self.cases["beta==0 and alpha==1"].when)
        # the loop is emitted once, before the branch
        self.assertEqual(["mm"], [b.name for b in self.prog.blocks])

    def test_beta_zero_never_reads_c(self):
        for label in ("beta==0 and alpha==1", "beta==0"):
            with self.subTest(case=label):
                self.assertEqual([], loads(self.ops(label), "C"))
                self.assertEqual(4, sum(isinstance(op, lsc_store) for op in self.ops(label)))

    def test_alpha_one_accumulates_into_ab(self):
        ops = self.ops("alpha==1")
        self.assertEqual(4, len(loads(ops, "C")))
        fmas = [op for op in ops if isinstance(op, lsc_transformation)]
        self.assertEqual({"AB"}, {op.indices[op.writes[0]].component for op in fmas})
        # AB's registers are stored, through C's addresses
        stores = [op for op in ops if isinstance(op, lsc_store)]
        self.assertEqual({("C", "AB")}, {(addr_comp(op), op.indices[1].component) for op in stores})

    def test_store_ab_alone(self):
        # beta 0, alpha 1: nothing but AB stored into C
        ops = self.ops("beta==0 and alpha==1")
        self.assertTrue(ops)
        self.assertTrue(all(isinstance(op, lsc_store) and "AB" == op.indices[1].component
                            for op in ops))

    def test_cases_start_alike(self):
        # each case loads its scalars itself: no case relies on another's loads
        for label in ("beta==0", "beta==1", "otherwise"):
            with self.subTest(case=label):
                self.assertEqual(1, len(loads(self.ops(label), "alpha")))
        # and C's loads and stores take the same address registers in every case
        self.assertEqual({0}, {addr_reg(op) for op in loads(self.ops("beta==1"), "C")})
        self.assertEqual({1}, {addr_reg(op) for op in self.ops("beta==1")
                               if isinstance(op, lsc_store)})

    def test_render(self):
        text = self.prog.render()
        self.assertIn("case beta==0 and alpha==1:", text)
        self.assertIn("case otherwise:", text)


class test_register_reuse(unittest.TestCase):
    """
    With fewer data registers than tiles: same data, same register; new data
    where it costs the fewest reloads
    """

    @staticmethod
    def optimal(seq, regs):
        held, loads = set(), 0
        for i, t in enumerate(seq):
            if t in held:
                continue
            loads += 1
            if len(held) == regs:
                rest = seq[i + 1:]
                held.remove(max(held, key=lambda x: rest.index(x) if x in rest else len(seq)))
            held.add(t)
        return loads

    def test_fewest_reloads(self):
        for order, regs in (("knm", 3), ("kmn", 2), ("mkn", 5), ("nmk", 4)):
            with self.subTest(order=order, regs=regs):
                ctx, _ = run(m="4", n="3", k="2", order=order)
                seq = {c: [op.coord(c) for op in ctx.stos[0]["mm"].ops] for c in ("A", "B")}
                regs_a, regs_b = min(regs, 8), min(regs, 6)
                body = program_builder(ctx, data_regs={"A": regs_a, "B": regs_b},
                                       preload=False).build().blocks[0].body
                self.assertEqual(self.optimal(seq["A"], regs_a), len(loads(body, "A")))
                self.assertEqual(self.optimal(seq["B"], regs_b), len(loads(body, "B")))

    def test_held_tile_keeps_its_register(self):
        ctx, _ = run(m="4", n="3", k="1", order="knm")
        body = program_builder(ctx, data_regs={"A": 3}, preload=False).build().blocks[0].body
        held, i = {}, 0
        seq = [op.coord("A") for op in ctx.stos[0]["mm"].ops]
        for op in body:
            if isinstance(op, lsc_load) and "A" == addr_comp(op):
                held[data(op)] = seq[i]
            elif isinstance(op, lsc_transformation):
                (reg,) = [r for r in read_regs(op) if "A" == r[0]]
                self.assertEqual(seq[i], held[reg])
                i += 1


class test_resolve_order(unittest.TestCase):

    def test_order_of_loads(self):
        ctx, _ = run()
        for order, first in ((["A", "B"], "A"), (["B", "A"], "B")):
            with self.subTest(order=order):
                body = program_builder(ctx, preload=False, resolve_order=order).build().blocks[0].body
                self.assertEqual(first, addr_comp(loads(body)[0]))

    def test_stage_parameter(self):
        ctx, res = run(stages=TO_STAGES + [model_stage], **{"resolve-order": ["B", "A"]})
        self.assertTrue(res.completed)
        with self.assertRaisesRegex(stage_error, "--resolve-order"):
            run(stages=TO_STAGES + [model_stage], **{"resolve-order": ["B", "X"]})
