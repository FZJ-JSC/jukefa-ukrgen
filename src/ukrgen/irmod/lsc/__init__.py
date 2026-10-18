"""
IR modifications on LSC IR programs, one per module:

    lanefuse                lane loads fused into one load        before specialization
    ldinc                   address computations fused into
                            post-increment accesses               after specialization
    combine_load_transform  notes for an AVX modification: memory operands
                            in place of loads
"""

from .base import lsc_irmod, irmod_param, irmod_placement
from .lanefuse import lanefuse
from .ldinc import ldinc
from .widen import widen
from .hoist import hoist
from .vectorize import vectorize_loops
from .unroll import unroll_loops

IRMODS : list[type[lsc_irmod]] = [widen, vectorize_loops, unroll_loops, hoist, lanefuse, ldinc]


def irmods_at(placement: irmod_placement) -> list[type[lsc_irmod]]:
    return [m for m in IRMODS if placement == m.placement]
