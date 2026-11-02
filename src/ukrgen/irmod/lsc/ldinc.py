"""
ldinc: address computations fused into post-increment accesses
"""

from __future__ import annotations

from typing import ClassVar

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
    #: run on the moves spelled as steps (the post-specialize stage's finish):
    #: a walk's step one add of a stride, fusable as a register increment
    on_steps : ClassVar[bool] = True
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

    def check_reg(self, op) -> bool:
        """
        Whether one of an access's signatures post-increments its address
        register by a register (AArch64's ld1 {v}, [x0], x1)
        """
        # the access's own forms (a lane store's, not a whole vector's)
        for sig in _sigs(op.sigs):
            mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
            if {"POSTINC"} == mods and "increg" in sig.operands:
                return True
        return False

    @staticmethod
    def post_increment(op, increment):
        """
        An access post-incrementing its address register: by elements, or by
        a polynomial of them (a stride's register, an offset's) - the access
        writes the register too, so the scheduler keeps the register's other
        accesses in order around it
        """
        op.increment = increment if isinstance(increment, sym) else sym.const(increment)
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
            terms = dict(op.delta.terms) if isinstance(op, lsc_addr_compute) else {}
            # a walk's step adding a planned offset's register (cs - 3 rs): a
            # register increment by it, its spelling kept for where the
            # register was given up
            st = (op.properties or {}).get("step") if isinstance(op, lsc_addr_compute) else None
            by_offset = st is not None and "offset" == st[0]
            # a walk's step by one stride: a register increment (spelled steps)
            by_stride = 1 == len(terms) and all(len(f) == 1 and f[0].startswith("stride(") and 1 == c
                                                for f, c in terms.items())
            if isinstance(op, lsc_addr_compute) and isinstance(nxt, (lsc_load, lsc_store)) \
                    and (set(terms) <= {()} or by_stride or by_offset) \
                    and nxt.indices[0].indices == op.indices[1].indices \
                    and nxt.indices[0].component == op.indices[1].component:
                comp = op.indices[0].component
                key = (comp, op.indices[1].indices[0])
                src = op.indices[0].indices[0]
                offset = None if by_stride or by_offset else dict(op.delta.terms).get((), 0)
                prev = chains.get(key)
                # a walk (a = a + c) moves by its own delta: that is the
                # increment; a scratch computation (s = a + c) by the distance
                # from the previous one
                walk = op.indices[0].indices == op.indices[1].indices
                if not walk:
                    # it reads its source register: that one's chain ends here
                    # (a0's next step fused before this copy from a0 moved it)
                    chains.pop((comp, src), None)
                # only an access at its register exactly post-increments: an
                # immediate (ldr q's) can't be the same instruction's
                at_reg = prev is not None and (prev[0].properties or {}).get("at_register")
                # a walk's step: the register's previous access, however the
                # register was set (from another: x0 = x3 + 16), nothing else
                # having used it since
                if prev is not None and (walk or prev[2] == src) and (by_stride or by_offset):
                    if walk and at_reg and self.check_reg(prev[0]):
                        self.post_increment(prev[0], op.delta)
                        if by_offset:
                            prev[0].properties["increment_step"] = st
                        out.append(nxt)
                        chains[key] = (nxt, None, src)
                        fused += 1
                        i += 2
                        continue
                elif prev is not None and prev[2] == src and at_reg and (walk or prev[1] is not None):
                    gap = offset if walk else offset - prev[1]
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
