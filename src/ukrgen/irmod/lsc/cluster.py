"""
Straight-line code's dependent instructions pulled together, before
addresses are fixed
"""

from ...schedulers.list_scheduler import cluster as cluster_order
from .base import irmod_placement, lsc_irmod


class cluster(lsc_irmod):
    """
    The model emits straight-line code STO after STO: gemm's epilogue loads
    every C tile, then scales them all, then combines and stores them - each
    tile's value live from its load to its store, all at once. Pulling each
    store's chain together - load C (its halves and inserts, in scratch of
    its own), scale, combine with its accumulator, store - before the next
    tile's is touched keeps a few tiles live at a time; the emitter renames
    the virtual registers onto the physical ones free, and the scheduler
    spreads the chains within a window. Before the specializer fixes
    addresses, which it then walks in this order
    """
    name = "cluster"
    description = "pull straight-line code's dependent instructions together (MRU)"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = True
    constraints = "straight-line blocks only; dependencies through registers kept"

    def apply(self, program) -> int:
        changed = 0
        for block in program.blocks + [b for c in program.cases for b in c.blocks]:
            if block.loop_index is not None or len(block.body) < 2:
                continue
            # a grouped register's members are the group, for dependencies
            order = cluster_order(list(block.body), getattr(program, "groups", None))
            if [id(op) for op in order] != [id(op) for op in block.body]:
                block.body = order
                changed += 1
        return changed
