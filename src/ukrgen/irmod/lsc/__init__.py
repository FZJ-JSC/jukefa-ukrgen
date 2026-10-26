"""
IR modifications on LSC IR programs, one per module:

    lanefuse                lane loads fused into one load        before specialization
    structfuse              a trans case's row stores fused into
                            one interleaving store                before specialization
    ldinc                   address computations fused into
                            post-increment accesses               after specialization
    combine_load_transform  notes for an AVX modification: memory operands
                            in place of loads
"""

from .base import lsc_irmod, irmod_param, irmod_placement
from .lanefuse import lanefuse
from .ldinc import ldinc
from .widen import widen
from .structfuse import structfuse
from .hoist import hoist
from .vectorize import vectorize_loops
from .unroll import unroll_loops
from .slices import fuse_slices, forward_slices, hoist_slices
from .cluster import cluster

IRMODS : list[type[lsc_irmod]] = [widen, structfuse, vectorize_loops, fuse_slices, forward_slices, hoist_slices,
                                  unroll_loops, hoist, cluster, lanefuse, ldinc]


def irmods_at(placement: irmod_placement) -> list[type[lsc_irmod]]:
    return [m for m in IRMODS if placement == m.placement]
