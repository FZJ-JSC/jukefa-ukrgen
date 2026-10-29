"""
Unrolling loops over a vector's elements
"""

import copy
from dataclasses import replace

from asmgen.registers import adt_size

from ...support.sig_group import sig_group
from .base import irmod_param, irmod_placement, lsc_irmod
from .vectorize import repeats
from .base import blocks_and_sections
from ...models.load_store_operations import lsc_loop, loop_walk, lsc_load, lsc_store
from ...models.lsc.index import lsc_reg_index
from ...lsc_model.addressing import sym
from asmgen.asmblocks.op import register_type as rgt
from ...support.domains import operand_values



class unroll_loops(lsc_irmod):
    """
    A loop over a vector's elements runs as many times as the vector has
    elements, a multiple of its divisor (16 bytes in elements: SVE's vector
    length is a multiple of 128 bits, RVV's V extension has VLEN >= 128). It
    unrolls by any of the divisor's divisors: each iteration takes that many
    elements, the count stepping down by as many
    """
    name = "unroll_loops"
    description = "unroll loops over a vector's elements"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = False
    params = [irmod_param(name="factor", default=2, parse=int,
                          description="elements a loop iteration takes: the largest dividing "
                                      "the loop's divisor, up to this"),
              irmod_param(name="preload", default=0, parse=int,
                          description="loops over slices: how many copies' loads - from the "
                                      "first - go to the end of the iteration before, software "
                                      "pipelined (the last iteration without); at most as many "
                                      "as keep register sets no other copy uses"),
              irmod_param(name="registers", default=1, parse=int,
                          description="registers an iteration's scalars rotate through "
                                      "(up to its elements): scalar loads and stores in "
                                      "flight together")]
    constraints = "the factor divides the element count, which is a multiple of the divisor"

    def apply(self, program) -> int:
        want = max(1, int(self.values["factor"]))
        changed = 0
        for op in list(repeats(program)) + list(slice_loops(program)):
            if op.info.get("count"):
                continue            # a run-time count (a masked tile's rows): not unrolled
            if op.info.get("explicit"):
                # set for this component (--COMP-subtiling): left as set
                continue
            # a vector holds a multiple of 16 bytes: the factors keeping the
            # count whole - and, over slices, every slice operand's immediate
            # taking an unrolled iteration's slices
            dt = self.ctx.component_dts[op.info["component"]]
            factors = [f for f in op.subtiling.count.count_unrolls(16 // adt_size(dt)) if f <= want]
            if "slices" == op.info.get("kind"):
                factors = [f for f in factors if immediates_take(op, f)]
            factor = max(factors, default=1)
            if factor > 1:
                op.subtiling = replace(op.subtiling, unroll=factor,
                                       registers=max(1, min(int(self.values["registers"]), factor)))
                if "slices" == op.info.get("kind"):
                    expand_copies(program, op)
                    depth = preload_depth(int(self.values["preload"]), op.subtiling.unroll,
                                          op.subtiling.registers)
                    if depth:
                        op.info["preload"] = depth
                changed += 1
        return changed


def slice_loops(program):
    for block, section in blocks_and_sections(program):
        for op in getattr(block, section) or []:
            if isinstance(op, lsc_loop) and "slices" == op.info.get("kind"):
                yield op


def immediates_take(loop, factor: int) -> bool:
    """
    Whether every slice operand of a loop's operations takes the immediates
    an unrolled iteration's slices need, 0 to factor-1, in some signature
    """
    for b in loop.block:
        sigs = b.sigs
        if sigs is None:
            continue
        names = {n for s in _sigs(sigs) for n in s.operands if n.endswith(("_immrow", "_immcol"))}
        if names and not any(all(i in operand_values(s, n) for i in range(factor))
                             for s in _sigs(sigs) for n in s.operands if n in names):
            return False
    return True


def _sigs(groups) -> list:
    """
    The signatures in a signature group, or in a list of groups
    """
    if groups is None:
        return []
    if isinstance(groups, list):
        return [s for g in groups for s in _sigs(g)]
    if isinstance(groups, sig_group):
        return list(groups.sigs)
    # a signature itself
    return [groups]


def _clone(op):
    new = copy.copy(op)
    new.indices = list(op.indices)
    new.properties = dict(op.properties or {})
    for attr in ("reads", "writes", "rtypes", "reg_types"):
        if getattr(op, attr, None) is not None:
            setattr(new, attr, list(getattr(op, attr)))
    return new


def expand_copies(program, loop):
    """
    An unrolled loop over slices with its copies in its block: each copy's
    slice operations at its immediate (property copy), its memory accesses
    walking from its own first slice - shifted along the index the slices
    iterate - and its own vector temporaries in register set copy mod
    registers: a scheduler sees only the dependencies there are and
    interleaves the copies. The emitter then emits the block once an
    iteration, every pointer and the slice index stepping by the unroll
    """
    unroll, registers = loop.subtiling.unroll, max(1, loop.subtiling.registers)
    if unroll < 2 or loop.info.get("unrolled"):
        return
    index = loop.info.get("index")
    def keys(op, positions):
        types = op.rtypes or []
        return [(op.indices[p].component, op.indices[p].indices[0], types[p] if p < len(types) else None)
                for p in positions]
    local, read = [], set()
    for b in loop.block:
        read |= set(keys(b, b.reads))
        for k in keys(b, b.writes):
            if rgt.VEC == k[2] and k not in read and k not in local:
                local.append(k)
    base, walks = list(loop.block), list(loop.walks)
    for b in base:
        b.add_property("copy", 0)
    block = list(base)
    for u in range(1, unroll):
        group = u % registers
        rename = {k: lsc_reg_index(k[0], [k[1] + 1000 * group]) for k in local} if group else {}
        moved = {}
        for b in base:
            n = _clone(b)
            types = n.rtypes or []
            for p, idx in enumerate(n.indices):
                k = (idx.component, idx.indices[0], types[p] if p < len(types) else None)
                if k in rename:
                    n.indices[p] = rename[k]
            n.add_property("copy", u)
            if isinstance(n, (lsc_load, lsc_store)):
                w = b.properties.get("walk", 0)
                if w not in moved:
                    old = loop.walks[w]
                    anchor = _clone(old.anchor)
                    anchor.offset = program.offsets.shifted(old.anchor.offset, index, sym.const(u))
                    moved[w] = len(walks)
                    walks.append(loop_walk(anchor=anchor, step=old.step))
                n.add_property("walk", moved[w])
            block.append(n)
    loop.block, loop.walks = block, walks
    loop.info["unrolled"] = unroll
    loop.refresh()


def preload_depth(asked: int, unroll: int, registers: int) -> int:
    """
    How many copies' loads can go to the iteration before: copy u's vectors
    in register set u mod registers, so the first P copies' sets must be
    used by no other copy - its own work would overwrite the preloaded
    values before they are consumed. The deepest such P up to the one asked,
    fewer than the copies
    """
    for depth in range(min(max(0, asked), unroll - 1), 0, -1):
        preloaded = {u % registers for u in range(depth)}
        if len(preloaded) == depth and \
                not any(u % registers in preloaded for u in range(depth, unroll)):
            return depth
    return 0
