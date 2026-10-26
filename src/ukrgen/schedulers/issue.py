"""
An issue model: the instructions a core issues in a cycle, by class
"""

from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt

from ..models.load_store_operations import (lsc_load, lsc_store, lsc_addr_compute, lsc_move,
                                            lsc_loop, lsc_transformation)

#: instruction classes: vector and scalar loads and stores, vector FP and
#: integer arithmetic, permutes, tile operations, scalar FP and integer
#: arithmetic, address arithmetic, branches
CLASSES = ("vl", "vs", "sl", "ss", "vf", "vi", "vp", "t", "f", "i", "addr", "br")
#: where no slot names a class: the class it is taken for
FALLBACK = {"addr": "i", "vs": "vl", "ss": "sl", "vp": "vf", "br": "i"}


class issue_model:
    """
    --sched-cycle-slots "[N:]slot,slot,...": each slot a class or classes
    joined by '|' (one of them a cycle), N the most issued a cycle (default:
    the slots). "2:vl|vs|vf,sl,i": a vector load, store or FP operation, a
    scalar load and an integer operation - two of them a cycle. An
    instruction of a class no slot names takes any free slot
    """

    def __init__(self, spec: str):
        text = spec.replace(" ", "")
        # ";a-b,c-d": classes never issued in the same cycle - the K1's vector
        # FP operation and scalar load, say, though each has a slot
        self.conflicts: set[frozenset] = set()
        if ";" in text:
            text, pairs = text.split(";", 1)
            for pair in filter(None, pairs.split(",")):
                a, _, b = pair.partition("-")
                if a not in CLASSES or b not in CLASSES:
                    raise ValueError(f"--sched-cycle-slots: conflict {pair} - classes are {', '.join(CLASSES)}")
                self.conflicts.add(frozenset((a, b)))
        width = None
        if ":" in text.split(",")[0]:
            head, text = text.split(":", 1)
            width = int(head)
        self.slots = []
        #: a slot taken at most once every n cycles ("sl/2"): a port's rate
        self.rate: dict[int, int] = {}
        #: an instruction of a class holding its slot n cycles ("vl*2"): what
        #: it occupies, nothing else issuing there meanwhile
        self.occupy: dict[tuple, int] = {}
        for slot in text.split(","):
            index = len(self.slots)
            if "/" in slot:
                slot, _, n = slot.rpartition("/")
                if int(n) > 1:
                    self.rate[index] = int(n)
            names = []
            for c in slot.split("|"):
                if "*" in c:
                    c, _, n = c.partition("*")
                    if int(n) > 1:
                        self.occupy[(index, c)] = int(n)
                names.append(c)
            classes = frozenset(names)
            unknown = classes - set(CLASSES)
            if unknown or not slot:
                raise ValueError(f"--sched-cycle-slots: {sorted(unknown) or 'an empty slot'} - "
                                 f"classes are {', '.join(CLASSES)}")
            self.slots.append(classes)
        self.width = width or len(self.slots)
        named = set().union(*self.slots)
        # a class no slot names is taken for its fallback's where one names that
        self.alias = {c: (FALLBACK[c] if c not in named and FALLBACK.get(c) in named else c)
                      for c in CLASSES}

    def accepts(self, cls: str) -> list[int]:
        """
        The slots an instruction of a class may take: those naming it, fewest
        classes first - any, where none does
        """
        cls = self.alias.get(cls, cls)
        named = [s for s, classes in enumerate(self.slots) if cls in classes]
        if not named:
            return list(range(len(self.slots)))
        return sorted(named, key=lambda s: len(self.slots[s]))

    def take(self, cls: str, used: set[int], issued: set[str] = frozenset(),
             blocked: set[int] = frozenset()) -> int | None:
        """
        The slot an instruction takes in a cycle whose slots used are used, or
        None where none is left, the cycle is full, or a class it can't
        issue beside is in it
        """
        if len(used) >= self.width:
            return None
        if any(frozenset((cls, other)) in self.conflicts for other in issued):
            return None
        return next((s for s in self.accepts(cls) if s not in used and s not in blocked), None)

    def holds(self, slot: int, cls: str) -> int:
        """
        The cycles an instruction of a class holds the slot it takes (1 but
        where the slot's spec gives it a *n)
        """
        return self.occupy.get((slot, self.alias.get(cls, cls)), 1)


def classify(op) -> str:
    """
    An instruction's class: by its operation and its registers
    """
    # the registers' machine types (rtypes: GP, FP, VEC, TILE) - reg_types
    # holds their roles in the IR (address, data)
    types = {t for t in (op.rtypes or []) if t is not None}
    vector = bool(types & {rgt.VEC})
    tile = bool(types & {rgt.TILE})
    if isinstance(op, lsc_load):
        return "vl" if vector or tile else "sl"
    if isinstance(op, lsc_store):
        return "vs" if vector or tile else "ss"
    if isinstance(op, lsc_addr_compute):
        return "addr"
    if isinstance(op, lsc_loop):
        return "br"
    if isinstance(op, lsc_move):
        return "vp" if vector else ("f" if rgt.FP in types else "i")
    if isinstance(op, lsc_transformation):
        if tile:
            return "t"
        if vector:
            return "vf"
        return "f" if rgt.FP in types else "i"
    return "i"
