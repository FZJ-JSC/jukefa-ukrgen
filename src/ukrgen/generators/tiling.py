"""
Tilings of an STO's iteration space.

An STO's operations are the points of its iteration space, counted in units of
what one execution of the chosen implementation covers along each index. Each
operand's coordinate in an operation is the point projected onto the operand's
own indices: A[m,k] at point (m,n,k) is at (m,k). A scalar has no indices and
projects to (), the same coordinate everywhere - what the diagonal band tiles
used to emulate. The mm generator hardcoded these projections for A, B and C;
here they come from the requirement, so mm, scaling and packing are the same
algorithm over different requirements.
"""

from __future__ import annotations

import itertools

from ..components.operation import operation
from ..components.tile import tile, dimension_properties as dimp, dimension_type as dimt

_ONE = dimp(dt=dimt.fixed, size=1)


def split_levels(order) -> list[tuple[str, str | None]]:
    """
    An order's entries as (index, level): level None for an index in one
    level, "reg" for an uppercase letter whose lowercase stands too (the
    registers of an operand whose lanes run along it), "lane" for that
    lowercase (its lanes)
    """
    upper = {o.lower() for o in order if 1 == len(o) and o.isupper()}
    out = []
    for o in order:
        if 1 == len(o) and o.isupper():
            out.append((o.lower(), "reg"))
        elif o in upper:
            out.append((o, "lane"))
        else:
            out.append((o, None))
    return out


def generate_tiling(*,
                    order: tuple[str, ...],
                    counts: dict[str, int],
                    operands: dict[str, tuple[str | None, ...]],
                    offset: dict[str, int] | None = None,
                    tiles: dict[str, tile] | None = None,
                    io: dict[str, tuple[bool, bool]] | None = None,
                    lanes: dict[str, tuple[str, int]] | None = None,
                    opstr: str = "",
                    factors: dict[str, int] | None = None) -> list[operation]:
    """
    Every point of an iteration space, with each operand's coordinate

    :param order: indices of the iteration space, outermost first - an index
                  in two levels where its uppercase letter stands too (kNmn):
                  the uppercase the registers of an operand whose lanes run
                  along it, the lowercase the lanes within one (the old mm
                  generator's MmNnKk orders). Where no operand's lanes run
                  along the index (a store of C) the uppercase iterates once
                  and the lowercase the whole index, in its own place: kNmn
                  multiplies per B register, per A vector, per lane, and
                  stores C in kmn
    :param counts: number of extents along each index
    :param operands: each operand's indices, None for an axis it doesn't vary along
    :param offset: shift along indices by name, e.g. {"k": 1} for the same
                   operations one loop iteration later
    :param tiles: each operand's register tile
    :param io: each operand's (read, written); by default all read, the first
               written
    :param lanes: operands used one element at a time: the index the
                  register's lanes run along and how many it holds. Their
                  register offset along it is the element position divided by
                  the lane count, and the lane the remainder.
    :param opstr: name of the operation(s), for printing
    :return: the operations, in iteration order
    :raises ValueError: if an operand uses an index outside the iteration space
    """
    offset = offset or {}
    levels = split_levels(order)
    plain = [i for i, _ in levels]
    for name, indices in operands.items():
        stray = [i for i in indices if i is not None and i not in plain]
        if stray:
            raise ValueError(f"{name} varies along {stray}, outside {order}")

    names = list(operands)
    tiles = tiles or {}
    lanes = lanes or {}
    io = io or {n: (True, i == 0) for i, n in enumerate(names)}

    # an index's lane count: the lanes of an operand that runs them along it
    along = {}
    for axis, count in lanes.values():
        if axis is not None and count > 1:
            along[axis] = max(along.get(axis, 1), count)
    # or a register holding several of the index's extents (the STO's factors)
    for axis, count in (factors or {}).items():
        if count > 1:
            along[axis] = max(along.get(axis, 1), count)
    def span(index, level):
        lanes_along = along.get(index, 1)
        if level is None:
            return counts[index]
        if "reg" == level:
            return -(-counts[index] // lanes_along) if lanes_along > 1 else 1
        return lanes_along if lanes_along > 1 else counts[index]
    ops = []
    for position in itertools.product(*(range(span(i, lvl)) for i, lvl in levels)):
        point, regs = {}, {}
        for (i, lvl), p in zip(levels, position):
            if "reg" == lvl:
                regs[i] = p
            else:
                point[i] = p
        for i, r in regs.items():
            lanes_along = along.get(i, 1)
            point[i] = r * lanes_along + point[i] if lanes_along > 1 else point[i]
        if any(point[i] >= counts[i] for i in regs):
            continue                # a register past the index's count
        point = {i: p + offset.get(i, 0) for i, p in point.items()}
        offsets, lane_pos = [], []
        for name in names:
            axis, count = lanes.get(name, (None, 1))
            offs, lns = [], []
            for idx in operands[name]:
                pos = point[idx] if idx is not None else 0
                if idx is not None and idx == axis:
                    offs.append(pos // count)
                    lns.append(pos % count)
                else:
                    offs.append(pos)
                    lns.append(None)
            offs += [0] * (2 - len(offs))
            lns += [None] * (2 - len(lns))
            offsets.append(offs)
            lane_pos.append(lns)
        ops.append(operation(
            tiles=[tiles.get(n, tile(dima=_ONE, dimb=_ONE)) for n in names],
            tile_offsets=offsets,
            subindices=[],
            opstr=opstr,
            tile_strs=names,
            indices=[tuple(operands[n]) for n in names],
            io=[io[n] for n in names],
            lanes=lane_pos,
            point=point))
    return ops


# The compositions name a generator per STO; the names stay distinct so they can
# diverge (packing's zero padding of partial panels, say), but today they are
# one algorithm.
generators = {
    "mm": generate_tiling,
    "scale": generate_tiling,
    "pack": generate_tiling,
}
