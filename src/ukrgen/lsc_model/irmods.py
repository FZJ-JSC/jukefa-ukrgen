"""
IR modifications: passes over specialized LSC IR, run in their own stage
between specialization and scheduling.
"""

from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

from ..models.load_store_operations import (
    lsc_load, lsc_store, lsc_addr_compute, ldst_modifier)
from ..models.lsc.reg import lsc_reg_type
from ..specializers.signature import _sigs, _masked
from ..models.lsc.index import lsc_reg_index
from ..support.data_move import dm_step, orig_ref, filter_by_step_requirements
from ..support.sig_group import group_sigs
from .addressing import sym
from .ir import ir_program


def _transfer_size(ctx, op) -> int | None:
    """
    Bytes an access moves: one element for a broadcast or a lane, a vector
    otherwise. None where vectors have no fixed size.
    """
    esize = adt_size(ctx.component_dts[op.indices[0].component])
    if ldst_modifier.bcast1 in op.mods or ldst_modifier.lane in op.mods:
        return esize
    return None if ctx.gen.is_vla else ctx.gen.simd_size


def _postinc_takes(ctx, op, increment: int) -> bool:
    """
    Whether one of an access's signatures post-increments its address register
    by this many bytes. Where a signature constrains the increment, its
    constraints decide; where it states none, only the access's transfer size is
    assumed - AArch64's structure loads (ld1r, ld1) take nothing else, while
    ldr takes a range, and asmgen does not say which.
    """
    for sig in _sigs(op.sigs):
        if _masked(sig) or {m.name for m in sig.modifiers} - {"MASK"} != {"POSTINC"}:
            continue
        shape = sig.operands.get("iinc")
        if shape is None:
            continue
        if not shape.value_constraints:
            if increment == _transfer_size(ctx, op):
                return True
            continue
        fits = True
        for cons in shape.value_constraints:
            lo, hi = getattr(cons, "minval", None), getattr(cons, "maxval", None)
            if lo is not None and not lo <= increment <= hi:
                fits = False
            valset = getattr(cons, "valset", None)
            if valset is not None and increment not in valset:
                fits = False
        if fits:
            return True
    return False


def _post_increment(op, elements: int):
    op.increment = sym.const(elements)
    op.mods.add(ldst_modifier.postinc)
    if 0 not in op.writes:
        op.writes = sorted(op.writes + [0])


def ldinc(ctx, program: ir_program):
    """
    Fuse address computations into post-increment accesses.

    Specializing leaves an access at an offset no signature takes behind an
    address computation into a scratch register: s = a + c, then the access
    through s. When the next such pair sets s from the same register, and the
    previous access has a signature post-incrementing by the distance between
    the two, that access becomes a post-increment and the next computation
    goes - the chain walks s: ld1r {v.2d}, [x], #8 instead of a mov and an add
    before every load.

    Whether an access can post-increment is decided by its signatures, not by
    the ISA.
    """
    def fuse(ops: list) -> list:
        out = []
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
                    if _postinc_takes(ctx, prev[0], gap * adt_size(ctx.component_dts[comp])):
                        _post_increment(prev[0], gap)
                        out.append(nxt)
                        chains[key] = (nxt, offset, src)
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
        return out

    for block in program.blocks + [b for c in program.cases for b in c.blocks]:
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            setattr(block, section, fuse(getattr(block, section)))


def lanefuse(ctx, program: ir_program):
    """
    Fuse loads into single lanes into one load of the whole register.

    An operation using one element of a register at a time (an FMA by element)
    gets its elements loaded lane by lane, which works for any layout. Where a
    register's lanes are all loaded, through the same address register, from
    contiguous memory - lane l at lane 0's offset plus l - one plain load at
    the first of them does the same. Strided lanes stay as they are until
    strided and indexed loads are specialized.

    Runs on the model's IR, before specialization gives each lane load an
    address of its own.
    """
    gen = ctx.gen
    if gen.is_vla:
        return
    db, strides = program.offsets, program.strides

    def plain(comp):
        step = dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC)
        sigs = filter_by_step_requirements(gen.load.get_signatures(), step,
                                           ctx.component_dts[comp])
        return step, (group_sigs(sigs) if sigs else None)

    def fuse(ops: list) -> list:
        runs: dict[tuple, dict[int, int]] = {}
        replace, drop = {}, set()
        for pos, op in enumerate(ops):
            if isinstance(op, lsc_load) and ldst_modifier.lane in op.mods:
                key = (op.indices[1].component, op.indices[1].indices[0])
                lane = op.properties.get("lane")
                run = runs.get(key)
                if run is None or lane in run:
                    run = runs[key] = {}
                run[lane] = pos
                comp = op.indices[0].component
                lanes = gen.simd_size // adt_size(ctx.component_dts[comp])
                if set(run) != set(range(lanes)):
                    continue
                runs.pop(key)
                first = ops[run[0]]
                base = db.elements_offset(first.offset, strides.get(comp, {}))
                contiguous = all(
                    (db.elements_offset(ops[p].offset, strides.get(comp, {})) - base)
                    == sym.const(l) for l, p in run.items())
                one_areg = all(ops[p].indices[0].indices == first.indices[0].indices
                               for p in run.values())
                step, sigs = plain(comp)
                if contiguous and one_areg and sigs:
                    at = min(run.values())
                    replace[at] = lsc_load(
                        comp, key[1], first.indices[0].indices[0], None, None,
                        first.tiles[1], set(), data=lsc_reg_index(key[0], [key[1]]),
                        rsln=first.rsln, step=step, sigs=sigs, offset=first.offset,
                        rtypes=first.rtypes)
                    drop |= {p for p in run.values() if p != at}
                continue
            # anything else writing a register ends its run
            for p in op.writes:
                idx = op.indices[p]
                runs.pop((idx.component, idx.indices[0]), None)
        return [replace.get(i, op) for i, op in enumerate(ops) if i not in drop]

    for block in program.blocks + [b for c in program.cases for b in c.blocks]:
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            setattr(block, section, fuse(getattr(block, section)))


# on the model's IR, before specialization
MODEL_IRMODS = {
    "lanefuse": lanefuse,
}

# on the specialized IR
IRMODS = {
    "ldinc": ldinc,
}
