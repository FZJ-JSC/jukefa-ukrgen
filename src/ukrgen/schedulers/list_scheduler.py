"""
List scheduling of LSC IR sections under dependency distances, optionally under
a register budget.

The order is built from scratch, slot by slot, so an instruction can end up
later than it started as well as earlier. It never fails: when no candidate
meets its distances, the one falling shortest is taken, and the report says
which distances were reached. With a register budget the same pass also does
what the MRU did: it keeps the values alive at once within the registers there
are, loading ahead while registers are free and holding back while they are
scarce - the budget loosening by itself as values die.

Distances come in the existing notation (dep:regt:rtag:op1:op2:dist); the
dependencies are computed here, on registers identified by type, component and
index, a lane counting as its whole register.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from asmgen.asmblocks.op import register_type as rgt

from ..models.lsc.reg import lsc_reg_type
from ..models.load_store_operations import lsc_transformation
from .dependency import dependency_type as dept
from .distance import distance_specification

TAGS = {rgt.VEC: "vreg", rgt.FP: "freg", rgt.GP: "greg", rgt.TILE: "treg"}
INF = float("inf")


def _key(op, pos, groups=None) -> tuple:
    """
    A register: its kind, component, number and type - a tile and a vector of
    the same component and number are different registers. A grouped
    register (a widening accumulator's pair) is its whole group: what touches
    a member touches the group
    """
    idx = op.indices[pos]
    rtypes = getattr(op, "rtypes", None) or []
    number = idx.indices[0]
    group = (groups or {}).get(idx.component)
    if group is not None and isinstance(number, int):
        number -= number % group[0]
    return (op.reg_types[pos], idx.component, number,
            rtypes[pos] if pos < len(rtypes) else None)


def _tag(op, pos) -> str | None:
    if lsc_reg_type.address == op.reg_types[pos]:
        return "greg"
    rtypes = getattr(op, "rtypes", None) or []
    return TAGS.get(rtypes[pos]) if pos < len(rtypes) else None


@dataclass
class edge:
    """
    dst depends on src through a register; carried: src is in the previous loop
    iteration
    """
    src : int
    dst : int
    dep : dept
    key : tuple
    tag : str | None
    carried : bool = False
    distance : int = 1
    spec : int | None = None


def dependencies(ops: list, loop: bool, groups: dict | None = None) -> list[edge]:
    """
    Read-after-write, write-after-read and write-after-write dependencies; for
    a loop body also those from one iteration into the next
    """
    n = len(ops)
    seq = list(enumerate(ops)) + (list(enumerate(ops)) if loop else [])
    last_write: dict[tuple, tuple[int, int]] = {}
    readers: dict[tuple, list[tuple[int, int]]] = {}
    edges: list[edge] = []

    def add(src, sstep, dst, dstep, dep, key, tag):
        if sstep >= n:                 # both in the second iteration: seen already
            return
        carried = dstep >= n
        if carried or src != dst:
            edges.append(edge(src, dst, dep, key, tag, carried))

    for step, (i, op) in enumerate(seq):
        reads = {_key(op, p, groups): _tag(op, p) for p in op.reads}
        writes = {_key(op, p, groups): _tag(op, p) for p in op.writes}
        for key, tag in reads.items():
            if key in last_write:
                add(*last_write[key], i, step, dept.RAW, key, tag)
        for key, tag in writes.items():
            for r, rstep in readers.get(key, []):
                add(r, rstep, i, step, dept.WAR, key, tag)
            if key in last_write:
                add(*last_write[key], i, step, dept.WAW, key, tag)
        for key in reads:
            readers.setdefault(key, []).append((i, step))
        for key in writes:
            last_write[key] = (i, step)
            readers[key] = []
    return edges


def _applies(spec: distance_specification, e: edge, ops: list) -> bool:
    a, b = ops[e.src], ops[e.dst]
    if spec.dep_type is not None and spec.dep_type != e.dep:
        return False
    if spec.reg_type is not None and spec.reg_type != e.key[0]:
        return False
    if spec.asm_reg_tag is not None and spec.asm_reg_tag != e.tag:
        return False
    if spec.op1_type is not None and not isinstance(a, spec.op1_type):
        return False
    if spec.op2_type is not None and not isinstance(b, spec.op2_type):
        return False
    if spec.op1_type is lsc_transformation and spec.tr1_name not in (None, a.op):
        return False
    if spec.op2_type is lsc_transformation and spec.tr2_name not in (None, b.op):
        return False
    return True


@dataclass
class schedule_report:
    """
    Per distance specification: the distance requested, the smallest reached,
    and how many dependencies fall short; and how far the register budget was
    exceeded, if it had to be
    """
    specs : list[str]
    requested : list[int]
    achieved : list[float]
    short : list[int]
    over_budget : int = 0

    def warnings(self) -> list[str]:
        out = [f"{s}: requested {r}, reached {a} ({n} dependencies short)"
               for s, r, a, n in zip(self.specs, self.requested, self.achieved, self.short) if n]
        if self.over_budget:
            out.append(f"register budget exceeded by up to {self.over_budget}")
        return out


@dataclass
class register_budget:
    """
    Registers available per register tag, data registers only, and how many
    values may be loaded ahead of their first use at once (None: as many as fit)
    """
    registers : dict[str, int]
    inflight : int | None = None
    live_out : set = field(default_factory=set)


def cluster(ops: list, groups: dict | None = None) -> list:
    """
    Dependent instructions pulled together - the MRU's first half: each sink
    (an instruction nothing after it depends on), in order, right after what
    it depends on and isn't placed yet - a C tile loaded, scaled, combined
    with its accumulator and stored before the next tile is touched. Its
    values live briefly, their registers free again for the next tile - the
    emitter renames virtual registers onto the physical ones free - and the
    list scheduler pulls the chains apart again as far as registers allow
    """
    edges = [e for e in dependencies(ops, False, groups) if not e.carried]
    preds: dict[int, list[int]] = {j: [] for j in range(len(ops))}
    succ = set()
    for e in edges:
        preds[e.dst].append(e.src)
        succ.add(e.src)
    placed, order = set(), []
    def visit(j):
        if j in placed:
            return
        for p in sorted(preds[j]):
            visit(p)
        placed.add(j)
        order.append(j)
    for j in range(len(ops)):
        if j not in succ:
            visit(j)
    for j in range(len(ops)):
        visit(j)
    return [ops[i] for i in order]


class list_scheduler:
    """
    :param specs: distance specifications
    """

    def __init__(self, specs: list[distance_specification], model=None, buckets=None):
        self.specs = specs
        #: per class a bucket's size (--sched-buckets "vf:5"): a cycle issuing
        #: one of the class fills it by one, a cycle without drains it by one;
        #: the class is preferred while it isn't full and waits while it is
        self.buckets = dict(buckets or {})
        #: an issue model (issue.issue_model): placed cycle by cycle, the
        #: distances in cycles; None: one instruction after another
        self.model = model
        self.cycles = None

    def edges(self, ops: list, loop: bool, groups: dict | None = None) -> list[edge]:
        edges = dependencies(ops, loop, groups)
        for e in edges:
            for i, spec in enumerate(self.specs):
                if _applies(spec, e, ops) and spec.distance > e.distance:
                    e.distance, e.spec = spec.distance, i
        return edges

    def __call__(self, ops: list, loop: bool = False,
                 budget: register_budget | None = None,
                 window: int | None = None,
                 groups: dict | None = None) -> tuple[list, schedule_report]:
        if len(ops) < 2:
            return list(ops), self.report(ops, list(range(len(ops))), self.edges(ops, loop, groups), 0)
        self.cycles = None
        edges = self.edges(ops, loop, groups)
        intra = [e for e in edges if not e.carried]
        # priority: the longest chain of required distances to the section's end
        prio = [0.0] * len(ops)
        for i in range(len(ops) - 1, -1, -1):
            prio[i] = max([e.distance + prio[e.dst] for e in intra if e.src == i] or [0])

        best, best_score, best_over, best_cycles = None, None, 0, None
        bonus = [0.0] * len(ops)
        rounds = (6 if self.model is not None else 4) if loop else 1
        for _ in range(rounds):
            order, over = self.place(ops, intra, [p + b for p, b in zip(prio, bonus)], budget,
                                     window)
            if self.model is not None:
                # in cycles: a carried dependency reaches across the loop's
                # cycles - its producer's iteration's rest and the
                # consumer's cycles into the next
                cyc, length = dict(self.cycle_of), self.cycles
                score = self.score_cycles(edges, cyc, length)
            else:
                pos = {op: t for t, op in enumerate(order)}
                score = self.score(edges, pos, len(ops))
            if best is None or score < best_score:
                best, best_score, best_over = order, score, over
                best_cycles = self.cycles
            if not loop:
                break
            for e in edges:
                if not e.carried:
                    continue
                if self.model is not None:
                    short = e.distance - ((length - cyc[e.src]) + cyc[e.dst])
                    if short > 0:
                        # the producer earlier, the consumer later
                        bonus[e.src] += short
                        bonus[e.dst] -= short
                else:
                    short = e.distance - ((len(ops) - pos[e.src]) + pos[e.dst])
                    if short > 0:
                        bonus[e.dst] += short
                        bonus[e.src] -= short
        self.cycles = best_cycles
        return [ops[i] for i in best], self.report(ops, best, edges, best_over)

    @staticmethod
    def score_cycles(edges, cyc, length) -> tuple:
        """
        How far dependencies fall short of their distances, in cycles - the
        worst, the total - and the cycles the block takes
        """
        shorts = []
        for e in edges:
            reached = (length - cyc[e.src]) + cyc[e.dst] if e.carried else cyc[e.dst] - cyc[e.src]
            shorts.append(max(0, e.distance - reached))
        return (max(shorts or [0]), sum(shorts), length)

    @staticmethod
    def score(edges, pos, n) -> tuple:
        shorts = []
        for e in edges:
            reached = (n - pos[e.src]) + pos[e.dst] if e.carried else pos[e.dst] - pos[e.src]
            shorts.append(max(0, e.distance - reached))
        return (max(shorts or [0]), sum(shorts))

    def place(self, ops, intra, prio, budget, window=None) -> tuple[list[int], int]:
        if self.model is not None:
            return self.place_cycles(ops, intra, prio, budget, window)
        return self.place_slots(ops, intra, prio, budget, window)

    def place_cycles(self, ops, intra, prio, budget, window=None) -> tuple[list[int], int]:
        """
        Fill cycles one at a time, as the issue model lets a core issue them:
        an instruction ready in the cycle its predecessors' cycles and the
        distances allow (a RAW one at least the next), each cycle's slots
        taken by the most critical ready - within the register budget
        """
        from .issue import classify
        n = len(ops)
        preds: dict[int, list[edge]] = {j: [] for j in range(n)}
        consumers: dict[int, list[int]] = {j: [] for j in range(n)}
        for e in intra:
            preds[e.dst].append(e)
            if dept.RAW == e.dep:
                consumers[e.src].append(e.dst)
        classes = [classify(op) for op in ops]
        cycle_of: dict[int, int] = {}
        order: list[int] = []
        regs = _register_state(ops, budget) if budget else None
        over = 0
        cycle = 0
        levels = {c: 0 for c in self.buckets}
        def earliest(j):
            return max([cycle_of[e.src] + max(e.distance, 1 if dept.RAW == e.dep else 0)
                        for e in preds[j]] or [0])
        while len(order) < n:
            used: set[int] = set()
            issued: set[str] = set()
            while len(order) < n:
                ready = [j for j in range(n) if j not in cycle_of
                         and all(e.src in cycle_of for e in preds[j])]
                if window is not None:
                    low = next(j for j in range(n) if j not in cycle_of)
                    ready = [j for j in ready if j < low + window] or ready
                now = [j for j in ready if earliest(j) <= cycle]
                candidates = now
                if regs is not None and now:
                    def admissible(j):
                        if not regs.fits(j):
                            return False
                        if regs.relief(j) >= 0 or regs.free_after(j) >= 1:
                            return True
                        return any(regs.relief(k) > 0 for k in consumers[j])
                    candidates = [j for j in now if admissible(j)]
                    if not candidates and not used and len(now) == len(ready):
                        # nothing fits: relieve the pressure most, and report it
                        j = max(now, key=lambda j: (regs.relief(j), prio[j], -j))
                        over = max(over, regs.excess(j))
                        candidates = [j]
                pick = None
                # buckets: a class not full first, a full one only where no
                # other instruction issues this cycle
                full = {c for c, size in self.buckets.items() if levels[c] >= size}
                filling = {c for c in self.buckets if c not in full}
                order_key = lambda j: (classes[j] not in filling, -prio[j], j)
                ranked = sorted(candidates, key=order_key)
                if full and any(classes[j] not in full for j in ranked):
                    ranked = [j for j in ranked if classes[j] not in full] + \
                             ([j for j in ranked if classes[j] in full] if not used and not issued
                              and not any(self.model.take(classes[k], used, issued) is not None
                                          for k in ranked if classes[k] not in full) else [])
                for j in ranked:
                    slot = self.model.take(classes[j], used, issued)
                    if slot is not None:
                        pick = j
                        used.add(slot)
                        issued.add(classes[j])
                        break
                if pick is None:
                    break
                cycle_of[pick] = cycle
                order.append(pick)
                if regs is not None:
                    regs.place(pick)
            for c, size in self.buckets.items():
                levels[c] = min(size, levels[c] + 1) if c in issued else max(0, levels[c] - 1)
            if not used:
                # nothing issues: on to the cycle the first ready one may
                pending = [earliest(j) for j in range(n) if j not in cycle_of
                           and all(e.src in cycle_of for e in preds[j])]
                cycle = max(cycle + 1, min(pending)) if pending else cycle + 1
            else:
                cycle += 1
        self.cycles = cycle
        self.cycle_of = cycle_of
        return order, over

    def place_slots(self, ops, intra, prio, budget, window=None) -> tuple[list[int], int]:
        """
        Fill slots one at a time: of the instructions whose predecessors are all
        placed, take the most critical one meeting its distances, else the one
        falling shortest - within the register budget where there is one
        """
        n = len(ops)
        preds: dict[int, list[edge]] = {j: [] for j in range(n)}
        consumers: dict[int, list[int]] = {j: [] for j in range(n)}
        for e in intra:
            preds[e.dst].append(e)
            if dept.RAW == e.dep:
                consumers[e.src].append(e.dst)
        placed: dict[int, int] = {}
        order: list[int] = []

        regs = _register_state(ops, budget) if budget else None
        over = 0
        for t in range(n):
            ready = [j for j in range(n) if j not in placed
                     and all(e.src in placed for e in preds[j])]
            if window is not None:
                # at most a window ahead of the first not placed: the chains
                # pulled together stay near each other
                low = next(j for j in range(n) if j not in placed)
                ready = [j for j in ready if j < low + window] or ready

            def slack(j):
                return min([t - placed[e.src] - e.distance for e in preds[j]] or [INF])

            candidates = ready
            pressed = False
            if regs is not None:
                # A value taking a register must not take the last free one
                # unless its consumers free registers: otherwise partly done
                # chains can fill every register, leaving none for the value
                # (alpha) that lets them complete.
                def admissible(j):
                    if not regs.fits(j):
                        return False
                    if regs.relief(j) >= 0 or regs.free_after(j) >= 1:
                        return True
                    return any(regs.relief(k) > 0 for k in consumers[j])
                fitting = [j for j in ready if admissible(j)]
                pressed = regs.free() <= 1
                if fitting:
                    candidates = fitting
                else:
                    # nothing fits: relieve the pressure most, and report it
                    j = max(ready, key=lambda j: (regs.relief(j), prio[j], -j))
                    over = max(over, regs.excess(j))
                    candidates = [j]
            met = [j for j in candidates if slack(j) >= 0]
            if pressed:
                # few registers left: free some first
                pick = max(met or candidates,
                           key=lambda j: (regs.relief(j), slack(j) >= 0, prio[j], -j))
            else:
                pick = max(met, key=lambda j: (prio[j], -j)) if met else \
                    max(candidates, key=lambda j: (slack(j), prio[j], -j))
            placed[pick] = t
            order.append(pick)
            if regs is not None:
                regs.place(pick)
        return order, over

    def report(self, ops, order, edges, over) -> schedule_report:
        pos = {op: t for t, op in enumerate(order)}
        n = len(ops)
        achieved = [INF] * len(self.specs)
        short = [0] * len(self.specs)
        for e in edges:
            if e.spec is None:
                continue
            reached = (n - pos[e.src]) + pos[e.dst] if e.carried else pos[e.dst] - pos[e.src]
            achieved[e.spec] = min(achieved[e.spec], reached)
            if reached < e.distance:
                short[e.spec] += 1
        report = schedule_report(specs=[str(s) for s in self.specs],
                               requested=[s.distance for s in self.specs],
                               achieved=achieved, short=short, over_budget=over)
        report.cycles = self.cycles
        return report


class _register_state:
    """
    Data registers alive while placing: those read before written in the
    section, and those defined since, until their last read - unless needed
    after the section
    """

    def __init__(self, ops, budget: register_budget):
        self.ops = ops
        self.budget = budget
        self.uses: dict[tuple, int] = {}
        self.live: set[tuple] = set()
        self.tag: dict[tuple, str] = {}
        self.ahead: set[tuple] = set()
        written = set()
        for op in ops:
            for p in op.reads:
                k = _key(op, p)
                if lsc_reg_type.data != k[0]:
                    continue
                self.uses[k] = self.uses.get(k, 0) + 1
                self.tag[k] = _tag(op, p)
                if k not in written:
                    self.live.add(k)
            for p in op.writes:
                k = _key(op, p)
                if lsc_reg_type.data == k[0]:
                    written.add(k)
                    self.tag[k] = _tag(op, p)

    def _data(self, j, positions):
        op = self.ops[j]
        return {_key(op, p) for p in positions if lsc_reg_type.data == op.reg_types[p]}

    def change(self, j) -> tuple[set, set]:
        reads, writes = self._data(j, self.ops[j].reads), self._data(j, self.ops[j].writes)
        defs = {k for k in writes if k not in self.live}
        frees = {k for k in reads if self.uses.get(k, 0) == 1 and k not in writes
                 and k not in self.budget.live_out}
        return defs, frees

    def count(self, live, tag) -> int:
        return sum(1 for k in live if self.tag.get(k) == tag)

    def excess(self, j) -> int:
        defs, frees = self.change(j)
        after = (self.live | defs) - frees
        return max([self.count(after, t) - n for t, n in self.budget.registers.items()] + [0])

    def fits(self, j) -> bool:
        defs, frees = self.change(j)
        if self.excess(j) > 0:
            return False
        reads = self._data(j, self.ops[j].reads)
        ahead = (self.ahead - reads) | {k for k in defs if self.uses.get(k, 0) > 0}
        return self.budget.inflight is None or len(ahead) <= self.budget.inflight \
            or len(ahead) <= len(self.ahead)

    def free(self) -> int:
        return min(n - self.count(self.live, t) for t, n in self.budget.registers.items())

    def free_after(self, j) -> int:
        defs, frees = self.change(j)
        after = (self.live | defs) - frees
        return min(n - self.count(after, t) for t, n in self.budget.registers.items())

    def relief(self, j) -> int:
        defs, frees = self.change(j)
        return len(frees) - len(defs)

    def place(self, j):
        defs, frees = self.change(j)
        reads = self._data(j, self.ops[j].reads)
        for k in reads:
            self.uses[k] = self.uses.get(k, 0) - 1
        self.ahead = (self.ahead - reads) | {k for k in defs if self.uses.get(k, 0) > 0}
        self.live = (self.live | defs) - frees
