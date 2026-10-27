"""
shufflenet: a trans case's row stores as an in-register transpose, stored
contiguously
"""
from __future__ import annotations

import copy

from asmgen.asmblocks.op import register_type as rgt, opmem_modifier as memmod
from asmgen.asmblocks.op.opmove import opmove_modifier as mvmod
from asmgen.registers import adt_size

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_permute, lsc_store
from ...models.lsc.index import lsc_reg_index
from ...support.transpose import transpose_network
from .base import lsc_irmod, irmod_placement, blocks_and_sections
from .structfuse import runs, _record


def plain_store_sigs(gen, dt) -> list:
    """a vector register stored at an address and an immediate: no structures, scatters, masks"""
    return [s for s in gen.store.forms(rtypes={"adreg": rgt.VEC}, dts={"adreg": dt})
            if set(s.modifiers) <= {memmod.IOFFSET}
            and not any(shape.modifiers for shape in s.operands.values())]


def _data_indices(program, comp: str) -> set[int]:
    """the component's data registers any operation names"""
    used = set()
    for block in program.blocks + [b for c in program.cases for b in c.blocks]:
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            for op in getattr(block, section) or []:
                for idx, rtype in zip(op.indices, op.rtypes or [None] * len(op.indices)):
                    if comp == idx.component and rtype is not None:
                        used.add(idx.indices[0])
    return used


class shufflenet(lsc_irmod):
    """
    A panel packed across the grain - packm's trans case - stores each row's
    vector into the panel cdim elements apart: a scatter (AVX-512, SVE), a
    strided store (RVV), or nothing at all (AVX2, NEON). Where the vector's
    length is fixed, a block of as many rows as it has lanes is transposed
    in registers instead - rounds of the ISA's permutes (support/transpose:
    AVX-512's doubles in 3, AMD's zen4 network; AVX2's in 2; NEON's in 1) -
    and its columns stored contiguously, each where its first element goes:
    rows lanes, 2*lanes, ... a step. The network runs in place, one more
    register than the rows: each pair's first result into the spare, its
    second over the pair's second row, the first row's register the spare
    after.
    """
    name = "shufflenet"
    description = "a trans case's row stores as an in-register transpose, stored contiguously"
    placement = irmod_placement.PRE_SPECIALIZE
    # what the shuffle store resolution stands for: run wherever it's chosen
    required = True
    constraints = ("a vector of fixed length; a step's rows stored strided along the panel, "
                   "consecutive registers, as many as the vector's lanes or a multiple; "
                   "one data register more than the rows")

    @classmethod
    def triggered(cls, ctx) -> bool:
        return any("shuffle" == op.rsln for p in ctx.programs for block, section in blocks_and_sections(p)
                   for op in getattr(block, section) or [] if isinstance(op, lsc_store))

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        if ctx.gen.is_vla:
            return ["the vector's length isn't known when generating: no fixed transpose"]
        if not ctx.gen.move.forms(modifiers={mvmod.PERMUTE}):
            return [f"{type(ctx.gen).__name__} has no permutes"]
        return []

    def apply(self, program) -> int:
        gen = self.ctx.gen
        changed = 0
        for block, section in blocks_and_sections(program):
            ops = list(getattr(block, section) or [])
            replace, dropped = {}, set()
            for members, n, comp in runs(program, ops):
                dt = self.ctx.component_dts[comp]
                lanes = gen.simd_size // adt_size(dt)
                net = transpose_network(gen, dt)
                sigs = plain_store_sigs(gen, dt)
                if net is None or not sigs or n % lanes:
                    continue
                vector_index = program.vector_indices.get(comp)
                spare = 1 + max(_data_indices(program, comp))
                ref = lambda i: lsc_reg_index(comp, [i])
                new_ops = []
                for t in range(n // lanes):
                    rows = [ops[members[t * lanes + i]] for i in range(lanes)]
                    regs = [r.indices[1].indices[0] for r in rows]
                    tile, vec = rows[0].tiles[1], [rgt.VEC] * 3
                    for rnd in net.rounds:
                        for i in range(lanes):
                            j = i ^ rnd.distance
                            if i < j:
                                a, b = regs[i], regs[j]
                                new_ops.append(lsc_permute(ref(a), ref(b), ref(spare), [tile] * 3,
                                                           sig=rnd.first, rtypes=vec))
                                new_ops.append(lsc_permute(ref(a), ref(b), ref(b), [tile] * 3,
                                                           sig=rnd.second, rtypes=vec))
                                regs[i], spare = spare, a
                    base = dict(_record(program, rows[0]).elements)
                    for c in range(lanes):
                        st = copy.deepcopy(rows[0])
                        st.indices = [st.indices[0], ref(regs[net.columns[c]])]
                        elements = dict(base)
                        elements[vector_index] = sym.of(elements.get(vector_index, sym())) + sym.const(c)
                        st.offset = program.offsets.add(comp, elements)
                        st.properties.pop("stride_index", None)
                        st.rsln = "shufflenet"
                        st.sigs = sigs
                        new_ops.append(st)
                replace[members[0]] = new_ops
                dropped.update(members[1:])
            if replace:
                out = []
                for k, op in enumerate(ops):
                    if k in replace:
                        out += replace[k]
                    elif k not in dropped:
                        out.append(op)
                setattr(block, section, out)
                changed += len(replace)
        return changed
