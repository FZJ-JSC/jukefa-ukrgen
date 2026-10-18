"""
Element loops into vector accesses
"""

from ...models.load_store_operations import (
    lsc_load, lsc_store, lsc_repeat, lsc_repeat_store,
)
from .base import irmod_placement, lsc_irmod, blocks_and_sections


def repeats(program):
    for block, section in blocks_and_sections(program):
        for op in getattr(block, section) or []:
            if isinstance(op, (lsc_repeat, lsc_repeat_store)):
                yield op


def vector_sigs(gen, op, dt):
    """
    The vector loads or stores doing what a loop over a vector's elements does:
    contiguous ones where the element stride is one, strided ones (with a
    stride register) otherwise
    """
    stride = dict(op.fill["stride"].terms) if op.fill.get("stride") is not None else {}
    contiguous = {(): 1} == stride
    move = gen.load if "load" == op.fill["direction"] else gen.store
    out = []
    for s in move.get_signatures():
        if dt != s.operands["adreg"].dt or s.operands["adreg"].modifiers:
            continue
        mods = {m.name for m in s.modifiers} - {"MASK"}
        if contiguous and mods <= {"IOFFSET", "VOFFSET"}:
            out.append(s)
        elif not contiguous and {"GSTRIDE"} == mods and "streg" in s.operands:
            out.append(s)
    return out


class vectorize_loops(lsc_irmod):
    """
    A loop over a vector's elements (vla_lanes) filling or draining it at an
    element stride is a strided vector access - RVV vlse/vsse - or, at stride
    one, a contiguous one. Where the ISA has those, this turns the loop into
    one: the fill information the loop records - component, index, element
    stride, direction - is all it needs.
    """
    name = "vectorize_loops"
    description = "turn loops over a vector's elements into strided or contiguous vector accesses"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = False
    constraints = "a vector load or store of each loop's element type, strided where its stride isn't one"

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        unmet = set()
        for program in ctx.programs:
            for op in repeats(program):
                dt = ctx.component_dts[op.fill["component"]]
                if not vector_sigs(ctx.gen, op, dt):
                    unmet.add(f"{op.fill['component']}: no vector {op.fill['direction']} of "
                              f"{dt.name} at stride {op.fill['stride']}")
        return sorted(unmet)

    def apply(self, program) -> int:
        changed = 0
        for op in list(repeats(program)):
            dt = self.ctx.component_dts[op.fill["component"]]
            sigs = vector_sigs(self.ctx.gen, op, dt)
            if not sigs:
                continue
            # the repeat already is a load or store of the vector from its
            # first element: it becomes a plain one, through these signatures
            op.__class__ = lsc_load if isinstance(op, lsc_repeat) else lsc_store
            op.sigs = sigs
            if any("GSTRIDE" in {m.name for m in s.modifiers} for s in sigs):
                op.add_property("stride_index", op.fill["index"])
            changed += 1
        return changed
