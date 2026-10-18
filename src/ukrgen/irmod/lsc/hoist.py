"""
Loads a loop doesn't change, once before it
"""

from ...models.load_store_operations import lsc_load, lsc_store, lsc_transformation, lsc_move, lsc_loop
from .base import irmod_placement, lsc_irmod


class hoist(lsc_irmod):
    """
    A loop loading something its index doesn't index - a packing kernel's
    kappa, broadcast - loads it again every iteration. Where nothing in the
    loop writes the registers it goes into but those loads, one load before
    the loop does: the block's init, which runs before the check skipping the
    loop, so a run with only the tail has it too.
    """
    name = "hoist"
    description = "load what a loop doesn't change once, before it"
    placement = irmod_placement.PRE_SPECIALIZE
    default_enabled = True
    constraints = ("the component isn't indexed by the loop's index, and only its loads "
                   "write the registers they go into")

    @staticmethod
    def written(op) -> set:
        """
        The registers an operation writes: a load's data register, an
        arithmetic operation's or a move's last operand
        """
        # a load's data and a move's destination are their second index, an
        # arithmetic operation's result its first
        if isinstance(op, (lsc_load, lsc_move)):
            idx = op.indices[1]
        elif isinstance(op, lsc_transformation):
            idx = op.indices[0]
        elif isinstance(op, lsc_loop):
            return {(op.indices[p].component, op.indices[p].indices[0]) for p in op.writes}
        else:
            return set()
        return {(idx.component, idx.indices[0])}

    def apply(self, program) -> int:
        changed = 0
        for block in program.blocks + [b for c in program.cases for b in c.blocks]:
            if block.loop_index is None:
                continue
            k = block.loop_index
            sections = ("body", "epilogue", "tail")
            ops = [op for s in sections for op in getattr(block, s) or []]
            invariant = {}
            for op in ops:
                if isinstance(op, lsc_load):
                    comp = op.indices[0].component
                    if k not in program.strides.get(comp, {}):
                        invariant.setdefault(next(iter(self.written(op))), []).append(op)
            others = set()
            for op in ops:
                if not (isinstance(op, lsc_load) and op.indices[0].component in
                        {c for c, _ in invariant}):
                    others |= self.written(op)
            hoisted = []
            for reg, loads in sorted(invariant.items(), key=lambda kv: str(kv[0])):
                # the same element every time: offset records are made per
                # access, so their contents compare
                where = {(program.offsets[l.offset].elements, str(l.rsln)) for l in loads}
                if reg in others or len(where) != 1:
                    continue
                first = loads[0]
                first.add_property("hoisted", True)
                hoisted.append(first)
                for s in sections:
                    setattr(block, s, [op for op in getattr(block, s) or [] if op not in loads])
                changed += 1
            block.prologue = hoisted + list(block.prologue)
        return changed
