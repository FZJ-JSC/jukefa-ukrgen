"""
The loops stage: the loops of the specialized IR made
"""

from ..ukr_context import ukr_context
from .stage import stage, stage_error
from ...specializers.signature import specialization_error
from ...models.lsc.offset_polynomial import offset_polynomial as offpoly


#: the walking pointer's address register: no component's own
WALKER = 1 << 20


def _scalar_of(idx, e):
    """A copy's scalar: the template's tile, numbered by its copy"""
    import copy as _copy
    new = _copy.copy(idx)
    new.indices = [e] + list(idx.indices[1:])
    return new


def copies(loop, program=None) -> None:
    """
    A loop over a vector's elements, its copies made: one element's operations
    once a copy (the loop's unroll), in the order the loop runs them - a batch
    of loads (as many as its scalars' registers), then their fills; or an
    extract, the shift and the store an element - each with its copy number
    and its role (load, fill; extract, shift, store), its scalar a virtual tile
    of its own. As many loads ahead of their fills as the registers asked
    (--...-subtiling registers, unroll_loops' registers): a cap on the scalars
    in flight. The emitter's loop emits the body as it is; the scheduler leaves
    its order (each access's element is the walker's steps before it - not IR
    steps yet: ADDRESSING_PLAN 6.4)
    """
    from ...models.lsc.builder import _clone
    if "slices" == loop.info.get("kind") or loop.info.get("copies") \
            or loop.info.get("direction") not in ("load", "store"):
        return
    unroll = loop.subtiling.unroll
    count = max(1, min(loop.subtiling.registers, unroll))

    # the scalar an element passes through (a load's data, an extract's): a
    # virtual tile of each copy's own - S0, S1 - allocated as written, free
    # after its last read (the emitter)
    template = loop.block[0] if "load" == loop.info["direction"] else loop.block[1]
    scalar = template.indices[1].component

    def copy_of(op, e, role):
        new = _clone(op)
        new.indices = [_scalar_of(idx, e) if idx.component == scalar else idx for idx in new.indices]
        new.properties["copy"] = e
        new.properties["role"] = role
        return new
    # the walking pointer the emitter sets up (from the anchor's element, the
    # element count its counter): each access at it, then a step of it - an
    # address step of the IR, so an access's element is the steps before it
    # whatever the order the scheduler gives the rest
    from ...models.lsc.operations import lsc_addr_compute, lsc_reg_index, scalar_tile
    from ...models.lsc.addressing import offpoly
    comp = loop.walks[0].anchor.indices[0].component

    index = loop.info.get("index")
    backwards = loop.subtiling.order < 0

    def at_walker(access, e, role):
        new = copy_of(access, e, role)
        new.indices = [lsc_reg_index(comp, [WALKER])] + list(new.indices[1:])
        if program is not None and index is not None:
            # its element's offset - the anchor's, e on along the loop's index
            # (from the last back: VL - 1 - e) - where the walker's steps put it
            amount = offpoly._make({("VL",): 1, (): -1 - e}) if backwards else offpoly.const(e)
            new.offset = program.offsets.shifted(access.offset, index, amount)
        # the walk's step - back, for a fill from the last element (SVE's insr)
        step = loop.walks[0].step if loop.subtiling.order >= 0 else offpoly.const(0) - loop.walks[0].step
        bump = lsc_addr_compute(comp, WALKER, WALKER, step, scalar_tile)
        bump.properties["copy"] = e
        bump.properties["role"] = "bump"
        return [new, bump]
    body = []
    if "load" == loop.info["direction"]:
        load, fill = loop.block
        for start in range(0, unroll, count):
            batch = range(start, min(unroll, start + count))
            body += [o for e in batch for o in at_walker(load, e, "load")]
            body += [copy_of(fill, e, "fill") for e in batch]
    else:
        extract, store, shift = loop.block
        for e in range(unroll):
            body += [copy_of(extract, e, "extract"), copy_of(shift, e, "shift")] + at_walker(store, e, "store")
    loop.block = body
    loop.info["copies"] = True
    loop.refresh()


class loop_stage(stage):
    """
    Each operation standing for a loop (a vector filled or drained element by
    element: program_builder.virtual) its loop - where the passes before left
    it, in every section - its forms the specializer's (its anchors' usable
    signatures), after isa_specialize's forms and before the addresses: the
    loop's copies, sections and preloads made here next (ADDRESSING_PLAN 6.3)
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

    def progress(self):
        from ...irmod.lsc.vectorize import loop_of
        from ...irmod.lsc.base import blocks_and_sections
        specializers = {id(sp.program): sp for sp in self.context.specializers or []}
        try:
            for program in self.context.programs or []:
                sp = specializers.get(id(program))
                made = {}
                for block, section in blocks_and_sections(program):
                    ops = getattr(block, section) or []
                    if not any(loop_of(op) is not None and loop_of(op) is not op for op in ops):
                        continue
                    out = []
                    for op in ops:
                        loop = loop_of(op)
                        if loop is not None and loop is not op:
                            if id(loop) not in made:
                                copies(loop, program)
                                if sp is not None:
                                    sp.forms(loop)
                            made[id(loop)] = loop
                            if loop.info.get("copies"):
                                # its walker set up by the addresses stage, where
                                # the anchor's walk leaves the register
                                loop.info["walker"] = True
                            out.append(loop)
                        else:
                            out.append(op)
                    setattr(block, section, out)
        except specialization_error as err:
            raise stage_error(f"specializing for the ISA: {err}") from err
        self.context.params.update(self.params)
        return []
