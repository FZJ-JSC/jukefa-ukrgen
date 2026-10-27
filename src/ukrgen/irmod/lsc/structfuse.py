"""
structfuse: a trans case's row stores fused into one interleaving store
"""
from __future__ import annotations

import copy

from asmgen.asmblocks.op import register_type as rgt, opmem_modifier as memmod

from ...lsc_model.addressing import sym
from ...models.load_store_operations import lsc_store, lsc_addr_compute
from .base import lsc_irmod, irmod_param, irmod_placement, blocks_and_sections
from .widen import struct_sigs


def _constant(delta) -> int | None:
    """an address delta's value, where it's a constant number of elements"""
    if isinstance(delta, int):
        return delta
    if isinstance(delta, sym):
        if not delta.terms:
            return 0
        if 1 == len(delta.terms) and () == delta.terms[0][0]:
            return delta.terms[0][1]
    return None


def _row_store(op, comp: str | None = None, row: int | None = None) -> bool:
    """
    A row's store into the panel across the grain: strided along the panel
    (stride_index), its vector register the row's
    """
    if not isinstance(op, lsc_store) or op.properties.get("stride_index") is None:
        return False
    if 2 != len(op.indices) or rgt.VEC != op.rtypes[1]:
        return False
    data = op.indices[1]
    if comp is not None and (data.component != comp or op.indices[0].component != comp):
        return False
    return row is None or data.indices[0] == row


def _touches(op, comp: str) -> bool:
    """whether an operation names one of the component's registers"""
    return any(comp == idx.component for idx in op.indices)


def _record(program, op):
    """an access's offset record: its elements along each index"""
    return None if op.offset is None else program.offsets.records[op.offset]


def _rows_apart(first, record, rows: int, vector_index: str | None) -> bool:
    """
    Whether an access is rows elements on from the first along one index -
    not the vector's - and where it is along every other
    """
    if first is None or record is None or first.component != record.component:
        return False
    a, b = dict(first.elements), dict(record.elements)
    differing = [k for k in set(a) | set(b) if a.get(k, sym()) != b.get(k, sym())]
    if 1 != len(differing) or vector_index == differing[0]:
        return False
    k = differing[0]
    start, at = _constant(a.get(k, sym())), _constant(b.get(k, sym()))
    return start is not None and at is not None and rows == at - start


def runs(program, ops: list):
    """
    The stores of a step's rows: (positions, rows, component) - strided
    stores of consecutive registers, the rows a row apart along an index
    other than the vector's; others' operations between them stay
    """
    i = 0
    while i < len(ops):
        if not _row_store(ops[i]):
            i += 1
            continue
        data = ops[i].indices[1]
        comp, first = data.component, data.indices[0]
        record = _record(program, ops[i])
        vector_index = program.vector_indices.get(comp)
        members, j = [i], i + 1
        while j < len(ops):
            op = ops[j]
            if _row_store(op, comp, first + len(members)) and \
                    _rows_apart(record, _record(program, op), len(members), vector_index):
                members.append(j)
            elif _touches(op, comp):
                break
            j += 1
        n = len(members)
        if n >= 2 and 0 == first % n:
            yield members, n, comp
            i = members[-1] + 1
            continue
        i += 1


def parse_split(text) -> dict[int, list[int]]:
    """
    --structfuse-split: rows=part+part, comma separated - 12=4+8,5=2+3 - the
    parts a step's rows go in, in that order (a part of 1 row its strided
    store); the rows not given parted greedily under fields
    """
    splits = {}
    for item in str(text or "").replace(" ", "").split(","):
        if not item:
            continue
        rows, eq, parts = item.partition("=")
        if not eq or not rows.isdigit() or not all(p.isdigit() and int(p) > 0 for p in parts.split("+")):
            raise ValueError(f"--structfuse-split {text}: rows=part+part, comma separated (12=4+8,5=2+3)")
        numbers = [int(p) for p in parts.split("+")]
        if sum(numbers) != int(rows):
            raise ValueError(f"--structfuse-split {item}: its parts take {sum(numbers)} rows, not {rows}")
        splits[int(rows)] = numbers
    return splits


