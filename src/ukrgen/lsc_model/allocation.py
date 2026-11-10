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

from dataclasses import dataclass, field, replace
from typing import Callable

from asmgen.asmblocks.noarch import asmgen
from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import asm_data_type as adt, reg_tracker

from . import classes, dtypes, liveness
from ..models.load_store_operations import lsc_loop
from .ir import ir_program

#: A virtual register's name: its component, its number within it and the kind
#: of register it is for (a vector, a scalar, a tile, an address). What the
#: renamer and the allocation keep or change; the number is what the model made
#: it, a ring slot or a copy's own.
register_key = tuple[str, int, rgt | None]

#: A physical register: its file (the tracker's tag) and its number in it
register_number = tuple[str, int]


@dataclass(frozen=True)
class live_range:
    """
    Where a virtual register is live
    :param block: the name of the IR block
    :param section: the section it starts in (`prologue`, `body`, `epilogue`,
                    `tail`, `subtail` - or a loop's own, by its name)
    :param first: the first operation of the sequence it appears in
    :param last: the last operation of it
    :param carried: live across a loop's back edge - then one range over the
                    whole iteration, first and last the sequence's ends
    """
    block: str
    section: str
    first: int
    last: int
    carried: bool = False


@dataclass(frozen=True)
class fixed_register:
    """
    Where a virtual register's number comes from although it isn't the
    allocation's to choose: a slot of its component's ring (the model's - the
    ring's registers a block of the file, the slot's number the block's base
    plus the slot), or the one register an instruction takes (`ring` None)
    :param slot: the slot within the ring, or the register itself
    :param why: what fixed it, for the report - "the model's A ring, slot 0"
    :param ring: the component whose ring gives the base, None for a register
                 an instruction pins
    """
    slot: int
    why: str
    ring: str | None = None


@dataclass(frozen=True)
class virtual_register:
    """
    A virtual register and what it needs - what the allocation binds a number
    for and the emitter looks up
    :param key: its name (`register_key`)
    :param register_class: its file and classes (`classes.register_class`: the
                           tracker's tag, its units, alignment and the
                           registers it may take), None where no data register
                           file is known for it yet
    :param ranges: its live ranges (`live_range`), one per live stretch - the
                   loop's iteration one sequence, so a prologue's write and the
                   body's read are one value
    :param parts: written in parts - a lane, a block, a tile's slice: one value,
                  never split, and a renamer's target only where it rewrites
                  all of it
    :param fixed: where its number isn't the allocation's to choose
                  (`fixed_register`)
    :param owner: the component whose data type forms its instruction
    """
    key: register_key
    register_class: classes.register_class | None
    ranges: tuple[live_range, ...]
    parts: bool = False
    fixed: fixed_register | None = None
    owner: str | None = None

    @property
    def tag(self) -> str | None:
        """Its file, the tracker's tag - None where it has no class"""
        return None if self.register_class is None else self.register_class.tag


@dataclass
class demand:
    """
    What one file needs in one place: the values of it live at once and the
    names - a name holds a register the iteration long, so the names are what a
    static allocation must fit
    :param tag: the file, the tracker's tag
    :param where: the block or loop the demand is in
    :param live: the most values of the file live at once there
    :param names: the names of the file the place holds
    :param pool: the registers the file has
    """
    tag: str
    where: str
    live: int
    names: int
    pool: int

    @property
    def fits(self) -> bool:
        """Whether the place's names fit the file's registers"""
        return self.names <= self.pool


@dataclass
class deferred:
    """
    A rename the renamer (the MRU on virtual registers) can't make, and what it
    would need to - kept apart so the question "does this have to be the
    allocator's or can the renamer be taught it" has an answer
    :param key: the virtual register it is about
    :param why: what stops the renamer - written in parts, pinned by an
                instruction, fixed by the model
    :param requires: what it would take to rename it
    """
    key: register_key
    why: str
    requires: str


