"""
The renamer (docs/REGISTER_ALLOCATION.md step 3): flexible values onto dead
registers within a budget. Its first use: a loop body's own temporaries - a
loop over slices' copies' vectors - under at most as many names as
registers there are for them, so the scheduler's order can't hold more
"""

import copy

from asmgen.asmblocks.op import register_type as rgt

from . import liveness


def rename_temporaries(body: list, limit: int, types=(rgt.VEC,)) -> int:
    """
    A loop body's own temporaries (written before read: liveness.local) under
    at most limit names, in the body's order - copies one after another: a
    value keeps its own name while fewer are in use, else takes the one dead
    longest of its component and register type (its data type its own). The
    reuse is a dependency the scheduler keeps - no order it gives holds more
    of them at once.
    :return: the values renamed
    """
    local = liveness.local(body, types)
    if len(local) <= limit:
        return 0
    wanted = set(local)
    first, last = {}, {}
    for pos, op in enumerate(body):
        for p in range(len(op.indices)):
            k = liveness.data_key(op, p)
            if k in wanted:
                first.setdefault(k, pos)
                last[k] = pos
    mapping, names, active, free, renamed = {}, set(), [], [], 0
    for k in sorted(local, key=lambda key: first[key]):
        # names whose values ended before this one starts, oldest freed first
        for end, name in sorted(a for a in active if a[0] < first[k]):
            active.remove((end, name))
            free.append(name)
        alike = [n for n in free if (n[0], n[2]) == (k[0], k[2])]
        if len(names) < limit or not alike:
            target = k
            names.add(k)
        else:
            target = alike[0]
            free.remove(target)
            renamed += 1
        mapping[k] = target
        active.append((last[k], target))
    for op in body:
        for p in range(len(op.indices)):
            k = liveness.data_key(op, p)
            if k in mapping and mapping[k] != k:
                idx = copy.copy(op.indices[p])
                idx.indices = [mapping[k][1]] + list(idx.indices[1:])
                op.indices[p] = idx
    return renamed
