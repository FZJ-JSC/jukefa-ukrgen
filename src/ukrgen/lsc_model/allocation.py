"""
The register allocation stage's analysis (docs/REGISTER_ALLOCATION.md: one
allocator, two passes - this is the first)

Everything the emitter works out while emitting is worked out here instead: a
value's file and class, what its instructions require of it, and its live
ranges over the IR - a loop one iteration with the back edge an edge, the
sections one sequence, so a prologue's write is the value its body reads, and
a value read across the back edge one range carried the whole loop. The
allocation that follows takes the problem and binds numbers; the emitter looks
them up.

The renames the MRU can't do are reported with what they require
(`allocation_problem.deferred`), so whether they have to stay here or the
renamer can be taught them is a question with an answer, not a guess.
"""

from dataclasses import dataclass, field

from asmgen.asmblocks.op import register_type as rgt

from . import classes, liveness
from ..models.load_store_operations import lsc_loop


@dataclass(frozen=True)
class live_range:
    """Where a value is live: the block, the section it starts in, the first
    and last operation it appears in - `carried` for a value live across a
    loop's back edge, one range over the whole iteration"""
    block: str
    section: str
    first: int
    last: int
    carried: bool = False


@dataclass(frozen=True)
class value:
    """A virtual register and what it needs"""
    key: tuple
    cls: classes.register_class | None
    ranges: tuple
    #: written in parts - a lane, a block, a tile's slice: one value, never
    #: split, and a renamer's target only where it rewrites all of it
    parts: bool = False
    #: the number it must take, where the user or the model fixed it
    fixed: tuple | None = None
    #: the component whose data type forms its instruction
    owner: str | None = None

    @property
    def tag(self) -> str | None:
        return None if self.cls is None else self.cls.tag


@dataclass
class demand:
    """What a file needs where: the values live at once and the names - a name
    holds a register the iteration long, so the names are what must fit"""
    tag: str
    where: str
    live: int
    names: int
    pool: int

    @property
    def fits(self) -> bool:
        return self.names <= self.pool


@dataclass
class deferred:
    """
    A rename the renamer (the MRU on virtual registers) can't make, and what it
    would need to - kept apart so the question "does this have to be the
    allocator's or can the renamer be taught it" has an answer
    """
    key: tuple
    why: str
    requires: str


@dataclass
class resources:
    """What the machine offers: the pools' sizes, the groups, the classes' input"""
    pools: dict = field(default_factory=dict)
    groups: dict = field(default_factory=dict)
    dts: dict = field(default_factory=dict)
    bounds: dict = field(default_factory=dict)
    tile_tag: object = None

    def class_of(self, key) -> classes.register_class | None:
        return classes.register_class_of(key, self.groups, self.dts, self.bounds,
                                         tile_tag=self.tile_tag)


@dataclass
class allocation_problem:
    """The analysis' answer: every virtual register, what each file needs
    where, and the renames that aren't the renamer's"""
    values: dict = field(default_factory=dict)
    demands: list = field(default_factory=list)
    deferred: list = field(default_factory=list)

    def short(self) -> list:
        """The demands that don't fit"""
        return [d for d in self.demands if not d.fits]

    def pressure(self, tag: str) -> int:
        """The most of a file live at once, any section"""
        return max((d.live for d in self.demands if d.tag == tag), default=0)

    def names(self, tag: str) -> int:
        """The most names of a file any section holds"""
        return max((d.names for d in self.demands if d.tag == tag), default=0)

    def report(self) -> str:
        lines = [f"{len(self.values)} virtual registers, {len(self.deferred)} renames the "
                 f"renamer can't make"]
        for d in self.demands:
            state = "ok" if d.fits else "SHORT"
            lines.append(f"  {d.tag:5s} {d.where:28s} live {d.live:3d} names {d.names:3d} "
                         f"of {d.pool:3d} {state}")
        for f in self.deferred:
            lines.append(f"  keep {f.key[0]}{f.key[1]}: {f.why} - needs {f.requires}")
        return "\n".join(lines)


def _positions(ops: list) -> list:
    """
    An operation's place in its section, its loops' operations flattened in
    behind it (a loop is one position for its block's liveness - its own
    sections are analysed as the iteration they are)
    """
    out, pos = [], 0
    for op in ops:
        out.append((pos, op))
        pos += 1
    return out


def _liveness(ops: list, live_out: set) -> tuple[list, set, set]:
    """
    Backward liveness over a straight sequence of operations, its end given:
    (what is live before each, what is live before the first, what is written
    before it is read - the values coming from outside)
    """
    before: list = [frozenset() for _ in ops]
    live = set(live_out)
    for pos in reversed(range(len(ops))):
        reads, writes = liveness.reads_writes(ops[pos])
        before[pos] = frozenset(live | reads)
        live = (live - writes) | reads
    return before, live, set(live)


