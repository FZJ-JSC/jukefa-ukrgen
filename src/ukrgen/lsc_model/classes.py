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


#: ZA's 64-bit tiles: a tile of element size e bytes is one of e, covering
#: eight of them over e
ZA_UNITS = 8


def units(cls: register_class, number: int, pool: frozenset | None = None) -> frozenset:
    """
    The physical units a register of a class occupies at a number - what must
    be dead for a value to take it: a tile of element size e (one of e) the
    64-bit tiles number + k*e (ZA's overlap: za0.s is za0.d and za4.d); a
    group its consecutive registers; else the register - in its file (the
    tracker's pool: SVE's FP registers the low parts of its vector registers,
    one unit)
    """
    file = pool if pool is not None else frozenset({cls.tag})
    if "treg" == cls.tag and cls.element:
        return frozenset((file, number + k * cls.element) for k in range(ZA_UNITS // cls.element))
    return frozenset((file, number + k) for k in range(cls.size))


def fits(cls: register_class, number: int) -> bool:
    """
    Whether a register number suits a class: one it may take, aligned to its
    group, a tile there is for its element size (four of singles: no za5.s)
    """
    if cls.allowed is not None and number not in cls.allowed:
        return False
    if cls.align > 1 and number % cls.align:
        return False
    if "treg" == cls.tag and cls.element and number >= cls.element:
        return False
    return True


def compatible(a: register_class, b: register_class, pool_a: frozenset, pool_b: frozenset) -> bool:
    """Whether values of two classes can follow each other in a register: one file"""
    return pool_a == pool_b and a.size == b.size and a.align == b.align