@dataclass
class resources:
    """
    What the machine offers, as both passes need it: the register files, their
    sizes, the groups, and what a register's class is computed from
    :param pools: the tracker's tag -> the numbers it can take (a file's
                  several views each have their own, the scalars' the vectors'
                  where they are their low halves)
    :param groups: component -> its register group (ways, and a structfuse
                   part's sizes), the model's
    :param dts: a virtual data register's data type (`dtypes.register_types`)
    :param bounds: a vector register's allowed registers, where its operands
                   limit them
    :param tile_tag: a data type's tile file, asmgen's tag - None for an ISA
                     without tiles
    :param tracker: the register tracker the files and what their registers
                    occupy come from (asmgen's `reg_tracker`) - its
                    `registered_types`, `max_regs`, `pool` and `storage` the
                    machine, no layout here
    :param reserved: tag -> the numbers it can't give a value: what the
                     machinery holds there before any value is placed (RVV's
                     mask is its vector 0, one register of a file of its own
                     sharing it) - a value placed there would clobber it
    """
    pools: dict[str, int] = field(default_factory=dict)
    groups: dict = field(default_factory=dict)
    dts: dict[tuple, adt] = field(default_factory=dict)
    bounds: dict[tuple, list[int]] = field(default_factory=dict)
    tile_tag: Callable[[adt], str] | None = None
    tracker: reg_tracker | None = None
    reserved: dict[str, set[int]] = field(default_factory=dict)

    def pool_of(self, tag: str) -> frozenset[str]:
        """
        The register file a tag's numbers belong to: the types sharing them
        (NEON's and SVE's scalars are their vectors' low halves, SME's smaller
        tiles the 64-bit ones, RVV's masks its vector 0)
        :param tag: the tracker's tag
        :return: the tags whose registers hold it, the tag alone without a
                 tracker to say
        """
        if self.tracker is None:
            return frozenset({tag})
        return self.tracker.pool(tag)

    def units(self, klass : classes.register_class, number : int) -> frozenset:
        """
        What a value of a class occupies at a number - what must be dead for it
        to take the register: a group's consecutive ones, a tile's the storage
        it shares
        :param klass: the value's register class
        :param number: the number
        :return: (tag, number) of each register it covers
        """
        if self.tracker is None:
            return frozenset((klass.tag, number + k) for k in range(max(1, klass.size)))
        return classes.units(klass, number, self.tracker)

    def class_of(self, key : register_key) -> classes.register_class | None:
        """
        The class of a virtual register's value
        :param key: the virtual register
        :return: its class, None where it isn't a data register
        """
        return classes.register_class_of(key, self.groups, self.dts, self.bounds,
                                         tile_tag=self.tile_tag)

    @classmethod
    def of(cls, program : ir_program, gen : asmgen, component_dts : dict[str, adt],
           tracker : reg_tracker | None = None) -> "resources":
        """
        The machine as the tracker knows it
        :param program: the IR the values' data types come from
        :param gen: the ISA's generator - its tracker, and the tile tags
        :param component_dts: component -> its data type (the ctx's)
        :param tracker: the register tracker to read the machine from - the
                        generator's own where None
        :return: the resources, every file the tracker has a pool for
        """
        dts = dtypes.register_types(program, component_dts)
        tracker = gen.get_reg_tracker() if tracker is None else tracker
        pools = {tag: size for tag, size in tracker.max_regs.items()}
        try:
            tile_tag = gen.treg_tag       # an ISA without tiles has none
        except AttributeError:
            tile_tag = None
        # the machinery's registers: the mask file's numbers that are a value
        # file's storage - RVV's m0 is v0, one register for the whole program's
        # masks - so no value can have them. SME's tile views (treg8 is one
        # register over the 64-bit tiles) are values' files, not this
        reserved: dict[str, set[int]] = {}
        for number in range(tracker.max_regs.get("mreg", 0)):
            for storage_tag, storage_number in tracker.storage("mreg", number):
                if storage_tag != "mreg" and storage_tag in pools:
                    reserved.setdefault(storage_tag, set()).add(storage_number)
        return cls(pools=pools, groups=program.groups, dts=dts, tile_tag=tile_tag,
                   tracker=tracker, reserved=reserved)


@dataclass
class allocation_problem:
    """
    The analysis' answer: every virtual register, what each file needs where,
    and the renames that aren't the renamer's
    :param values: virtual register name (`register_key`) -> `virtual_register`
    :param demands: one `demand` per file and place
    :param deferred: the renames the renamer can't make (`deferred`)
    """
    values: dict[register_key, virtual_register] = field(default_factory=dict)
    demands: list[demand] = field(default_factory=list)
    deferred: list[deferred] = field(default_factory=list)

    def short(self) -> list[demand]:
        """The demands that don't fit their file"""
        return [d for d in self.demands if not d.fits]

    def pressure(self, tag: str) -> int:
        """
        The most of a file live at once, any place
        :param tag: the file, the tracker's tag
        """
        return max((d.live for d in self.demands if d.tag == tag), default=0)

    def names(self, tag: str) -> int:
        """
        The most names of a file any place holds
        :param tag: the file, the tracker's tag
        """
        return max((d.names for d in self.demands if d.tag == tag), default=0)

    def report(self) -> str:
        """The problem as text: what every file needs where, and what the
        renamer can't do"""
        lines = [f"{len(self.values)} virtual registers, {len(self.deferred)} renames the "
                 f"renamer can't make"]
        for d in self.demands:
            state = "ok" if d.fits else "SHORT"
            lines.append(f"  {d.tag:5s} {d.where:28s} live {d.live:3d} names {d.names:3d} "
                         f"of {d.pool:3d} {state}")
        for f in self.deferred:
            lines.append(f"  keep {f.key[0]}{f.key[1]}: {f.why} - needs {f.requires}")
        return "\n".join(lines)


