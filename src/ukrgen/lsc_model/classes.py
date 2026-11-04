"""
A value's register class (docs/REGISTER_ALLOCATION.md step 3: the analysis
pass's classes) - what register a value can take: the renamer considers only
dead registers of a compatible class, the allocation assigns within it
"""

from dataclasses import dataclass

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

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
    #: its element size in bytes where the file depends on it (ZA's tiles)
    element: int | None = None


def register_class_of(key: tuple, groups: dict, dts: dict, bounds: dict) -> register_class | None:
    """
    The class of a data register's value - key (component, number, register
    type), its data type by its value (dts: by the value's own register),
    groups (structfuse's parts, RVV's and SVE's consecutive groups), bounds (a
    vector register's allowed ones)
    """
    comp, number, rtype = key
    tag = TAGS.get(rtype)
    if tag is None:
        return None
    if rgt.TILE == rtype:
        dt = dts.get((comp, number))
        return register_class(tag, element=adt_size(dt) if dt is not None else None)
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