class structfuse(lsc_irmod):
    """
    A panel packed across the grain - packm's trans case, its rows
    contiguous along the panel - stores each row's vector into the panel
    cdim elements apart (SVE's scatter, RVV's strided store), the address a
    row on between rows and back after. Where the ISA stores N registers
    interleaved - element e of register p at memory element N*e + p:
    NEON's and SVE's st2-st4, RVV's segment stores of 2-8 fields - the
    step's N row stores are one: the rows a group of consecutive registers,
    stored where row 0's was. That's the packed panel where its rows are N
    apart, as the trans dispatch calls a case: cdim rows, P's leading
    dimension cdim.
    """
    params = [irmod_param(name="fields", default=0, parse=int,
                          description="the most rows one structure store takes (0: the ISA's most); a "
                                      "step's rows beyond it parted - as many of them as fit, then the "
                                      "rest - each part a strided structure store (RVV's vssseg) where "
                                      "the ISA has them"),
              irmod_param(name="split", default={}, parse=parse_split,
                          description="parts by row count, in order - rows=part+part, comma separated: "
                                      "12=4+8,5=2+3 - over fields' greedy ones for those rows (a part of "
                                      "1 row its strided store)")]
    name = "structfuse"
    description = "a trans case's row stores fused into one interleaving (structure) store"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = False
    constraints = ("a step's rows stored strided along the panel, one register each, a row apart, "
                   "the first a multiple of their number; a structure store of as many registers")

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        if not ctx.gen.store.forms(modifiers={memmod.STRUCT}):
            return [f"{type(ctx.gen).__name__} has no structure stores"]
        return []

    def apply(self, program) -> int:
        gen = self.ctx.gen
        changed = 0
        for block, section in blocks_and_sections(program):
            ops = list(getattr(block, section) or [])
            fused_at, dropped = {}, set()
            for members, n, comp in runs(program, ops):
                dt = self.ctx.component_dts[comp]
                most = max((s.structural_params["nstructs"] for s in gen.store.get_signatures()
                            if "STRUCT" in {m.name for m in s.modifiers}
                            and "GSTRIDE" not in {m.name for m in s.modifiers}
                            and dt == s.operands["adreg"].dt), default=0)
                cap = min(most, self.values["fields"]) if self.values["fields"] else most
                if cap < 2:
                    continue
                # the parts given for these rows (split); else one structure,
                # or parts of cap rows and the rest - each part's rows
                # interleaved into the columns, a stride apart (strided)
                given = self.values["split"].get(n)
                if given is not None:
                    if max(given) > most:
                        raise ValueError(f"--structfuse-split {n}={'+'.join(map(str, given))}: a part of "
                                         f"{max(given)} rows, the ISA's structures take {most} at most")
                    parts = list(given)
                else:
                    parts = [n] if n <= cap else [cap] * (n // cap) + ([n % cap] if n % cap else [])
                strided = len(parts) > 1
                sigs = {s: struct_sigs(gen, "store", dt, s, strided) for s in set(parts) if s > 1}
                if not sigs:
                    continue                # all parts single rows: the strided stores they are
                ways = max(parts)
                known = program.groups.get(comp)
                if not sigs or not all(sigs.values()) or (known is not None and len(known) < 3):
                    continue
                # each part a group of its own - its registers consecutive,
                # wherever its first row's is (a step's rows needn't start at
                # a multiple of the widest part: 12 rows in 8 and 4, the
                # second step's 8 from row 12)
                partitions = dict(known[2]) if known is not None else {}
                row = 0
                for s in parts:
                    if s > 1:
                        part = [ops[members[row + p]] for p in range(s)]
                        fused = copy.deepcopy(part[0])
                        if not strided:
                            fused.properties.pop("stride_index", None)
                        fused.add_property("group", s)
                        fused.sigs = sigs[s]
                        # it reads every row's register, each with its row's
                        # tile: schedulers see the members, not only the first
                        extra = range(len(fused.indices), len(fused.indices) + s - 1)
                        fused.indices = list(fused.indices) + [op.indices[1] for op in part[1:]]
                        fused.tiles = list(fused.tiles) + [op.tiles[1] for op in part[1:]]
                        fused.reads = list(fused.reads) + list(extra)
                        fused.rtypes = list(fused.rtypes) + [op.rtypes[1] for op in part[1:]]
                        fused.reg_types = list(fused.reg_types) + [op.reg_types[1] for op in part[1:]]
                        partitions[part[0].indices[1].indices[0]] = s
                        fused_at[members[row]] = fused
                        dropped.update(members[row + 1:row + s])
                    row += s
                program.groups[comp] = (ways, "STRUCT", partitions)
            if fused_at:
                setattr(block, section, [fused_at.get(k, op) for k, op in enumerate(ops) if k not in dropped])
                changed += len(fused_at)
        return changed