def _analyse_sequence(ops: list, live_out: set, where: str, resources_: resources,
                      problem: allocation_problem, section_of=None) -> tuple[set, set]:
    """
    A sequence of operations' values, ranges and demands
    :return: (what is live before it, what it reads from outside)
    """
    before, live_in, exposed = _liveness(ops, live_out)
    for pos, op in enumerate(ops):
        section = section_of(pos) if section_of else where
        reads, writes = liveness.reads_writes(op)
        keeps = liveness.keeps(op)
        for key in reads | writes:
            carried = key in live_in and key in exposed and pos == 0
            entry = problem.values.get(key)
            rng = live_range(where, section, pos, pos, carried)
            # a value written in parts - a lane, a block, a tile's slice: one
            # value, a renamer only where it rewrites every part
            parted = entry.parts if entry is not None else False
            if keeps and key in writes:
                parted = True
            if entry is None:
                problem.values[key] = value(key=key, cls=resources_.class_of(key),
                                            ranges=(rng,), parts=parted, owner=key[0])
            else:
                problem.values[key] = value(key=key, cls=entry.cls,
                                            ranges=entry.ranges + (rng,),
                                            parts=parted, fixed=entry.fixed, owner=entry.owner)
        if isinstance(op, lsc_loop):
            _analyse_loop(op, before[pos] - reads, resources_, problem)
    # a value carried the whole sequence: one range over it
    for key in exposed & live_in:
        entry = problem.values.get(key)
        if entry is not None and entry.ranges:
            first = entry.ranges[0]
            problem.values[key] = value(key=key, cls=entry.cls,
                                        ranges=(live_range(where, first.section, 0,
                                                           len(ops) - 1, True),),
                                        parts=entry.parts, fixed=entry.fixed,
                                        owner=entry.owner)
    _demand(ops, live_out, where, resources_, problem)
    return live_in, exposed


def _analyse_loop(loop, live_out: set, resources_: resources,
                  problem: allocation_problem) -> None:
    """
    A loop's iteration: its sections one sequence (a prologue's write the
    value its body reads), the values across its back edge carried
    """
    sections = [(name, op) for name in lsc_loop.SECTIONS
                for op in loop.sections.get(name) or []]
    ops = [op for _, op in sections]
    if not ops:
        return
    names = [name for name, _ in sections]
    _analyse_sequence(ops, live_out, f"{loop.info.get('component')}<{loop.info.get('kind')}>",
                      resources_, problem, section_of=lambda pos: names[pos])


def _demand(ops: list, live_out: set, where: str, resources_: resources,
            problem: allocation_problem) -> None:
    """What each file needs here: the values of it live at once, and the names"""
    before, _, _ = _liveness(ops, live_out)
    tags = {}

    def tag_of(key):
        if key not in tags:
            entry = resources_.class_of(key)
            tags[key] = None if entry is None else entry.tag
        return tags[key]

    names, live_max = {}, {}
    for pos, op in enumerate(ops):
        reads, writes = liveness.reads_writes(op)
        live = before[pos] | reads | writes
        for tag in {tag_of(key) for key in live if tag_of(key) is not None}:
            names.setdefault(tag, set()).update(key for key in live if tag_of(key) == tag)
            live_max[tag] = max(live_max.get(tag, 0),
                                sum(1 for key in live if tag_of(key) == tag))
    for tag, keys in names.items():
        problem.demands.append(demand(tag, where, live_max.get(tag, 0), len(keys),
                                      resources_.pools.get(tag, 0)))


def analyse(program, resources_: resources) -> allocation_problem:
    """
    A program's allocation problem: every block's sections, its loops' own,
    the k loop's ring values and its sections
    """
    problem = allocation_problem()
    blocks = list(program.blocks) + [b for case in program.cases for b in case.blocks]
    for pos, block in enumerate(blocks):
        later = blocks[pos + 1:]
        live_out = set()
        for after in later:
            for section in ("init", "prologue", "body", "epilogue", "tail", "subtail"):
                for op in getattr(after, section, None) or []:
                    live_out |= liveness.reads_writes(op)[0]
        ops, names = [], []
        for section in ("init", "prologue", "body", "epilogue", "tail", "subtail"):
            for op in getattr(block, section, None) or []:
                ops.append(op)
                names.append(section)
        if not ops:
            continue
        _analyse_sequence(ops, live_out, block.name, resources_, problem,
                          section_of=lambda pos: names[pos])
    # the renames a renamer can't make, with what they need: a value written in
    # parts, one an instruction pins, one the model or the user fixed - the
    # question "must this be the allocation's" answered per value
    for key in sorted(problem.values, key=str):
        entry = problem.values[key]
        if entry.parts:
            problem.deferred.append(deferred(
                key, "written in parts (a lane, a block, a tile's slice)",
                "a renamer rewriting every part, or one register kept for it"))
        elif entry.cls is not None and entry.cls.allowed is not None:
            problem.deferred.append(deferred(
                key, "an instruction pins it",
                "one of the vector registers " + str(list(entry.cls.allowed))))
        elif entry.fixed is not None:
            problem.deferred.append(deferred(key, "fixed by the model or the user",
                                             str(entry.fixed)))
    return problem


