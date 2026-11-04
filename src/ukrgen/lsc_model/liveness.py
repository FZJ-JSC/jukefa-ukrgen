"""
The IR's liveness, one analysis (docs/REGISTER_ALLOCATION.md step 2): which
registers an operation reads and writes, which operations read before they
write, what's live after each - by a key function, a caller's (the
emitter's: a data register by component, number and register type; the
scheduler's: the IR's register class, a group's members its first)
"""

from asmgen.asmblocks.op import register_type as rgt

from ..models.load_store_operations import lsc_loop

SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")
#: the register types holding data: what renaming and allocation move
DATA = (rgt.VEC, rgt.FP, rgt.TILE)


def data_key(op, p):
    """
    A data register - vector, scalar, tile - by component, number and register
    type (a tile and a vector of one component and number differ); None for
    an operand of another kind
    """
    types = op.rtypes or []
    if p < len(op.indices) and p < len(types) and types[p] in DATA:
        return (op.indices[p].component, op.indices[p].indices[0], types[p])
    return None


def reads_writes(op, key=data_key) -> tuple[set, set]:
    """
    The registers an operation reads and writes - a loop's: what its body
    reads before writing it (carried into it), what it writes
    """
    def at(o, positions):
        return {k for p in positions or [] for k in [key(o, p)] if k is not None}
    if isinstance(op, lsc_loop):
        reads, writes = set(), set()
        for b in op.block:
            reads |= at(b, b.reads) - writes
            writes |= at(b, b.writes)
        return reads, writes
    return at(op, op.reads), at(op, op.writes)


def exposed(ops: list, key=data_key) -> set:
    """The registers operations read before they write them, in order"""
    out, written = set(), set()
    for op in ops:
        reads, writes = reads_writes(op, key)
        out |= reads - written
        written |= writes
    return out


def live_afters(ops: list, end: set, key=data_key) -> list:
    """
    What's live after each operation: read by a later one before it's written,
    or at the end (end)
    """
    live, out = set(end), [None] * len(ops)
    for pos in reversed(range(len(ops))):
        out[pos] = set(live)
        reads, writes = reads_writes(ops[pos], key)
        live = (live - writes) | reads
    return out


def read_before_written(blocks: list, key=data_key) -> set:
    """The registers blocks read before writing them: alive into them"""
    return exposed([op for b in blocks for s in SECTIONS for op in getattr(b, s) or []], key)


def across(order: list, pos: int, end: set, key=data_key) -> set:
    """
    The registers live across order[pos] (a loop) it neither reads nor writes:
    read after it before written, or live at the end (end) and not written
    after it - held while it runs, not its iterations'
    """
    reads, writes = reads_writes(order[pos], key)
    after = live_afters(order[pos:], end, key)[0]
    return after - reads - writes


def local(ops: list, types=(rgt.VEC,), key=data_key) -> list:
    """
    The registers operations write before reading them - an operation reading
    and writing one reads it first - in the order first written: temporaries
    of their own (a loop's body's), of the register types given
    """
    out, read = [], set()
    for op in ops:
        read |= {k for p in op.reads or [] for k in [key(op, p)] if k is not None}
        for p in op.writes or []:
            k = key(op, p)
            if k is not None and k[-1] in types and k not in read and k not in out:
                out.append(k)
    return out
