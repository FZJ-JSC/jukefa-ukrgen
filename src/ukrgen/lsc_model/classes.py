"""
A value's register class (docs/REGISTER_ALLOCATION.md step 3: the analysis
pass's classes) - what register a value can take: the renamer considers only
dead registers of a compatible class, the allocation assigns within it
"""

from dataclasses import dataclass

from asmgen.asmblocks.op import register_type as rgt

#: a register type's tracker tag
TAGS = {rgt.VEC: "vreg", rgt.FP: "freg", rgt.TILE: "treg"}


@dataclass(frozen=True)
class register_class:
    #: the tracker's register type (its file: the tracker's pool)
    tag: str
    #: registers taken together (a group's ways, a structfuse part's size)
    size: int = 1
    #: the first a multiple of this (a group's: its ways)
    align: int = 1
    #: the registers it may take - None: any of its file
    allowed: tuple | None = None


def register_class_of(key: tuple, groups: dict, dts: dict, bounds: dict,
                      tile_tag=None) -> register_class | None:
    """
    The class of a data register's value - key (component, number, register
    type), its data type by its value (dts: by the value's own register),
    groups (structfuse's parts, RVV's and SVE's consecutive groups), bounds (a
    vector register's allowed ones), tile_tag (asmgen's treg_tag: the
    tracker's type of a data type's tiles)
    """
    comp, number, rtype = key
    tag = TAGS.get(rtype)
    if tag is None:
        return None
    if rgt.TILE == rtype:
        dt = dts.get((comp, number))
        return register_class(tile_tag(dt) if tile_tag is not None and dt is not None else tag)
    if rgt.VEC != rtype:
        return register_class(tag)
    group = groups.get(comp)
    parts = group[2] if group is not None and len(group) > 2 else None
    if parts is not None:
        part = next(((s, n) for s, n in parts.items() if s <= number < s + n), None)
        if part is not None:
            return register_class(tag, size=part[1], align=1)
    elif group is not None:
        return register_class(tag, size=group[0], align=group[0])
    allowed = bounds.get(key)
    return register_class(tag, allowed=tuple(allowed) if allowed is not None else None)


def units(cls: register_class, number: int, rt) -> frozenset:
    """
    What a register of a class occupies at a number - what must be dead for a
    value to take it: the tracker's storage of each register it takes (a
    group's consecutive ones; SME's tiles: za0.s is za0.d and za4.d; SVE's
    d3 is v3) - no ISA's layout here, the tracker's (asmgen); two values
    conflict where their units meet
    """
    out = set()
    for k in range(cls.size):
        out |= rt.storage(cls.tag, number + k)
    return frozenset(out)


def fits(cls: register_class, number: int, rt) -> bool:
    """
    Whether a register number suits a class: one it may take, aligned to its
    group, one of the registers its type has (the tracker's: four tiles of
    singles - no za5.s)
    """
    if cls.allowed is not None and number not in cls.allowed:
        return False
    if cls.align > 1 and number % cls.align:
        return False
    return 0 <= number and number + cls.size <= rt.max_regs.get(cls.tag, 0)


def compatible(a: register_class, b: register_class, rt) -> bool:
    """Whether values of two classes can follow each other in a register: one file (the tracker's pool), one group shape"""
    return rt.pool(a.tag) == rt.pool(b.tag) and a.size == b.size and a.align == b.align
