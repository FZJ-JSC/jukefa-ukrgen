"""
Widening: operations on narrow elements accumulating into wide ones
"""

import copy

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_load, lsc_store, lsc_transformation, lsc_zero, lsc_loop
from ...support.tiles import widening_ways
from .base import irmod_placement, lsc_irmod, blocks_and_sections

#: the widening methods this modification carries out
IMPLEMENTED = {"SPLIT_CONTIGUOUS", "SPLIT_INTERLEAVED", "VEC_GROUP"}


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


def struct_sigs(gen, op: str, dt, ways: int) -> list:
    """
    A load's or store's signatures moving ways registers interleaved: element
    e of register p at memory element ways * e + p (ld2/st2 and the like)
    """
    return [s for s in getattr(gen, op).get_signatures()
            if "STRUCT" in {m.name for m in s.modifiers}
            and ways == s.structural_params.get("nstructs")
            and dt == s.operands["adreg"].dt]


def wide_components(ctx, program) -> dict[str, tuple[int, str]]:
    """
    The components a program widens into: how many registers a group of them
    takes, by which method
    """
    sizes = {}
    for op in widening_ops(program):
        sig = _sig(op)
        narrow = _narrow(sig)
        for o in sig.operands.values():
            if rgt.VEC == o.rtype and adt_size(o.dt) > narrow:
                sizes[adt_size(o.dt)] = (widening_ways(sig), sig.structural_params["widening_method"].name)
    # every component with vector registers of a widened type: the model
    # counted them as groups, in the plain chains too
    wide = {}
    for block, section in blocks_and_sections(program):
        for op in getattr(block, section) or []:
            for idx, rtype in zip(op.indices, op.rtypes):
                dt = ctx.component_dts.get(idx.component)
                if rgt.VEC == rtype and dt is not None and adt_size(dt) in sizes:
                    wide[idx.component] = sizes[adt_size(dt)]
    return wide


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
    - SPLIT_INTERLEAVED (SVE fmlalb/fmlalt): one instruction per member p,
      computing part p - every ways-th element from p. Operations within
      registers, member by member; the group's loads and stores interleave
      its members: structure loads and stores (ld2w/st2w)
    - VEC_GROUP (RVV vfwmacc): one instruction for the whole group, its first
      register named; loads and stores likewise (a wide element type makes
      them reach the group); zeroing member by member; other arithmetic on the
      group in the group's element type, which the emitter switches to

    Where offsets in vector lengths count vectors of each component's own
    type (SVE), a wide component's offsets stretch to whole groups here; RVV's
    vl counts elements alike for every type and needs none.

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
                if "VEC_GROUP" == method:
                    continue
                shape = sig.operands.get("part")
                if shape is None:
                    unmet.add(f"{op.op}: its {method} signature takes no part")
                    continue
                for cons in shape.value_constraints:
                    if getattr(cons, "maxval", ways - 1) < ways - 1 or getattr(cons, "minval", 0) > 0:
                        unmet.add(f"{op.op}: its signature doesn't take every part of {ways}")
                if "SPLIT_CONTIGUOUS" == method and ctx.gen.is_vla:
                    unmet.add(f"{op.op}: contiguous parts of a vector-length agnostic register")
            for comp, (ways, method) in wide_components(ctx, program).items():
                dt = ctx.component_dts[comp]
                if "SPLIT_INTERLEAVED" == method:
                    for move in ("load", "store"):
                        if not struct_sigs(ctx.gen, move, dt, ways):
                            unmet.add(f"{comp}: no {move} interleaving {ways} {dt.name} registers")
                if "VEC_GROUP" == method and not hasattr(ctx.gen, "vsetvli_keep_vl"):
                    unmet.add(f"{comp}: no way to switch to the group's element type")
        return sorted(unmet)

    @property
    def per_type_vl(self) -> bool:
        """
        Whether offsets in vector lengths count vectors of each component's
        own type (SVE: MUL VL, incb). RVV's vl counts elements, the same for
        every type: a group of wide registers is one vl of wide elements
        already
        """
        gen = self.ctx.gen
        if not gen.is_vla:
            return False
        predication = getattr(gen.isa_setup(), "predication", None)
        return predication is None or "IMPLICIT" != predication().name

    def apply(self, program) -> int:
        wide = wide_components(self.ctx, program)
        program.groups.update(wide)
        gen = self.ctx.gen
        changed = 0
        for block, section in blocks_and_sections(program):
            out = []
            for op in getattr(block, section) or []:
                if isinstance(op, lsc_loop):
                    out.append(op)
                    continue
                at = [j for j, idx in enumerate(op.indices)
                      if idx.component in wide and rgt.VEC == op.rtypes[j]]
                if not at:
                    out.append(op)
                    continue
                ways, method = wide[op.indices[at[0]].component]
                memory = isinstance(op, (lsc_load, lsc_store))
                if memory and self.per_type_vl:
                    # offsets counted in the component's own vectors: groups
                    op.offset = self.stretched(program, op, ways)
                widening = isinstance(op, lsc_transformation) and widening_ways(_sig(op)) > 1
                # a broadcast (alpha, beta) has no vector index: the same value in
                # every member, not elements to interleave
                along = memory and program.vector_indices.get(op.indices[0].component) is not None
                whole = ("VEC_GROUP" == method and not isinstance(op, lsc_zero)) or \
                    ("SPLIT_INTERLEAVED" == method and along)
                if whole:
                    # one operation for the group, its first register named
                    for j in at:
                        op.indices[j].indices[0] = op.indices[j].indices[0] * ways
                    op.add_property("group", ways)
                    if "SPLIT_INTERLEAVED" == method:
                        comp = op.indices[0].component
                        op.sigs = struct_sigs(gen, "load" if isinstance(op, lsc_load) else "store",
                                              self.ctx.component_dts[comp], ways)
                    out.append(op)
                    changed += 1
                    continue
                for part in range(ways):
                    member = copy.deepcopy(op)
                    for j in at:
                        member.indices[j].indices[0] = member.indices[j].indices[0] * ways + part
                    if widening:
                        member.add_property("part", part)
                    if memory and part and program.vector_indices.get(member.indices[0].component):
                        # a broadcast (alpha, beta) is the same in every member
                        member.offset = self.member_offset(program, member, part)
                    out.append(member)
                changed += 1
            setattr(block, section, out)
        return changed

    def stretched(self, program, op, ways):
        """
        A wide access's offset with its vector index's elements scaled to
        whole groups
        """
        comp = op.indices[0].component
        vidx = program.vector_indices.get(comp)
        if vidx is None:
            # a broadcast: no index to stretch along
            return op.offset
        record = program.offsets[op.offset]
        elements = {}
        for idx, e in record.elements:
            if idx == vidx:
                total = e
                for _ in range(ways - 1):
                    total = total + e
                e = total
            elements[idx] = e
        return program.offsets.add(comp, elements)

    def member_offset(self, program, op, part):
        """
        Where member part of a group sits: part registers' elements on along
        the component's vector index - a new offset record
        """
        comp = op.indices[0].component
        elements = self.ctx.gen.simd_size // adt_size(self.ctx.component_dts[comp])
        return program.offsets.shifted(op.offset, program.vector_indices[comp],
                                       sym.const(part * elements))
