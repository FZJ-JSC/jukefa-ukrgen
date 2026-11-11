"""
The IR's liveness, one analysis (docs/REGISTER_ALLOCATION.md step 2): which
registers an operation reads and writes, which operations read before they
write, what's live after each - by a key function, a caller's (the
emitter's: a data register by component, number and register type; the
scheduler's: the IR's register class, a group's members its first)
"""

from asmgen.asmblocks.op import register_type as rgt

from ..models.load_store_operations import lsc_load, lsc_loop, lsc_move
from ..support.data_move import dm_step

SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")
#: the register types holding values: what renaming and allocation move - a
#: set's mask, the machinery's registers in the IR, among them
DATA = (rgt.VEC, rgt.FP, rgt.TILE, rgt.MASK)


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


def _dest_mods(op) -> set:
    """The modifiers an operation's step asks of its destination register, by name"""
    if not isinstance(op.step, dm_step):
        return set()
    return {m.name for m in (op.step.opd_mod_reqs or {}).get(op.step.dest, ())}


def keeps(op) -> bool:
    """
    Whether an operation keeps part of a data register it writes - writes a
    part: a lane loaded keeps the other lanes (a ZEROOTHERS load of lane 0
    none - none below it, the rest zeroed: the whole register written), a
    block written into a vector the other blocks (AVX's vinsertf128; a block
    extracted into a scratch writes all of it), a slice written into a tile
    the other slices. The value flows through it: it reads what it writes -
    in a loop over slices: the loop, covering its tiles' slices, writes
    them whole (reads_writes)
    """
    # a load or a move only: other operations (a scheduler's tests' state-only
    # ones) have no lanes, blocks or slices to keep
    if isinstance(op, lsc_load):
        lane = op.properties.get("lane")
        return lane is not None and not ("ZEROOTHERS" in _dest_mods(op) and 0 == lane)
    if isinstance(op, lsc_move):
        if op.properties.get("block") is not None:
            return "IBLOCK" in _dest_mods(op)
        if op.properties.get("slice") is not None:
            types = op.rtypes or []
            return len(types) > 1 and rgt.TILE == types[1]
    return False


def reads_writes(op, key=data_key) -> tuple[set, set]:
    """
    The registers an operation reads and writes - a loop's: what its body
    reads before writing it (carried into it), what it writes; a loop over
    slices writes its tiles whole (each slice once: through one slice index,
    as lanes by their numbers) - what its slices keep of a tile not read
    """
    def at(o, positions):
        return {k for p in positions or [] for k in [key(o, p)] if k is not None}

    if isinstance(op, lsc_loop):
        covered = set()
        if "slices" == op.info.get("kind"):
            covered = {key(op, p) for p in range(len(op.indices))
                       if p < len(op.rtypes or []) and rgt.TILE == op.rtypes[p]} - {None}
        reads, writes = set(), set()
        for b in op.block:
            r, w = reads_writes(b, key)
            if covered and not isinstance(b, lsc_loop) and keeps(b):
                # what a slice keeps of a tile the loop covers: the loop
                # writes the tile whole - what else it keeps stays read
                own = at(b, b.reads)
                r = own | (r - own - covered)
            reads |= r - writes
            writes |= w
        return reads, writes
    r, w = at(op, op.reads), at(op, op.writes)
    # what an operation keeping part of it writes it reads too (keeps)
    return (r | w, w) if keeps(op) else (r, w)


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


def live_in(ops: list, end: set, key=data_key) -> set:
    """What's live before operations: read by one before it's written, or at the end (end) and not written"""
    live = set(end)
    for op in reversed(ops):
        reads, writes = reads_writes(op, key)
        live = (live - writes) | reads
    return live
