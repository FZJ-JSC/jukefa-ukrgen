"""
bind_operands: the registers an operation's signature names carried by the
operation

A load's, store's, move's or transformation's `indices` are the register
operands the *model* made; a signature names more - a governing predicate
(`amreg`), a slice's index register, an operand the instruction clobbers. This
pass carries them in the operation: an index slot with its register type, a
read (and a write, where the instruction writes it too), so that liveness, the
renamer and the allocation see the value the emitter binds by name
(docs/REGISTER_ALLOCATION.md: *the signatures' operands in the IR*).
"""
from __future__ import annotations

from asmgen.asmblocks.op import operand_role as orl

from ...models.lsc.index import lsc_reg_index
from ...specializers.signature import _sigs
from ...models.lsc.allocator_decisions import sections
from ...models.lsc.operations import lsc_set, lsc_load, lsc_move, lsc_store, lsc_transformation
from .base import lsc_irmod, irmod_placement, blocks_and_sections


def _group(op):
    """The signatures an operation may take, or None where it has none yet"""
    if isinstance(op, lsc_transformation):
        return op.resolution.compute_sg if op.resolution is not None else None
    return op.sigs


def mask_operand(sigs : list) -> tuple | None:
    """
    The signature operand every one of the signatures masks with, where they
    all name the same one
    :param sigs: the signatures an operation may take
    :return: (name, rtype), or None where they disagree or none is masked
    """
    found = None
    for sig in sigs:
        masks = [(name, shape.rtype) for name, shape in sig.operands.items()
                 if orl.MASK == shape.orole]
        if 1 != len(masks):
            return None
        if found is not None and found != masks[0]:
            return None
        found = masks[0]
    return found


def bind_mask(op, sigs : list | None = None, live : bool = False,
              rtypes : dict | None = None) -> bool:
    """
    The mask a masked operation takes, as a slot of its own
    :param op: the operation
    :param sigs: the signatures it may take - its own where None
    :param rtypes: the mask values the program already names, their register
                  types - a tail's mask is the type its set gave it, not each
                  access's signature's (RVV's v0 is VEC to the instruction and
                  a mask to the IR)
    :param live: whether the slot is also read (and written, where the
                 instruction clobbers it: AVX's gathers) - the passes after
                 this one see it live then, which changes what they emit, so
                 the reading is a step of its own (phase (b) of
                 docs/REGISTER_ALLOCATION.md)
    :return: whether it was bound
    """
    sigs = _sigs(_group(op)) if sigs is None else list(sigs)
    if not sigs:
        return False
    mask = mask_operand(sigs)
    if mask is None:
        return False
    name, rtype = mask
    if any(slot is not None and slot == name for slot in (op.hw_operands or [])):
        return False
    # the value's name: what the program calls this mask already (a masked
    # tail's `mask(m)`), else the operand's own name
    tail = op.properties.get("tail")
    component = f"mask({tail})" if tail is not None else "mask"
    rtype = (rtypes or {}).get(component, rtype)
    slot = len(op.indices)
    op.indices.append(lsc_reg_index(component, [0]))
    op.rtypes = list(op.rtypes or []) + [rtype]
    op.reg_types = list(op.reg_types) + [op.reg_types[0]]
    op.hw_operands = list(op.hw_operands or [None] * slot) + [name]
    op.mask_slot = slot
    if live:
        op.reads = list(op.reads) + [slot]
        if any(name in (sig.clobber_list or []) for sig in sigs):
            op.writes = list(op.writes) + [slot]
    return True


class bind_operands(lsc_irmod):
    """
    Every operation carries the registers its chosen signature names, the
    masks first: what the emitter used to bind by name at emission time is a
    value the passes before it can see. Nothing reads the new slots yet, so
    the kernels are byte for byte the same.
    """
    name = "bind_operands"
    description = "the signatures' register operands carried by the operations"
    placement = irmod_placement.POST_SPECIALIZE
    required = True

    @classmethod
    def triggered(cls, ctx) -> bool:
        """
        Every kernel's operations carry their signatures' registers
        :param ctx: the context after specialization
        :return: True, always
        """
        return True

    def apply(self, program) -> int:
        """
        Bind the accesses' register operands: a load's, store's or move's mask
        - a transformation's later, its slots the builder's own and its
        `hw_operands` zipped with them whole at emission (phase (b) of
        docs/REGISTER_ALLOCATION.md)
        :param program: the IR, specialized for the ISA
        :return: how many operations were bound
        """
        bound = 0
        # the mask values the program sets, their types: an access takes the
        # type of the value, not its own signature's spelling of it
        known = {op.indices[0].component: op.rtypes[0] for op in program.entry
                 if isinstance(op, lsc_set)}
        # every run of operations, a loop's among them: a loop over slices
        # holds the accesses that carry a tail's mask
        for run in sections(program):
            for op in run:
                if isinstance(op, (lsc_load, lsc_store, lsc_move)):
                    # a masked access reads the mask the tail's set wrote -
                    # the slot the emitter resolves at emission
                    # (docs/REGISTER_ALLOCATION.md: the masks, (b))
                    bound += 1 if bind_mask(op, live=True, rtypes=known) else 0
        return bound
