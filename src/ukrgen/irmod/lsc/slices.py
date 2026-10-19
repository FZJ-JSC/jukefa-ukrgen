"""
Loops over tiles' slices: fused, values forwarded through them, invariant
loads hoisted out of them
"""

from asmgen.asmblocks.op import register_type as rgt

from ...models.load_store_operations import lsc_load, lsc_store, lsc_move, lsc_loop
from .base import irmod_param, irmod_placement, lsc_irmod, blocks_and_sections


SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")


def slice_loop(op) -> bool:
    return isinstance(op, lsc_loop) and "slices" == op.info.get("kind")


def tiles_of(loop) -> set:
    """
    The tile registers a loop over slices covers
    """
    return {_key(i, r) for i, r in zip(loop.indices, loop.rtypes) if rgt.TILE == r}


def _disjoint(program, a, b) -> bool:
    """
    Two accesses of a component lie in different tiles: their offsets differ
    by vector lengths - tiles partition the microtile by them
    """
    comp = a.indices[0].component
    strides = program.strides.get(comp, {})
    try:
        diff = program.offsets.elements_offset(a.offset, strides) - \
            program.offsets.elements_offset(b.offset, strides)
    except Exception:
        return False
    return any("VL" in factors and c for factors, c in dict(diff.terms).items())


def _key(index, rtype=None) -> tuple:
    """
    A register: its component, number and type - a tile and a vector of the
    same component and number are different registers
    """
    return (index.component, index.indices[0], rtype)


def _rtype(op, p):
    types = getattr(op, "rtypes", None) or []
    return types[p] if p < len(types) else None


def _written(op) -> set:
    return {_key(op.indices[p], _rtype(op, p)) for p in getattr(op, "writes", [])}


def _read(op) -> set:
    return {_key(op.indices[p], _rtype(op, p)) for p in getattr(op, "reads", [])}


class fuse_slices(lsc_irmod):
    """
    Adjacent loops over slices covering a tile register in common - the same
    orientation, the same number of slices - become one: each covers its
    tiles completely, slice by slice in the same order, so a slice of the
    second depends only on the same slice of the first. gemm's scaling and
    adding on a tile and the tile's store run in one pass over its slices
    """
    name = "fuse_slices"
    description = "fuse loops over tiles' slices: the same tile's, or every tile's of a path"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = True
    constraints = "slices of one orientation, as many; nothing flowing between the loops' tiles"
    params = [irmod_param(name="across_tiles", default=True,
                          parse=lambda v: str(v).lower() not in ("0", "false", "no", "off"),
                          description="fuse loops over different tiles too - one pass over the "
                                      "slices of every tile of a path, a slice index shared")]

    def apply(self, program) -> int:
        fused = 0
        for block, section in blocks_and_sections(program):
            ops = list(getattr(block, section) or [])
            i = 0
            while i < len(ops):
                first = ops[i]
                j = i + 1
                while slice_loop(first) and j < len(ops):
                    second = ops[j]
                    # a later loop over the same tiles moves up to the first,
                    # past what it doesn't depend on, and joins it
                    if slice_loop(second) and self.compatible(first, second, self.values["across_tiles"]) and \
                            all(self.independent(program, second, between) for between in ops[i + 1:j]):
                        ops[i] = first = self.fuse(first, second)
                        del ops[j]
                        fused += 1
                        continue
                    j += 1
                i += 1
            setattr(block, section, ops)
        return fused

    @staticmethod
    def compatible(first, second, across_tiles=True) -> bool:
        """
        Loops over slices of one orientation, as many: the slice index is the
        same for every tile, each tile's memory walking by its own pointer -
        covering a tile in common, or any tiles where fusing across them
        """
        return first.info.get("axis") == second.info.get("axis") \
            and first.subtiling.count == second.subtiling.count \
            and (across_tiles or bool(tiles_of(first) & tiles_of(second)))

    @staticmethod
    def independent(program, moved, between) -> bool:
        """
        Whether a loop can move above an operation: no register flow either
        way, and no memory both touch where either stores - accesses of the
        same component disjoint when their tiles are: their first slices'
        offsets differ by vector lengths
        """
        if _read(moved) & _written(between) or _written(moved) & (_read(between) | _written(between)):
            return False
        def accesses(op):
            if isinstance(op, lsc_loop):
                return [b for b in op.block if isinstance(b, (lsc_load, lsc_store))] + \
                       [w.anchor for w in op.walks]
            return [op] if isinstance(op, (lsc_load, lsc_store)) else []
        for a in accesses(moved):
            for b in accesses(between):
                if a.indices[0].component != b.indices[0].component:
                    continue
                if isinstance(a, lsc_load) and isinstance(b, lsc_load):
                    continue
                if not _disjoint(program, a, b):
                    return False
        return True

    @staticmethod
    def fuse(first, second):
        offset = len(first.walks)
        for b in second.block:
            if isinstance(b, (lsc_load, lsc_store)):
                b.add_property("walk", b.properties.get("walk", 0) + offset)
        first.block = list(first.block) + list(second.block)
        first.walks = list(first.walks) + list(second.walks)
        first.refresh()
        return first


