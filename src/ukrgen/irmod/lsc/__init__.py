"""
IR modifications on LSC IR programs, one per module:

    lanefuse                lane loads fused into one load        before specialization
    structfuse              a trans case's row stores fused into
                            one interleaving store                before specialization
    shufflenet              a trans case's row stores as an in-
                            register transpose, stored contiguously before specialization
    tailmask                a vec case's last vector masked to a
                            run-time count, tail(<index>)        before specialization
    addrmerge               an address register's moves with
                            nothing between using it, one         after specialization
    ldinc                   address computations fused into
                            post-increment accesses               after specialization
    combine_load_transform  notes for an AVX modification: memory operands
                            in place of loads
"""

from .base import lsc_irmod, irmod_param, irmod_placement
from .lanefuse import lanefuse
from .ldinc import ldinc
from .addrmerge import addrmerge
from .widen import widen
from .structfuse import structfuse
from .shufflenet import shufflenet
from .tailmask import tailmask
from .hoist import hoist
from .vectorize import vectorize_loops
from .unroll import unroll_loops
from .slices import fuse_slices, forward_slices, hoist_slices
from .cluster import cluster

IRMODS : list[type[lsc_irmod]] = [widen, structfuse, shufflenet, tailmask, vectorize_loops, fuse_slices, forward_slices, hoist_slices,
                                  unroll_loops, hoist, cluster, lanefuse, addrmerge, ldinc]


def irmods_at(placement: irmod_placement) -> list[type[lsc_irmod]]:
    return [m for m in IRMODS if placement == m.placement]
