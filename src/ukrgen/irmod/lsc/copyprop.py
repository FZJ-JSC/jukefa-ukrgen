"""
Copy propagation: a copy (packm's kappa == 1, Y = X - the builder's lsc_moves
tagged copy) renamed away. Its destination's later reads read its source, the
move is dropped, and the copy is left its load and store.

Only those moves: lane moves, broadcasts, slices' extracts and inserts and
permutes aren't copies, and no register is renamed but a copy's destination,
while it holds the copy's value. A copy is kept wherever renaming could change
what is read:

- its source written before its destination's last read
- its destination read before written in a section (a value from outside it:
  an earlier iteration's)
- a loop reading the destination and writing the source, or writing the
  destination (its iterations' order)
- a register of a group (structure loads and stores: consecutive registers)

A tile's copy kept is an error: no instruction copies a tile into another.
So tiles' copies are copyprop_tiles' - required, no list of modifications
leaving it out; vectors' copyprop's - after shufflenet, which knows a
transpose's rows by the copy's registers (ZA's tiles have no shuffles).
"""

from asmgen.asmblocks.op import register_type as rgt

from ...models.load_store_operations import lsc_loop, lsc_move
from ...models.lsc.index import lsc_reg_index
from .base import irmod_placement, lsc_irmod, blocks_and_sections

DATA = (rgt.VEC, rgt.FP, rgt.TILE)


def _keys(op, positions) -> list:
    """
    The data registers at positions of an operation: (component, register,
    register type)
    """
    rtypes = op.rtypes or []
    return [(op.indices[p].component, op.indices[p].indices[0], rtypes[p])
            for p in positions if p < len(rtypes) and rtypes[p] in DATA]


def _events(ops):
    """
    The operations in order, a loop's whole block where the loop is
    """
    for op in ops:
        if isinstance(op, lsc_loop):
            yield from _events(op.block)
        else:
            yield op


def _live_in(ops, key) -> bool:
    """
    Whether operations read a register before writing it
    """
    for op in _events(ops):
        if key in _keys(op, op.reads):
            return True
        if key in _keys(op, op.writes):
            return False
    return False


def _rename(op, dst, src_index) -> None:
    """
    An operation's reads of dst read src instead - a loop's in its block -
    lanes kept
    """
    if isinstance(op, lsc_loop):
        for inner in op.block:
            _rename(inner, dst, src_index)
        op.refresh()
        return
    rtypes = op.rtypes or []
    for p in op.reads:
        if p < len(rtypes) and rtypes[p] in DATA and \
                (op.indices[p].component, op.indices[p].indices[0], rtypes[p]) == dst:
            op.indices[p] = lsc_reg_index(src_index.component,
                                          [src_index.indices[0]] + list(op.indices[p].indices[1:]))


class copyprop(lsc_irmod):
    """
    Vectors' copies renamed away, so a copy (kappa == 1) emits its load and
    store only; one kept a move
    """

    name = "copyprop"
    description = "copies (packm's kappa == 1) renamed away: the copy's reads read its source"
    placement = irmod_placement.PRE_SPECIALIZE
    # after shufflenet (it knows a transpose's rows by the copy's registers,
    # its permutes then reading them like any other read) and structfuse (its
    # groups kept); a tile's copy needs it
    default_enabled = True
    #: the register types of the copies it renames
    renames : tuple = (rgt.VEC, rgt.FP)

    def apply(self, program) -> int:
        changed = 0
        for block, section in blocks_and_sections(program):
            changed += self.propagate(program, getattr(block, section) or [], [])
        return changed

    def propagate(self, program, ops: list, after: list) -> int:
        """
        A list of operations' copies renamed away - a loop's block's as one
        of its iterations (the loop refreshed), after: what follows the list
        """
        changed, i = 0, 0
        while i < len(ops):
            op = ops[i]
            if isinstance(op, lsc_loop):
                inner = self.propagate(program, op.block, ops[i + 1:] + after)
                if inner:
                    op.refresh()
                    changed += inner
                i += 1
                continue
            if not (isinstance(op, lsc_move) and op.properties.get("copy_sto")):
                i += 1
                continue
            (src,), (dst,) = _keys(op, op.reads), _keys(op, op.writes)
            if dst[2] not in self.renames:
                i += 1
                continue
            why = self.kept(program, ops, i, src, dst, after)
            if why is not None:
                if rgt.TILE == dst[2]:
                    raise ValueError(f"{op.properties['copy_sto']}: a tile's copy kept ({why}), and no "
                                     f"instruction copies a tile into another")
                i += 1
                continue
            for later in self.reads_of(ops, i, dst):
                _rename(later, dst, op.indices[0])
            del ops[i]
            changed += 1
        return changed

    @staticmethod
    def reads_of(ops, i, dst) -> list:
        """
        The operations after a copy reading its destination, until written
        """
        out = []
        for op in ops[i + 1:]:
            if dst in _keys(op, op.reads):
                out.append(op)
            if dst in _keys(op, op.writes):
                break
        return out

    def kept(self, program, ops, i, src, dst, after) -> str | None:
        """
        Why a copy is to be kept; None where it can be renamed away
        """
        groups = program.groups or {}
        if src[2] != dst[2]:
            return "its registers of different types"
        if _live_in(after, dst):
            return "its destination read after its loop"
        if src[0] in groups or dst[0] in groups:
            return "a register of a group"
        if _live_in(ops[:i], dst):
            return "its destination read before the copy"
        for other, section in blocks_and_sections(program):
            if (getattr(other, section) or []) is not ops and _live_in(getattr(other, section) or [], dst):
                return f"its destination read before written in a {section}"
        clobbered = False
        for op in ops[i + 1:]:
            reads, writes = _keys(op, op.reads), _keys(op, op.writes)
            if dst in reads:
                if clobbered:
                    return "its source written before its destination's last read"
                if isinstance(op, lsc_loop) and src in writes:
                    return "a loop reading its destination writes its source"
            if dst in writes:
                if isinstance(op, lsc_loop):
                    return "a loop writes its destination"
                break
            if src in writes:
                clobbered = True
        return None


class copyprop_tiles(copyprop):
    """
    Tiles' copies renamed away (ZA's kappa == 1: rows loaded straight into the
    tile's slices) - required: no instruction copies a tile into another
    """

    name = "copyprop_tiles"
    description = "tiles' copies (ZA's kappa == 1) renamed away: no instruction copies a tile"
    required = True
    renames = (rgt.TILE,)

    @classmethod
    def triggered(cls, ctx) -> bool:
        # a kernel without tiles' copies: nothing to rename
        return True