class forward_slices(lsc_irmod):
    """
    In a loop over slices, a slice moved from a vector into a tile and moved
    back out of the same tile slice later - nothing writing the tile or the
    vector between - needs no second move: its readers read the first vector
    """
    name = "forward_slices"
    description = "forward slices moved into a tile and back out within a loop over slices"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = True
    constraints = "the slice and the vector unchanged between the two moves"

    def apply(self, program) -> int:
        forwarded = 0
        for block, section in blocks_and_sections(program):
            for op in getattr(block, section) or []:
                if slice_loop(op):
                    forwarded += self.forward(op) + self.store_vectors(op)
        # a tile written only to be stored, its stores now from the vectors:
        # the writes go - dead where nothing on the same path reads the tile
        # later (the cases of a dispatch are separate paths)
        common = [op for b in program.blocks for section in SECTIONS
                  for op in (getattr(b, section) or [])]
        paths = [common] + [[op for b in case.blocks for section in SECTIONS
                             for op in (getattr(b, section) or [])] for case in program.cases]
        def reads_of(ops):
            out = set()
            for op in ops:
                for o in (op.block if isinstance(op, lsc_loop) else [op]):
                    out |= _read(o)
            return out
        everywhere = reads_of(common + [op for path in paths[1:] for op in path])
        for n, path in enumerate(paths):
            for pos, op in enumerate(path):
                if not slice_loop(op):
                    continue
                later = reads_of(path[pos + 1:]) if n else everywhere
                inside = reads_of([op])
                dead = [b for b in op.block if isinstance(b, lsc_move) and "slice" in b.properties
                        and rgt.TILE == b.rtypes[1] and _key(b.indices[1], rgt.TILE) not in later
                        and _key(b.indices[1], rgt.TILE) not in inside]
                if dead:
                    op.block = [b for b in op.block if b not in dead]
                    op.refresh()
                    forwarded += len(dead)
        return forwarded

    def store_vectors(self, loop) -> int:
        """
        A tile slice stored right after a vector was moved into it - nothing
        changing either between - is the vector stored: through a contiguous
        vector store at the same address
        """
        count, moved_in = 0, {}
        for op in loop.block:
            if isinstance(op, lsc_move) and "slice" in op.properties and rgt.TILE == op.rtypes[1]:
                moved_in[_key(op.indices[1], rgt.TILE)] = op.indices[0]
                continue
            if isinstance(op, lsc_store) and rgt.TILE == op.rtypes[1] and \
                    _key(op.indices[1], rgt.TILE) in moved_in:
                vector = moved_in[_key(op.indices[1], rgt.TILE)]
                dt = self.ctx.component_dts.get(op.indices[0].component)
                sigs = [s for s in self.ctx.gen.store.get_signatures()
                        if rgt.VEC == s.operands["adreg"].rtype and dt == s.operands["adreg"].dt
                        and not s.operands["adreg"].modifiers
                        and {m.name for m in s.modifiers} <= {"MASK"}]
                if sigs:
                    op.indices[1] = vector
                    op.rtypes = [op.rtypes[0], rgt.VEC]
                    op.sigs = sigs
                    for k in ("slice_reg", "slice_imm"):
                        op.properties.pop(k, None)
                    count += 1
                    continue
            written = _written(op)
            for tile in [t for t, v in moved_in.items() if t in written or _key(v, rgt.VEC) in written]:
                del moved_in[tile]
        if count:
            loop.refresh()
        return count

    @staticmethod
    def forward(loop) -> int:
        count = 0
        last_in: dict = {}      # tile -> the vector last moved into it
        rename: dict = {}       # vector moved out -> the vector it equals
        block = []
        for op in loop.block:
            # readers of a forwarded vector read the one it equals
            for p in getattr(op, "reads", []):
                k = _key(op.indices[p], _rtype(op, p))
                if k in rename:
                    op.indices[p] = rename[k][1]
            moved = isinstance(op, lsc_move) and "slice" in op.properties
            if moved and rgt.TILE == op.rtypes[0] and _key(op.indices[0], rgt.TILE) in last_in:
                # back out of the tile: the vector moved in
                rename[_key(op.indices[1], op.rtypes[1])] = (None, last_in[_key(op.indices[0], rgt.TILE)][1])
                count += 1
                continue
            written = _written(op)
            for tile in [t for t, (vec, _) in last_in.items() if t in written or vec in written]:
                del last_in[tile]
            for k in [k for k in rename if k in written]:
                del rename[k]
            if moved and rgt.TILE == op.rtypes[1]:
                last_in[_key(op.indices[1], rgt.TILE)] = (_key(op.indices[0], op.rtypes[0]), op.indices[0])
            block.append(op)
        if count:
            loop.block = block
            loop.refresh()
        return count


