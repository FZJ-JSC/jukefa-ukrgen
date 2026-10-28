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

    def short_regions(self, ops: list) -> list:
        """
        The vl route: the operations at the tail's length between an lsc_state
        at its count and one at the full length - a last vector's chain where
        it closes in the section (its load, what reads what the chain writes,
        the last-vector store of it: one region, half the switches), else each
        last-vector access alone. Every other vector operation reads the
        length, so the schedulers keep them out of between
        """
        from ...schedulers.list_scheduler import _key
        tails = [k for k, op in enumerate(ops) if op.properties.get("tail_vl") is not None]
        if not tails:
            return ops
        region_of = {}
        for k in (k for k in tails if isinstance(ops[k], lsc_load)):
            chain, written = [k], {_key(ops[k], p) for p in ops[k].writes}
            for j in range(k + 1, len(ops)):
                if j in region_of:
                    continue
                if written & {_key(ops[j], p) for p in ops[j].reads}:
                    chain.append(j)
                    written |= {_key(ops[j], p) for p in ops[j].writes}
            # it closes where it ends in last-vector stores and nothing outside
            # it reads what it writes
            stores = [j for j in chain if isinstance(ops[j], lsc_store)]
            closes = stores and all(ops[j].properties.get("tail_vl") is not None for j in stores) \
                and all(j in chain or not (written & {_key(ops[j], p) for p in ops[j].reads})
                        for j in range(len(ops)))
            if closes:
                for j in chain:
                    region_of[j] = k
        state = lambda op, value: lsc_state({"vlen": value}, self.ctx.component_dts[op.indices[1].component])
        out, placed = [], set()
        for k, op in enumerate(ops):
            head = region_of.get(k)
            if head is not None:
                members = sorted(j for j, h in region_of.items() if h == head)
                if k == members[-1]:
                    first = ops[members[0]]
                    index = first.properties["tail_vl"]
                    out += [state(first, f"tail({index})"), *(ops[j] for j in members), state(first, "max")]
                    placed.update(members)
                continue
            if op.properties.get("tail_vl") is not None:
                index = op.properties["tail_vl"]
                out += [state(op, f"tail({index})"), op, state(op, "max")]
                continue
            out.append(op)
        return out

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
            for block, section in blocks_and_sections(program):
                setattr(block, section, self.short_regions(list(getattr(block, section) or [])))
        return marked
