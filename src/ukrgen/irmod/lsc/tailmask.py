"""
tailmask: a kernel's last vector along an index masked to a run-time count
"""
from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt
from asmgen.asmblocks.op.opset import opset_modifier

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_load, lsc_store
from .base import lsc_irmod, irmod_placement, blocks_and_sections


def _vectors(offset) -> int | None:
    """an offset's vector lengths, where it's a whole number of them"""
    terms = dict(offset.terms) if isinstance(offset, sym) else {}
    if set(terms) - {("VL",)}:
        return None
    return terms.get(("VL",), 0)


class tailmask(lsc_irmod):
    """
    A packm vec case packs cdim = N*VL + M rows in one pass, M from 1 to VL-1
    known at run time: its kernel takes N+1 vectors along cdim, the last
    one's loads and stores under a mask of its first M elements - SVE's
    whilelo, set once from the kernel's parameter tail(m) - the elements
    past them neither read nor written. The accesses marked are each
    component's at its highest vector along its vector's index.
    """
    name = "tailmask"
    description = "a kernel's last vector along an index masked to a run-time count, tail(<index>)"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = False
    constraints = "masks of a register's count (MASKAVL: SVE's whilelo); vectors along the index a VL apart"

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        if not ctx.gen.set.forms(modifiers={opset_modifier.MASKAVL}):
            return [f"{type(ctx.gen).__name__} has no masks of a register's count"]
        return []

    def apply(self, program) -> int:
        accesses = [(block, section, k, op) for block, section in blocks_and_sections(program)
                    for k, op in enumerate(getattr(block, section) or [])
                    if isinstance(op, (lsc_load, lsc_store)) and op.offset is not None
                    and rgt.VEC == (op.rtypes or [None, None])[1]]
        last = {}
        for _, _, _, op in accesses:
            comp = op.indices[1].component
            index = program.vector_indices.get(comp)
            if index is None:
                continue
            n = _vectors(program.offsets.records[op.offset].along(index))
            if n is None:
                last[comp] = None                     # not whole vectors: left alone
            elif last.get(comp, 0) is not None:
                last[comp] = max(last.get(comp, 0), n)
        marked = 0
        for _, _, _, op in accesses:
            comp = op.indices[1].component
            index = program.vector_indices.get(comp)
            if index is None or last.get(comp) is None:
                continue
            if last[comp] == _vectors(program.offsets.records[op.offset].along(index)):
                op.add_property("tail", index)
                program.tails.add(index)
                marked += 1
        return marked