class hoist_slices(lsc_irmod):
    """
    A load in a loop over slices whose address doesn't move with the slices
    - alpha's and beta's broadcasts - and whose register nothing else in the
    loop writes runs once, before the loop
    """
    name = "hoist_slices"
    description = "hoist loads that don't move with the slices out of loops over slices"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = True
    constraints = "the load's walk steps by nothing; its register not written in the loop"

    def apply(self, program) -> int:
        hoisted = 0
        for block, section in blocks_and_sections(program):
            out = []
            for op in getattr(block, section) or []:
                if slice_loop(op):
                    before = self.hoist(op)
                    hoisted += len(before)
                    out += before
                out.append(op)
            setattr(block, section, out)
        return hoisted

    @staticmethod
    def hoist(loop) -> list:
        writes = {}
        for op in loop.block:
            for k in _written(op):
                writes[k] = writes.get(k, 0) + 1
        out, keep, walks, renumber = [], [], [], {}
        for op in loop.block:
            w = op.properties.get("walk") if isinstance(op, lsc_load) else None
            if w is not None and not dict(loop.walks[w].step.terms) \
                    and all(1 == writes.get(k, 0) for k in _written(op)):
                anchor = loop.walks[w].anchor
                anchor.properties.pop("walk", None)
                out.append(anchor)
                continue
            keep.append(op)
        if not out:
            return []
        for op in keep:
            if isinstance(op, (lsc_load, lsc_store)):
                w = op.properties.get("walk", 0)
                if w not in renumber:
                    renumber[w] = len(walks)
                    walks.append(loop.walks[w])
                op.add_property("walk", renumber[w])
        loop.block, loop.walks = keep, walks
        loop.refresh()
        return out