def _liveness(ops : list, live_out : set[register_key]) -> tuple[list, set[register_key]]:
    """
    Backward liveness over a straight sequence of operations
    :param ops: the operations, in the order they run
    :param live_out: what is live after the last of them
    :return: (what is live before each, what is live before the first - the
             values coming from outside)
    """
    before: list = [frozenset() for _ in ops]
    live = set(live_out)
    for pos in reversed(range(len(ops))):
        reads, writes = liveness.reads_writes(ops[pos])
        before[pos] = frozenset(live | reads)
        live = (live - writes) | reads
    return before, live


def _analyse_sequence(ops : list, live_out : set[register_key], where : str,
                      resources_ : resources, problem : allocation_problem,
                      section_of : Callable[[int], str] | None = None) -> tuple[set[register_key],
                                                                                set[register_key]]:
    """
    A sequence of operations' virtual registers, their ranges and their demand
    :param ops: the operations, in the order they run
    :param live_out: what is live after the last of them
    :param where: the block or loop the sequence is in, for the ranges' and
                  demands' names
    :param resources_: the machine
    :param problem: the problem the values and demands are added to
    :param section_of: position -> the section's name, where the sequence spans
                       sections (a loop's iteration)
    :return: (what is live before the sequence, what it reads from outside -
             written before read within it)
    """
    before, live_in = _liveness(ops, live_out)
    for pos, op in enumerate(ops):
        section = section_of(pos) if section_of else where
        reads, writes = liveness.reads_writes(op)
        keeps = liveness.keeps(op)
        for key in reads | writes:
            carried = key in live_in and pos == 0
            entry = problem.values.get(key)
            rng = live_range(where, section, pos, pos, carried)
            # a value written in parts - a lane, a block, a tile's slice: one
            # value, a renamer only where it rewrites every part
            parted = entry.parts if entry is not None else False
            if keeps and key in writes:
                parted = True
            if entry is None:
                problem.values[key] = virtual_register(key=key,
                                                       register_class=resources_.class_of(key),
                                                       ranges=(rng,), parts=parted, owner=key[0])
            else:
                problem.values[key] = virtual_register(key=key,
                                                       register_class=entry.register_class,
                                                       ranges=entry.ranges + (rng,),
                                                       parts=parted, fixed=entry.fixed,
                                                       owner=entry.owner)
        if isinstance(op, lsc_loop):
            _analyse_loop(op, before[pos] - reads, resources_, problem)
    # a value carried the whole sequence: one range over it
    for key in live_in:
        entry = problem.values.get(key)
        if entry is not None and entry.ranges:
            first = entry.ranges[0]
            problem.values[key] = virtual_register(
                key=key, register_class=entry.register_class,
                ranges=(live_range(where, first.section, 0, len(ops) - 1, True),),
                parts=entry.parts, fixed=entry.fixed, owner=entry.owner)
    _demand(ops, live_out, where, resources_, problem)
    return live_in, live_in


def _analyse_loop(loop : lsc_loop, live_out : set[register_key], resources_ : resources,
                  problem : allocation_problem) -> None:
    """
    A loop's iteration: its sections one sequence (a prologue's write the value
    its body reads), the values across its back edge carried
    :param loop: the loop, an `lsc_loop` of a block
    :param live_out: what is live after the loop
    :param resources_: the machine
    :param problem: the problem the values and demands are added to
    """
    sections = [(name, op) for name in lsc_loop.SECTIONS
                for op in loop.sections.get(name) or []]
    ops = [op for _, op in sections]
    if not ops:
        return
    names = [name for name, _ in sections]
    _analyse_sequence(ops, live_out, f"{loop.info.get('component')}<{loop.info.get('kind')}>",
                      resources_, problem, section_of=lambda pos: names[pos])


