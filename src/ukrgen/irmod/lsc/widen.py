"""
Widening: operations on narrow elements accumulating into wide ones
"""

import copy

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_load, lsc_store, lsc_transformation
from ...support.tiles import widening_ways
from .base import irmod_placement, lsc_irmod, blocks_and_sections

#: the widening methods this modification carries out
IMPLEMENTED = {"SPLIT_CONTIGUOUS"}


def _sig(op):
    return op.resolution.compute_sg.representative


def widening_ops(program):
    for block, section in blocks_and_sections(program):
        for op in getattr(block, section) or []:
            if isinstance(op, lsc_transformation) and widening_ways(_sig(op)) > 1:
                yield op


def _narrow(sig) -> int:
    return min(adt_size(o.dt) for o in sig.operands.values()
               if rgt.VEC == o.rtype and getattr(o, "dt", None) is not None)


class widen(lsc_irmod):
    """
    The model counts a wide register as a group of them, as many as a narrow
    register's elements take, so a widening operation reaches as far as its
    narrow registers. This carries the groups out by the ISA's widening method
    (its signatures' widening_method):

    - SPLIT_CONTIGUOUS (NEON fmlal/fmlal2): one instruction per member p of the
      group, computing part p - a contiguous run of the elements; every other
      operation on the group, member by member, member p's memory a run of
      elements on from member p - 1's

    Required wherever an operation widens; runs on the model's IR, before
    specialization gives each access an address of its own.
    """
    name = "widen"
    description = "carry out widening operations by the ISA's widening method"
    placement = irmod_placement.PRE_SPECIALIZE
    required = True
    constraints = ("every widening operation's signatures take each part of the wide result, "
                   "by a widening method implemented here")

    @classmethod
    def triggered(cls, ctx) -> bool:
        return any(True for p in ctx.programs for _ in widening_ops(p))

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        unmet = set()
        for program in ctx.programs:
            for op in widening_ops(program):
                sig = _sig(op)
                method = sig.structural_params["widening_method"].name
                ways = widening_ways(sig)
                if method not in IMPLEMENTED:
                    unmet.add(f"{op.op}: widening by {method} is not implemented yet")
                    continue
                shape = sig.operands.get("part")
                if shape is None:
                    unmet.add(f"{op.op}: its {method} signature takes no part")
                    continue
                for cons in shape.value_constraints:
                    if getattr(cons, "maxval", ways - 1) < ways - 1 or getattr(cons, "minval", 0) > 0:
                        unmet.add(f"{op.op}: its signature doesn't take every part of {ways}")
                if ctx.gen.is_vla:
                    unmet.add(f"{op.op}: contiguous parts of a vector-length agnostic register")
        return sorted(unmet)

    def apply(self, program) -> int:
        wide: dict[str, int] = {}
        for op in widening_ops(program):
            sig, ways = _sig(op), widening_ways(_sig(op))
            narrow = _narrow(sig)
            for hw, idx in zip(op.hw_operands, op.indices):
                shape = sig.operands[hw]
                if rgt.VEC == shape.rtype and adt_size(shape.dt) > narrow:
                    wide[idx.component] = ways
        changed = 0
        for block, section in blocks_and_sections(program):
            ops = getattr(block, section) or []
            out = []
            for op in ops:
                at = [j for j, idx in enumerate(op.indices)
                      if idx.component in wide and rgt.VEC == op.rtypes[j]]
                if not at:
                    out.append(op)
                    continue
                ways = wide[op.indices[at[0]].component]
                widening = isinstance(op, lsc_transformation) and widening_ways(_sig(op)) > 1
                for part in range(ways):
                    member = copy.deepcopy(op)
                    for j in at:
                        member.indices[j].indices[0] = member.indices[j].indices[0] * ways + part
                    if widening:
                        member.add_property("part", part)
                    if isinstance(member, (lsc_load, lsc_store)) and part:
                        member.offset = self.member_offset(program, member, part)
                    out.append(member)
                changed += 1
            setattr(block, section, out)
        return changed

    def member_offset(self, program, op, part):
        """
        Where member part of a group sits: part registers' elements on along
        the component's vector index - a new offset record
        """
        comp = op.indices[0].component
        elements = self.ctx.gen.simd_size // adt_size(self.ctx.component_dts[comp])
        return program.offsets.shifted(op.offset, program.vector_indices[comp],
                                       sym.const(part * elements))
