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
from dataclasses import dataclass


@dataclass(frozen=True)
class tile_op:
    """
    One execution of an STO's implementation

    :param point: position along each index of the iteration space, in units of
                  the index's extent
    :param coords: each operand's position along its own indices
    """
    point : tuple[tuple[str, int], ...]
    coords : tuple[tuple[str, tuple[int, ...]], ...]

    def at(self, index: str) -> int:
        """
        Position of the operation along an index
        """
        return dict(self.point)[index]

    def coord(self, operand: str) -> tuple[int, ...]:
        """
        Position of an operand's tile in this operation
        """
        return dict(self.coords)[operand]

    def __str__(self):
        point = " ".join(f"{i}={p}" for i, p in self.point)
        coords = " ".join(f"{o}({','.join(map(str, c))})" for o, c in self.coords)
        return f"[{point}]  {coords}"


def generate_tiling(*,
                    order: tuple[str, ...],
                    counts: dict[str, int],
                    operands: dict[str, tuple[str | None, ...]],
                    offset: dict[str, int] | None = None) -> list[tile_op]:
    """
    Every point of an iteration space, with each operand's coordinate

    :param order: indices of the iteration space, outermost first
    :param counts: number of extents along each index
    :param operands: each operand's indices, None for an axis it doesn't vary along
    :param offset: shift along indices by name, e.g. {"k": 1} for the same
                   operations one loop iteration later
    :return: the operations, in iteration order
    :raises ValueError: if an operand uses an index outside the iteration space
    """
    offset = offset or {}
    for name, indices in operands.items():
        stray = [i for i in indices if i is not None and i not in order]
        if stray:
            raise ValueError(f"{name} varies along {stray}, outside {order}")

    ops = []
    for position in itertools.product(*(range(counts[i]) for i in order)):
        point = {i: p + offset.get(i, 0) for i, p in zip(order, position)}
        coords = tuple((name, tuple(point[i] for i in indices if i is not None))
                       for name, indices in operands.items())
        ops.append(tile_op(point=tuple(point.items()), coords=coords))
    return ops


# The compositions name a generator per STO; the names stay distinct so they can
# diverge (packing's zero padding of partial panels, say), but today they are
# one algorithm.
generators = {
    "mm": generate_tiling,
    "scale": generate_tiling,
    "pack": generate_tiling,
}