def _demand(ops : list, live_out : set[register_key], where : str, resources_ : resources,
            problem : allocation_problem) -> None:
    """
    What each file needs here: the values of it live at once, and the names
    :param ops: the operations, in the order they run
    :param live_out: what is live after the last of them
    :param where: the block or loop, for the demand's name
    :param resources_: the machine - the pools and the classes
    :param problem: the problem the demands are added to
    """
    before, _ = _liveness(ops, live_out)
    tags: dict[register_key, str | None] = {}

    def tag_of(key : register_key) -> str | None:
        """A virtual register's file, the tracker's tag - None for no class"""
        if key not in tags:
            entry = resources_.class_of(key)
            tags[key] = None if entry is None else entry.tag
        return tags[key]

    names: dict[str, set[register_key]] = {}
    live_max: dict[str, int] = {}
    for pos, op in enumerate(ops):
        reads, writes = liveness.reads_writes(op)
        per_file: dict[str, set[register_key]] = {}
        for key in before[pos] | reads | writes:
            tag = tag_of(key)
            if tag is not None:
                per_file.setdefault(tag, set()).add(key)
        for tag, keys in per_file.items():
            names.setdefault(tag, set()).update(keys)
            live_max[tag] = max(live_max.get(tag, 0), len(keys))
    for tag, keys in names.items():
        problem.demands.append(demand(tag, where, live_max.get(tag, 0), len(keys),
                                      resources_.pools.get(tag, 0)))


