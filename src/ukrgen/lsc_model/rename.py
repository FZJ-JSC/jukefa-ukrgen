"""
The renamer (docs/REGISTER_ALLOCATION.md step 3): flexible values onto dead
registers within a budget. Its first use: a loop body's own temporaries - a
loop over slices' copies' vectors - under at most as many names as
registers there are for them, so the scheduler's order can't hold more
"""

import copy

from asmgen.asmblocks.op import register_type as rgt

from . import classes, liveness


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


def rename_straight(ops: list, end: set, limit: int, flexible, tags: frozenset,
                    prefer: str = "new") -> int:
    """
    A straight-line section's flexible values onto at most limit names of a
    register file at once. A value whose life lies in the section - a full
    write first (not a lane or slice of a register), dead before the section
    ends (not in end) - keeps its own name where that is in use already or
    fewer than limit are, else takes a name free all through its life:
    another value's, dead - an accumulator after its store, C's value in
    AB's (its owner set: its data type its own) - the one free longest.
    flexible(key): a component the user didn't fix (data-regs); tags: the
    file's register types (the tracker's pool). prefer: where a value looks
    first - new (its own name while fewer than limit are in use, then the
    dead name free longest), dead (the dead name freed last: the fewest
    registers), distance (the dead name free longest: the most room to load
    ahead) - a new name where no dead one fits. The reuse is a dependency
    the scheduler keeps: no order it gives holds more.
    :return: the values renamed
    """
    mine = lambda k: k is not None and classes.TAGS.get(k[2]) in tags
    rw = []
    for op in ops:
        reads = {k for p in op.reads or [] for k in [liveness.data_key(op, p)] if mine(k)}
        writes = {k for p in op.writes or [] for k in [liveness.data_key(op, p)] if mine(k)}
        # a lane, a block or a slice written is part of a register - the rest
        # kept (a lane load keeps the lanes below, AVX's vinsertf128 the other
        # block), though the IR has the operation read only its source: a
        # value built piece by piece one value, read by each piece written (a
        # block extracted into a scratch writes all of it: kept from moving)
        if any(op.properties.get(p) is not None for p in ("lane", "block", "slice")):
            reads |= writes
        rw.append((reads, writes))
    afters, live = [None] * len(ops), {k for k in end if mine(k)}
    for pos in reversed(range(len(ops))):
        afters[pos] = set(live)
        live = (live - rw[pos][1]) | rw[pos][0]
    # each name's values: (first, last, movable) - first -1 where live into
    # the section, last len(ops) where live after it
    spans, live = {}, {k: -1 for k in live}
    for pos, (reads, writes) in enumerate(rw):
        for k in reads | writes:
            live.setdefault(k, pos)
        for k in [k for k in live if k not in afters[pos]]:
            first = live.pop(k)
            movable = first >= 0 and k in rw[first][1] and k not in rw[first][0] and flexible(k)
            spans.setdefault(k, []).append((first, pos, movable))
    for k, first in live.items():
        spans.setdefault(k, []).append((first, len(ops), False))
    taken = {k: [(f, l) for f, l, m in ss if not m] for k, ss in spans.items()}
    in_use = {k for k, ss in taken.items() if ss}
    clear = lambda name, f, l: all(e < f or b > l for b, e in taken.get(name, []))
    plan = []
    # in order of their first write - ties by name: the same names every run
    # (no set's order, which follows string hashing)
    order = lambda k: (k[0], k[1])
    for f, l, k in sorted(((f, l, k) for k, ss in spans.items() for f, l, m in ss if m),
                          key=lambda v: (v[0], v[1], order(v[2]))):
        free = sorted((n for n in in_use if n != k and n[2] == k[2] and clear(n, f, l)), key=order)
        own = k in in_use or ("new" == prefer and len(in_use) < limit)
        if own or not free:
            in_use.add(k)
            taken.setdefault(k, []).append((f, l))
            continue
        freed = lambda n: max((e for b, e in taken[n] if e < f), default=-2)
        if "dead" == prefer:
            target = min(free, key=lambda n: (-freed(n), order(n)))
        else:
            target = min(free, key=lambda n: (freed(n), order(n)))
        taken[target].append((f, l))
        plan.append((k, f, l, target))
    for k, f, l, target in plan:
        for pos in range(f, l + 1):
            op = ops[pos]
            for p in range(len(op.indices)):
                if liveness.data_key(op, p) == k:
                    idx = copy.copy(op.indices[p])
                    idx.owner = op.indices[p].value()
                    idx.component, idx.indices = target[0], [target[1]] + list(idx.indices[1:])
                    op.indices[p] = idx
    return len(plan)
