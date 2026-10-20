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
        width = None
        if ":" in text.split(",")[0]:
            head, text = text.split(":", 1)
            width = int(head)
        self.slots = []
        for slot in text.split(","):
            classes = frozenset(slot.split("|"))
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

    def take(self, cls: str, used: set[int]) -> int | None:
        """
        The slot an instruction takes in a cycle whose slots used are used, or
        None where none is left or the cycle is full
        """
        if len(used) >= self.width:
            return None
        return next((s for s in self.accepts(cls) if s not in used), None)


def classify(op) -> str:
    """
    An instruction's class: by its operation and its registers
    """
    types = set(getattr(op, "reg_types", None) or [])
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