def analyse(program : ir_program, resources_ : resources) -> allocation_problem:
    """
    A program's allocation problem: every block's sections, its loops' own,
    the model's rings and the registers an instruction pins
    :param program: the IR, after the address passes (one allocation for all of
                    it, cases included)
    :param resources_: the machine
    :return: the problem - the values, the demands and the renames the renamer
             can't make
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
    # the values whose register isn't the allocation's to choose: a slot of
    # the component's ring - the model says which component holds how many,
    # so slot k is the k-th of them - and a value only one register meets
    for key in list(problem.values):
        entry = problem.values[key]
        if entry.register_class is None:
            continue
        ring = program.registers.get(key[0])
        if ring is not None and ring[0] == key[2] and 0 <= key[1] < ring[1]:
            problem.values[key] = replace(entry, fixed=fixed_register(
                key[1], f"the model's {key[0]} ring, slot {key[1]}", ring=key[0]))
        elif entry.register_class.allowed is not None and 1 == len(entry.register_class.allowed):
            problem.values[key] = replace(entry, fixed=fixed_register(
                int(entry.register_class.allowed[0]),
                "the only register its instruction takes"))
    # the renames a renamer can't make, with what they need: a value written in
    # parts, one an instruction pins, one the model or the user fixed - the
    # question "must this be the allocation's" answered per value
    for key in sorted(problem.values, key=str):
        entry = problem.values[key]
        if entry.parts:
            problem.deferred.append(deferred(
                key, "written in parts (a lane, a block, a tile's slice)",
                "a renamer rewriting every part, or one register kept for it"))
        elif entry.register_class is not None and entry.register_class.allowed is not None:
            problem.deferred.append(deferred(
                key, "an instruction pins it",
                "one of the vector registers " + str(list(entry.register_class.allowed))))
        elif entry.fixed is not None:
            where = (f"register {entry.fixed.slot} of the {entry.fixed.ring} ring"
                     if entry.fixed.ring is not None else f"register {entry.fixed.slot}")
            problem.deferred.append(deferred(key, "fixed: " + entry.fixed.why, where))
    return problem


@dataclass
class allocation_result:
    """
    The allocation's answer: a number per virtual register, and what it couldn't
    place (a section whose names don't fit, a value no register of its class
    meets)
    :param bindings: virtual register name -> its register (`register_number`)
    :param unfitted: (the virtual register or file, why it wasn't placed)
    """
    bindings: dict[register_key, register_number] = field(default_factory=dict)
    unfitted: list[tuple[register_key, str]] = field(default_factory=list)

    def number(self, key : register_key) -> register_number | None:
        """
        The register a virtual one takes
        :param key: the virtual register
        :return: (the file's tag, its number), None where it wasn't placed
        """
        return self.bindings.get(key)

    def report(self) -> str:
        """What was placed and what wasn't, as text"""
        lines = [f"{len(self.bindings)} values placed, {len(self.unfitted)} not"]
        for key, why in self.unfitted:
            lines.append(f"  {key[0]}{key[1]}: {why}")
        return "\n".join(lines)


def _overlaps(a : virtual_register, b : virtual_register) -> bool:
    """
    Whether two virtual registers are live at once
    :param a: one of them
    :param b: the other
    :return: True where a range of one intersects a range of the other in the
             same block - a carried range the whole of its loop, so it meets
             everything there
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


def _rings(problem : allocation_problem, resources_ : resources) -> dict[str, tuple[str, int, int]]:
    """
    Each ring's block of its file: the model's components given a run of
    registers of their own, the slot's number the block's base plus the slot
    :param problem: the problem, whose fixed values name the rings' slots
    :param resources_: the machine - the pools the blocks come from
    :return: component -> (the file's tag, the block's base, its width); the
             components that found no room left out
    """
    need: dict[str, int] = {}
    tags: dict[str, str] = {}
    widths: dict[str, int] = {}
    for entry in problem.values.values():
        if entry.fixed is None or entry.fixed.ring is None or entry.register_class is None:
            continue
        ring = entry.fixed.ring
        tags[ring] = entry.register_class.tag
        need[ring] = max(need.get(ring, 0), entry.fixed.slot + 1)
        widths[ring] = max(widths.get(ring, 1), max(1, entry.register_class.size))
    blocks : dict[str, tuple[str, int, int]] = {}
    # the machinery's own numbers are taken before any ring claims a block
    used : dict[str, set[int]] = {tag: set(numbers)
                                  for tag, numbers in resources_.reserved.items()}
    # in the order their values first appear - the emitter's own, the one the
    # kernel reaches first getting the bottom of the file
    first : dict[str, int] = {}
    for pos, entry in enumerate(problem.values.values()):
        if entry.fixed is not None and entry.fixed.ring is not None:
            first.setdefault(entry.fixed.ring, pos)
    for comp in sorted(need, key=lambda c: (first.get(c, 0), c)):
        tag, size, ways = tags[comp], need[comp], widths[comp]
        pool = resources_.pools.get(tag, 0)
        taken = used.setdefault(tag, set())
        base = next((b for b in range(0, pool - size + 1, ways)
                     if not any(b + i in taken for i in range(size))), None)
        if base is None:
            continue
        taken.update(range(base, base + size))
        blocks[comp] = (tag, base, size)
    return blocks


def allocate(problem : allocation_problem, resources_ : resources) -> allocation_result:
    """
    The second pass: a static number per virtual register, no emission
    :param problem: the analysis' answer
    :param resources_: the machine - the files' sizes and what each register
                       may take
    :return: the numbers, and what couldn't be placed. The fixed ones as given
             - a ring's block of the file, the slot's number the block's base
             plus the slot, an instruction's only register - then the most
             constrained (fewest registers of its class to choose from, then
             longest lived, then by name), each taking the lowest register of
             its class free of every value it is live at once with; a group's
             registers consecutive and aligned, as its class says
    """
    result = allocation_result()
    # the model's rings first: they claim their blocks before anything else
    # of their file is placed
    rings = _rings(problem, resources_)
    for key in sorted(problem.values, key=str):
        entry = problem.values[key]
        if entry.fixed is None or entry.register_class is None:
            continue
        if entry.fixed.ring is not None:
            block = rings.get(entry.fixed.ring)
            if block is None:
                result.unfitted.append((key, f"no room in the {entry.register_class.tag} file "
                                             f"for the {entry.fixed.ring} ring"))
                continue
            tag, base, _ = block
            result.bindings[key] = (tag, base + entry.fixed.slot)
        else:
            result.bindings[key] = (entry.register_class.tag, entry.fixed.slot)
    # the values the rings and the instructions didn't place, by the file
    # their numbers come from: its views conflict with one another
    by_pool: dict[frozenset[str], list[register_key]] = {}
    for key, entry in problem.values.items():
        if entry.register_class is None:
            result.unfitted.append((key, "no register class (not a data or address file yet)"))
            continue
        if result.number(key) is not None:
            continue
        by_pool.setdefault(resources_.pool_of(entry.register_class.tag), []).append(key)

    def choices(entry : virtual_register) -> list[int]:
        """The numbers a value's class lets it take"""
        klass = entry.register_class
        if klass is None:
            return []
        pool = resources_.pools.get(klass.tag, 0)
        held = resources_.reserved.get(klass.tag, set())
        numbers = list(klass.allowed) if klass.allowed is not None else list(range(pool))
        return [n for n in numbers if n not in held]

    def held(entry : virtual_register, number : int) -> frozenset:
        """The registers a value at a number occupies"""
        klass = entry.register_class
        return frozenset() if klass is None else resources_.units(klass, number)

    for pool_tags, keys in sorted(by_pool.items(), key=lambda item: sorted(item[0])):
        pool = max((resources_.pools.get(tag, 0) for tag in pool_tags), default=0)
        if pool <= 0:
            for key in keys:
                result.unfitted.append((key, f"no pool known for the "
                                             f"{'/'.join(sorted(pool_tags))} file"))
            continue
        # what the fixed ones of this file already hold: (the value, its number)
        taken: list[tuple[virtual_register, int]] = []
        for k, entry in problem.values.items():
            placed = result.number(k)
            if placed is None or entry.register_class is None \
                    or resources_.pool_of(entry.register_class.tag) != pool_tags:
                continue
            taken.append((entry, placed[1]))
        for key in sorted(keys, key=lambda k: (len(choices(problem.values[k])),
                                               -_span(problem.values[k]), str(k))):
            entry = problem.values[key]
            size, align = _units(entry)
            free = [c for c in choices(entry)
                    if c % align == 0 and c + size <= resources_.pools.get(_tag(entry) or "", 0)
                    and all(not (held(entry, c) & held(other, number))
                            for other, number in taken if _overlaps(entry, other))]
            if not free:
                result.unfitted.append((key, f"no {'/'.join(sorted(pool_tags))} register free "
                                             f"of the values it is live with "
                                             f"({len(choices(entry))} of the file's "
                                             f"{resources_.pools.get(_tag(entry) or '', 0)})"))
                continue
            number = free[0]
            # the value's own tag: its instruction's view of the file
            result.bindings[key] = (_tag(entry) or sorted(pool_tags)[0], number)
            taken.append((entry, number))
    return result


def _tag(entry : virtual_register) -> str | None:
    """
    A virtual register's file, the tracker's tag
    :param entry: the virtual register
    :return: the tag, None where it has no class
    """
    return None if entry.register_class is None else entry.register_class.tag


def _units(entry : virtual_register) -> tuple[int, int]:
    """
    A value's width and alignment: a group's ways and the multiple its first
    register sits on, one and one where it has no class
    :param entry: the virtual register
    """
    klass = entry.register_class
    return (1, 1) if klass is None else (max(1, klass.size), max(1, klass.align))


def _span(entry : virtual_register) -> int:
    """
    How long a virtual register is live, its ranges together
    :param entry: the virtual register
    """
    return sum(r.last - r.first + 1 for r in entry.ranges)


def validate(problem : allocation_problem, result : allocation_result,
             resources_ : resources) -> list[str]:
    """
    What is wrong with a result, as text - the check the tests and tools assert
    empty
    :param problem: the analysis' answer
    :param result: the allocation's
    :param resources_: the machine
    :return: one line per fault: two values live at once sharing a register (or
             one of a group's), a number outside the file, an alignment or an
             allowed register broken; [] where it is right
    """
    wrong = []
    for key, entry in problem.values.items():
        placed = result.number(key)
        if placed is None or entry.register_class is None:
            continue
        tag, number = placed
        pool = resources_.pools.get(tag, 0)
        size, align = _units(entry)
        if number in resources_.reserved.get(tag, set()):
            wrong.append(f"{key[0]}{key[1]} at {number}, the machinery's own")
        allowed = entry.register_class.allowed
        if allowed is not None and number not in allowed:
            wrong.append(f"{key[0]}{key[1]} at {number}, not one of {list(allowed)}")
        if number % align or number + size > pool:
            wrong.append(f"{key[0]}{key[1]} at {number} (size {size}, align {align}, "
                         f"{pool} registers)")
    # the placed values, with the registers each occupies: two live at once
    bound : list[tuple[register_key, frozenset, virtual_register]] = []
    for key, entry in problem.values.items():
        placed = result.number(key)
        if placed is None or entry.register_class is None:
            continue
        bound.append((key, resources_.units(entry.register_class, placed[1]), entry))
    for pos, (one_key, one_held, one) in enumerate(bound):
        for other_key, other_held, other in bound[pos + 1:]:
            if _overlaps(one, other) and one_held & other_held:
                shared = ", ".join(f"{tag}{number}" for tag, number in sorted(one_held & other_held))
                wrong.append(f"{one_key[0]}{one_key[1]} and {other_key[0]}{other_key[1]} "
                             f"share {shared} live at once")
    return wrong
