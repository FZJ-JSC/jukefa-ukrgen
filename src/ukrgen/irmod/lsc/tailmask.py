"""
tailmask: a kernel's last vector along an index masked to a run-time count
"""
from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt
from asmgen.asmblocks.op.opset import opset_modifier

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_load, lsc_state, lsc_store
from ...specializers.signature import _sigs
from .base import lsc_irmod, irmod_param, irmod_placement, blocks_and_sections


def _masked(gen, op) -> list:
    """
    An access's forms under a mask: its own where they take one (SVE's
    every vector access), else each one's twin with MASK (RVV's v0.t)
    """
    action = "load" if isinstance(op, lsc_load) else "store"
    every = getattr(gen, action).get_signatures()
    out = []
    for s in _sigs(op.sigs):
        mods = {m.name for m in s.modifiers}
        if "MASK" in mods:
            out.append(s)
            continue
        out += [t for t in every if {m.name for m in t.modifiers} == mods | {"MASK"}
                and t.structural_params == s.structural_params
                and t.operands["adreg"].dt == s.operands["adreg"].dt]
    return out


def _vectors(offset) -> int | None:
    """
    An offset along a vector's index, ordered as vectors are: whole vector
    lengths where they're symbolic (SVE, RVV: k*VL), elements where the
    length is a number (AVX-512's 0, 8, 16); None where it's neither
    """
    terms = dict(offset.terms) if isinstance(offset, sym) else {}
    if not terms:
        return 0
    if set(terms) <= {("VL",)}:
        return terms[("VL",)]
    if set(terms) <= {()}:
        return terms[()]
    return None


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
    params = [irmod_param(name="route", default="mask", choices=("mask", "vl"),
                          description="mask: the last vector's accesses masked (SVE's predicate, RVV's v0, "
                                      "AVX-512's k); vl: RVV's vector length set to the count around each "
                                      "of them (vsetvli), the full length back after")]

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        if not ctx.gen.set.forms(modifiers={opset_modifier.MASKAVL}):
            return [f"{type(ctx.gen).__name__} has no masks of a register's count"]
        return []

    def apply(self, program) -> int:
        route = self.values["route"]
        if "vl" == route and not [f for f in self.ctx.gen.set.forms(modifiers={opset_modifier.VLEN})
                                  if "avlreg" in f.operands]:
            raise ValueError(f"tailmask route vl: {type(self.ctx.gen).__name__} sets no vector length "
                             f"from a register (RVV's vsetvli rd, avl)")
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
                if "mask" == route:
                    masked = _masked(self.ctx.gen, op)
                    if not masked:
                        raise ValueError(f"tailmask: {comp}'s last vector has no masked form of its "
                                         f"{'load' if isinstance(op, lsc_load) else 'store'}")
                    op.sigs = masked
                else:
                    program.tail_vl.add(index)
                    op.add_property("tail_vl", index)
                op.add_property("tail", index)
                program.tails.add(index)
                marked += 1
        if program.tail_vl:
            # the vl route: each last-vector access between an lsc_state at the
            # tail's count and one at the full length - every vector operation
            # reads the length, so the schedulers keep them out of between
            for block, section in blocks_and_sections(program):
                ops = list(getattr(block, section) or [])
                out = []
                for op in ops:
                    index = op.properties.get("tail_vl")
                    if index is None:
                        out.append(op)
                        continue
                    dt = self.ctx.component_dts[op.indices[1].component]
                    out += [lsc_state({"vlen": f"tail({index})"}, dt), op, lsc_state({"vlen": "max"}, dt)]
                setattr(block, section, out)
        return marked
