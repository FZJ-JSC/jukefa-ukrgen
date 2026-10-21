"""
Scheduling the specialized LSC IR
"""

import logging

from ...models.load_store_operations import lsc_loop
from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...models.lsc.reg import lsc_reg_type
from ...schedulers.distance import distance_specification
from ...schedulers.list_scheduler import list_scheduler, register_budget, _key

SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")


def _read_before_written(blocks) -> set:
    """
    Data registers the blocks read before writing them: alive into them
    """
    seen, live = set(), set()
    for block in blocks:
        for section in SECTIONS:
            for op in getattr(block, section):
                for p in op.reads:
                    k = _key(op, p)
                    if lsc_reg_type.data == k[0] and k not in seen:
                        live.add(k)
                for p in op.writes:
                    seen.add(_key(op, p))
    return live


class schedule_stage(stage):
    """
    Schedules every section of every part's program under dependency distances
    (--distances, dep:regt:rtag:op1:op2:dist), loop bodies as loops. It never
    fails: distances it cannot reach are reported as warnings.

    --mru schedules straight-line blocks within the registers there are, which
    lets values reuse registers as others die - C taking AB's registers in the
    epilogue - while loading ahead as far as free registers allow.
    --mru-inflight limits how many values are loaded ahead at once (0: just in
    time); --mru-reserve keeps registers out of the budget.

    --print-schedule prints the scheduled IR and what each distance reached.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.log = logging.getLogger("SCHED")
        self.params["distances"] = stage_param(
                value=[], default=[], multi=True, required=False,
                description="Dependency distances, dep:regt:rtag:op1:op2:dist")
        self.params["mru"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Schedule straight-line blocks within the registers there are - "
                            "the default; kept for older command lines")
        self.params["sched-cycle-slots"] = stage_param(
                value=None, required=False,
                description="An issue model: what a core issues a cycle - \"[N:]slot,...\", "
                            "each slot a class or classes joined by | (one of them a cycle), "
                            "N the most a cycle; classes vl vs sl ss vf vi vp t f i addr br. "
                            "\"2:vl|vs|vf,sl,i\": a vector load, store or FP operation, a "
                            "scalar load and an integer one, two a cycle. Instructions placed "
                            "cycle by cycle, the distances in cycles")
        self.params["sched-buckets"] = stage_param(
                value=None, required=False,
                description="With an issue model: per class a bucket - \"vf:5,vl:2\" - a cycle "
                            "issuing one of the class fills it by one, a cycle without drains it; "
                            "the class preferred while it isn't full, waiting while it is (a "
                            "vector unit's queue kept fed, not overfed)")
        self.params["mru-window"] = stage_param(
                value=None, required=False,
                description="With MRU: how far ahead of the first instruction not yet placed one "
                            "may move, in the order the cluster irmod pulled together "
                            "(default 12)")
        self.params["no-mru"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Don't schedule straight-line blocks within the registers there "
                            "are: a gemm whose accumulators fill the register file then can't "
                            "stream C through its epilogue")
        self.params["mru-inflight"] = stage_param(
                value=None, required=False,
                description="With --mru: values loaded ahead of their use at most at once")
        self.params["mru-reserve"] = stage_param(
                value="0", default="0", required=False,
                description="With --mru: registers kept out of the budget")
        self.params["print-schedule"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the scheduled IR and the distances reached, and exit")

    def progress(self):
        try:
            specs = [distance_specification.from_string(s)
                     for s in self.params["distances"].value or []]
        except (ValueError, KeyError) as err:
            raise stage_error(f"--distances: {err}") from err
        # on unless turned off: the epilogue's C streams through the registers
        # the accumulators free only when scheduled so
        mru = not bool(self.params["no-mru"].value)
        if not specs and not mru:
            self.context.params.update(self.params)
            return []
        inflight = self.params["mru-inflight"].value
        reserve = int(self.params["mru-reserve"].value)
        gen = self.context.gen
        slots = self.params["sched-cycle-slots"].value
        if slots:
            from ...schedulers.issue import issue_model
            try:
                model = issue_model(slots)
            except ValueError as err:
                raise stage_error(str(err)) from err
        else:
            model = None
        buckets = {}
        for item in filter(None, (self.params["sched-buckets"].value or "").replace(" ", "").split(",")):
            cls, _, size = item.partition(":")
            buckets[cls] = int(size or 1)
        scheduler = list_scheduler(specs, model, buckets)
        lines = []

        for program in self.context.programs:
            paths = [(None, program.blocks)] + [(c, program.blocks + c.blocks)
                                                for c in program.cases]
            done = set()
            for case, blocks in paths:
                for pos, block in enumerate(blocks):
                    if id(block) in done:
                        continue
                    done.add(id(block))
                    budget = None
                    if mru and block.loop_index is None:
                        later = blocks[pos + 1:] + ([] if case is not None else
                                                    [b for c in program.cases for b in c.blocks])
                        budget = register_budget(
                            registers={"vreg": gen.max_vregs() - reserve,
                                       "freg": gen.max_fregs() - reserve},
                            inflight=None if inflight is None else int(inflight),
                            live_out=_read_before_written(later))
                    for section in SECTIONS:
                        ops = getattr(block, section)
                        loop = block.loop_index is not None and "body" == section
                        # MRU: chains pulled together before addresses were
                        # fixed (the cluster irmod), spread within a window
                        window = None
                        if budget is not None:
                            window = int(self.params["mru-window"].value or 12)
                        order, report = scheduler(ops, loop=loop, budget=budget, window=window,
                                                  groups=program.groups)
                        setattr(block, section, order)
                        # a loop's own block, as a loop body: a fused loop's
                        # tiles' chains, an unrolled one's copies, interleaved
                        for op in order:
                            if isinstance(op, lsc_loop) and op.block:
                                inner, _ = scheduler(list(op.block), loop=True,
                                                     groups=program.groups)
                                op.block = inner
                                op.refresh()
                        where = f"{(case.label + ': ') if case else ''}{block.name} {section}"
                        # what fell short is expected where registers are few
                        # (straight-line code): --debug or --print-schedule
                        for warning in report.warnings():
                            self.log.debug(f"{where}: {warning}")
                            lines.append(f"// {where}: {warning}")
                        if getattr(report, "cycles", None):
                            lines.append(f"// {where}: {report.cycles} cycles as the issue model "
                                         f"issues them")
                        if ops and specs:
                            lines.append(f"// {where}: " + ", ".join(
                                f"{s} reached {a}" for s, a in zip(report.specs, report.achieved)
                                if a != float("inf")))

        if self.params["print-schedule"].value:
            raise early_exit("\n".join(lines) + "\n\n" +
                             "\n\n".join(p.render() for p in self.context.programs))
        self.context.params.update(self.params)
        return []
