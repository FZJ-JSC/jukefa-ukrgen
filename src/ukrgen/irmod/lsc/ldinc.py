"""
ldinc: address computations fused into post-increment accesses
"""

from __future__ import annotations

from asmgen.registers import adt_size

from ...models.load_store_operations import (
    lsc_load, lsc_store, lsc_addr_compute, ldst_modifier)
from ...models.lsc.reg import lsc_reg_type
from ...lsc_model.addressing import sym
from ...specializers.signature import _sigs, _masked, _accepts
from .base import lsc_irmod, irmod_placement, blocks_and_sections


class ldinc(lsc_irmod):
    """
    Specializing leaves an access at an offset no signature takes behind an
    address computation into a scratch register: s = a + c, then the access
    through s. When the next such pair sets s from the same register, and the
    previous access has a signature post-incrementing by the distance between
    the two, that access becomes a post-increment and the next computation
    goes - the chain walks s: ld1r {v.2d}, [x], #8 instead of a mov and an add
    before every load. A post-incremented access writes its address register,
    so the schedulers see the dependency.
    """

    name = "ldinc"
    description = "fuse address computations into post-increment accesses"
    placement = irmod_placement.POST_SPECIALIZE
    constraints = ("consecutive accesses through one scratch address register set from "
                   "the same source, the distance between them a post-increment one of "
                   "the earlier access's signatures takes - where a signature states no "
                   "constraint on the increment, only the access's transfer size")

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        for op in ("load", "store"):
            if any("POSTINC" in {m.name for m in s.modifiers}
                   for s in getattr(ctx.gen, op).get_signatures()):
                return []
        return ["post-increment load or store signatures"]

    def transfer_size(self, op) -> int | None:
        """
        Bytes an access moves: one element for a broadcast or a lane, a vector
        otherwise; None where vectors have no fixed size
        """
        esize = adt_size(self.ctx.component_dts[op.indices[0].component])
        if ldst_modifier.bcast1 in op.mods or ldst_modifier.lane in op.mods:
            return esize
        return None if self.ctx.gen.is_vla else self.ctx.gen.simd_size

    def check(self, op, increment: int) -> bool:
        """
        Whether one of an access's signatures post-increments its address
        register by this many bytes. asmgen's NEON signatures don't constrain
        the increment, though AArch64's structure loads (ld1r, ld1) only take
        their transfer size while ldr takes a range: without a stated
        constraint only the transfer size is assumed.
        """
        for sig in _sigs(op.sigs):
            if _masked(sig) or {m.name for m in sig.modifiers} - {"MASK"} != {"POSTINC"}:
                continue
            shape = sig.operands.get("iinc")
            if shape is None:
                continue
            if not shape.value_constraints:
                # unconstrained in asmgen: read conservatively as the
                # transfer size, what every post-increment form takes
                if increment == self.transfer_size(op):
                    return True
                continue
            if _accepts(sig, "iinc", increment):
                return True
        return False

    @staticmethod
    def post_increment(op, elements: int):
        op.increment = sym.const(elements)
        op.mods.add(ldst_modifier.postinc)
        if 0 not in op.writes:
            op.writes = sorted(op.writes + [0])

    def fuse(self, ops: list) -> tuple[list, int]:
        out, fused = [], 0
        chains: dict[tuple, tuple] = {}
        i = 0
        while i < len(ops):
            op = ops[i]
            nxt = ops[i + 1] if i + 1 < len(ops) else None
            if isinstance(op, lsc_addr_compute) and isinstance(nxt, (lsc_load, lsc_store)) \
                    and set(dict(op.delta.terms)) <= {()} \
                    and nxt.indices[0].indices == op.indices[1].indices \
                    and nxt.indices[0].component == op.indices[1].component:
                comp = op.indices[0].component
                key = (comp, op.indices[1].indices[0])
                src = op.indices[0].indices[0]
                offset = dict(op.delta.terms).get((), 0)
                prev = chains.get(key)
                if prev is not None and prev[2] == src:
                    gap = offset - prev[1]
                    if self.check(prev[0], gap * adt_size(self.ctx.component_dts[comp])):
                        self.post_increment(prev[0], gap)
                        out.append(nxt)
                        chains[key] = (nxt, offset, src)
                        fused += 1
                        i += 2
                        continue
                out += [op, nxt]
                chains[key] = (nxt, offset, src)
                i += 2
                continue
            # anything else using a chained address register ends its chain
            for pos, idx in enumerate(op.indices):
                if lsc_reg_type.address == op.reg_types[pos]:
                    chains.pop((idx.component, idx.indices[0]), None)
            out.append(op)
            i += 1
        return out, fused

    def apply(self, program) -> int:
        total = 0
        for block, section in blocks_and_sections(program):
            ops, fused = self.fuse(getattr(block, section))
            setattr(block, section, ops)
            total += fused
        return total
