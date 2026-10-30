"""
addrmerge: an address register's moves with nothing between using it, one
"""
from __future__ import annotations

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_addr_compute, lsc_loop
from .base import lsc_irmod, irmod_placement, blocks_and_sections


def _key(idx) -> tuple:
    return idx.component, tuple(idx.indices)


def _in_place(op) -> bool:
    """an address register moved by a delta: dest = src + delta, the same register"""
    return isinstance(op, lsc_addr_compute) and _key(op.indices[0]) == _key(op.indices[1])


def _sym(delta) -> sym:
    return sym.const(delta) if isinstance(delta, int) else delta


def _constant(delta) -> bool:
    """a number of elements: no vector lengths, no run-time strides"""
    return all(() == factors for factors, _ in _sym(delta).terms)


def _vectors(delta) -> bool:
    """a number of vector lengths: VL its only factor - no constant, no stride"""
    return all(("VL",) == factors for factors, _ in _sym(delta).terms)


def _addresses(op) -> set[str]:
    """
    The components whose address registers an operation names - its indices
    without a register type (a load's or store's address, an address
    computation's registers), not its data registers'
    """
    rtypes = op.rtypes or [None] * len(op.indices)
    return {idx.component for idx, rt in zip(op.indices, rtypes) if rt is None}


class addrmerge(lsc_irmod):
    """
    An address register moved twice by a number of elements with nothing
    between using the component's addresses - a loop's last iteration
    advancing as every iteration does, then moving back the step it
    preloads no more (add $128, then add $-32) - moves once, by the sum; a
    move that comes to nothing, and moves no iteration on, goes. The advances
    (a loop's move to its next iteration, which offsets within an iteration
    don't count) add up the same, so every access's offset stays.
    Conservative: any access through any of the component's address
    registers between - the emitter derives some from others (C's columns) -
    keeps the moves apart. Moves by vector lengths merge where the ISA adds
    them as immediates (SVE's, SME's incb, decb, addvl: a section's walk
    moved back and the loop's advance, -8 and +8 vector lengths, nothing);
    not RVV's (in registers, a sum perhaps one more), nor moves by strides,
    nor a constant with vector lengths (a polynomial: a register's). Nor
    anything across sections, loops or labels.
    """
    name = "addrmerge"
    description = "an address register's moves with nothing between using it merged into one"
    placement = irmod_placement.POST_SPECIALIZE
    constraints = ("moves of one address register in place, in one section, nothing naming "
                   "the register between them")

    def apply(self, program) -> int:
        from ...emitters.asmops import adds_vectors
        vectors = adds_vectors(self.ctx.gen)
        mergeable = lambda delta: _constant(delta) or (vectors and _vectors(delta))
        changed = 0
        for block, section in blocks_and_sections(program):
            ops = list(getattr(block, section) or [])
            out, pending, merged = [], {}, 0
            for op in ops:
                if isinstance(op, lsc_loop):
                    pending.clear()
                    out.append(op)
                    continue
                if _in_place(op) and mergeable(op.delta):
                    key = _key(op.indices[0])
                    if key in pending and _constant(out[pending[key]].delta) == _constant(op.delta):
                        first = out[pending[key]]
                        first.delta = _sym(first.delta) + _sym(op.delta)
                        advances = [a for a in (first.properties.get("advance"),
                                                op.properties.get("advance")) if a is not None]
                        if advances:
                            total = advances[0]
                            for a in advances[1:]:
                                total = total + a
                            first.properties["advance"] = total
                        merged += 1
                        continue
                    pending[key] = len(out)
                    out.append(op)
                    continue
                if _in_place(op):
                    # a move by vector lengths or strides: not merged, the
                    # register's own moves apart
                    pending.pop(_key(op.indices[0]), None)
                else:
                    for comp in _addresses(op):
                        for key in [k for k in pending if comp == k[0]]:
                            del pending[key]
                out.append(op)
            kept = [op for op in out if not (_in_place(op) and _sym(op.delta).is_zero()
                                              and op.properties.get("advance") is None)]
            merged += len(out) - len(kept)
            if merged:
                setattr(block, section, kept)
                changed += merged
        return changed