@dataclass
class allocation_result:
    """The allocation's answer: a number per virtual register, and what it
    couldn't place (a section whose names don't fit, a value no register of its
    class meets)"""
    bindings: dict = field(default_factory=dict)
    unfitted: list = field(default_factory=list)

    def number(self, key) -> tuple | None:
        """The (tag, number) a value takes, or None where it wasn't placed"""
        return self.bindings.get(key)

    def report(self) -> str:
        lines = [f"{len(self.bindings)} values placed, {len(self.unfitted)} not"]
        for key, why in self.unfitted:
            lines.append(f"  {key[0]}{key[1]}: {why}")
        return "\n".join(lines)


def _overlaps(a: value, b: value) -> bool:
    """
    Whether two values are live at once: a range of one intersecting a range of
    the other in the same block - a carried range the whole of its loop, so it
    meets everything there
    """
    for one in a.ranges:
        for other in b.ranges:
            if one.block != other.block:
                continue
            if one.carried or other.carried:
                return True
            if one.first <= other.last and other.first <= one.last:
                return True
    return False


def allocate(problem: allocation_problem, resources_: resources) -> allocation_result:
    """
    The second pass: a static number per virtual register, no emission. The
    fixed ones as given, then the most constrained - fewest registers of its
    class to choose from, then longest lived, then by name - each taking the
    lowest register of its class free of every value it is live at once with;
    a group's registers consecutive and aligned, as its class says
    """
    result = allocation_result()
    by_tag: dict = {}
    for key, entry in problem.values.items():
        if entry.cls is None:
            result.unfitted.append((key, "no register class (not a data or address file yet)"))
            continue
        by_tag.setdefault(entry.cls.tag, []).append(key)

    def choices(entry):
        allowed = entry.cls.allowed
        pool = resources_.pools.get(entry.cls.tag, 0)
        return list(allowed) if allowed is not None else list(range(pool))

    for tag, keys in sorted(by_tag.items()):
        pool = resources_.pools.get(tag, 0)
        if pool <= 0:
            # a file the problem's resources say nothing of (the tiles' own,
            # asmgen's tag by data type: the emitter's to name until step 4's)
            for key in keys:
                result.unfitted.append((key, f"no pool known for the {tag} file"))
            continue
        taken: list = []            # (key, entry, first of its units)
        for key in sorted(keys, key=lambda k: (len(choices(problem.values[k])),
                                               -_span(problem.values[k]), str(k))):
            entry = problem.values[key]
            size = max(1, entry.cls.size)
            align = max(1, entry.cls.align)
            free = [c for c in choices(entry)
                    if c % align == 0 and c + size <= pool
                    and all(abs(c - other) >= max(size, problem.values[k2].cls.size)
                            for k2, other, _ in taken
                            if _overlaps(entry, problem.values[k2]))]
            if not free:
                result.unfitted.append((key, f"no {tag} register free of the values it is live "
                                             f"with ({len(choices(entry))} of the file's {pool})"))
                continue
            number = free[0]
            result.bindings[key] = (tag, number)
            taken.append((key, number, number))
        if len(taken) > pool:
            result.unfitted.append(((tag, 0), f"{len(taken)} names for {pool} {tag} registers"))
    return result


def _span(entry: value) -> int:
    """How long a value is live, its ranges together: the longest first"""
    return sum(r.last - r.first + 1 for r in entry.ranges)


def validate(problem: allocation_problem, result: allocation_result,
             resources_: resources) -> list:
    """
    What is wrong with a result, as text: a value left unplaced that some
    register of its class could hold, two values live at once sharing a
    register (or one of a group's), a number outside the file, an alignment or
    an allowed register broken. Empty where it is right - the check the
    allocation's tests and tools assert
    """
    wrong = []
    for key, entry in problem.values.items():
        placed = result.number(key)
        if placed is None:
            continue
        tag, number = placed
        pool = resources_.pools.get(tag, 0)
        size, align = max(1, entry.cls.size), max(1, entry.cls.align)
        if entry.cls.allowed is not None and number not in entry.cls.allowed:
            wrong.append(f"{key[0]}{key[1]} at {number}, not one of {list(entry.cls.allowed)}")
        if number % align or number + size > pool:
            wrong.append(f"{key[0]}{key[1]} at {number} (size {size}, align {align}, {pool} registers)")
    keys = [k for k in problem.values if result.number(k) is not None]
    for pos, one in enumerate(keys):
        for other in keys[pos + 1:]:
            a, b = problem.values[one], problem.values[other]
            if a.cls.tag != b.cls.tag or not _overlaps(a, b):
                continue
            gap = abs(result.number(one)[1] - result.number(other)[1])
            if gap < max(a.cls.size, b.cls.size):
                wrong.append(f"{one[0]}{one[1]} and {other[0]}{other[1]} share "
                             f"{result.number(one)[1]} live at once")
    return wrong
