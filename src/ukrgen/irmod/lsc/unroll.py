"""
Unrolling loops over a vector's elements
"""

from .base import irmod_param, irmod_placement, lsc_irmod
from .vectorize import repeats


class unroll_loops(lsc_irmod):
    """
    A loop over a vector's elements runs as many times as the vector has
    elements, a multiple of its divisor (16 bytes in elements: SVE's vector
    length is a multiple of 128 bits, RVV's V extension has VLEN >= 128). It
    unrolls by any of the divisor's divisors: each iteration takes that many
    elements, the count stepping down by as many
    """
    name = "unroll_loops"
    description = "unroll loops over a vector's elements"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = False
    params = [irmod_param(name="factor", default=2, parse=int,
                          description="elements a loop iteration takes: the largest dividing "
                                      "the loop's divisor, up to this")]
    constraints = "the factor divides the element count, which is a multiple of the divisor"

    def apply(self, program) -> int:
        want = max(1, int(self.values["factor"]))
        changed = 0
        for op in repeats(program):
            factor = max(f for f in range(1, want + 1) if 0 == op.divisor % f)
            if factor > 1:
                op.unroll = factor
                changed += 1
        return changed
