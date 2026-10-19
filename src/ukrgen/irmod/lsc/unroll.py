"""
Unrolling loops over a vector's elements
"""

from dataclasses import replace

from asmgen.registers import adt_size

from .base import irmod_param, irmod_placement, lsc_irmod
from .vectorize import repeats
from .base import blocks_and_sections
from ...models.load_store_operations import lsc_loop
from ...support.domains import operand_values



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
                                      "the loop's divisor, up to this"),
              irmod_param(name="registers", default=1, parse=int,
                          description="registers an iteration's scalars rotate through "
                                      "(up to its elements): scalar loads and stores in "
                                      "flight together")]
    constraints = "the factor divides the element count, which is a multiple of the divisor"

    def apply(self, program) -> int:
        want = max(1, int(self.values["factor"]))
        changed = 0
        for op in list(repeats(program)) + list(slice_loops(program)):
            if op.info.get("explicit"):
                # set for this component (--COMP-subtiling): left as set
                continue
            # a vector holds a multiple of 16 bytes: the factors keeping the
            # count whole - and, over slices, every slice operand's immediate
            # taking an unrolled iteration's slices
            dt = self.ctx.component_dts[op.info["component"]]
            factors = [f for f in op.subtiling.count.count_unrolls(16 // adt_size(dt)) if f <= want]
            if "slices" == op.info.get("kind"):
                factors = [f for f in factors if immediates_take(op, f)]
            factor = max(factors, default=1)
            if factor > 1:
                op.subtiling = replace(op.subtiling, unroll=factor,
                                       registers=max(1, min(int(self.values["registers"]), factor)))
                changed += 1
        return changed


def slice_loops(program):
    for block, section in blocks_and_sections(program):
        for op in getattr(block, section) or []:
            if isinstance(op, lsc_loop) and "slices" == op.info.get("kind"):
                yield op


def immediates_take(loop, factor: int) -> bool:
    """
    Whether every slice operand of a loop's operations takes the immediates
    an unrolled iteration's slices need, 0 to factor-1, in some signature
    """
    for b in loop.block:
        sigs = getattr(b, "sigs", None)
        if sigs is None:
            continue
        names = {n for s in _sigs(sigs) for n in s.operands if n.endswith(("_immrow", "_immcol"))}
        if names and not any(all(i in operand_values(s, n) for i in range(factor))
                             for s in _sigs(sigs) for n in s.operands if n in names):
            return False
    return True


def _sigs(groups) -> list:
    """
    The signatures in a signature group, or in a list of groups
    """
    if groups is None:
        return []
    if isinstance(groups, list):
        return [s for g in groups for s in _sigs(g)]
    for attr in ("sigs", "members", "signatures"):
        if hasattr(groups, attr):
            return list(getattr(groups, attr))
    return [getattr(groups, "representative", groups)]
