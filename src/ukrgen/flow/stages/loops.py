"""
The loops stage: the loops of the specialized IR made
"""

from ..ukr_context import ukr_context
from .stage import stage, stage_error
from ...specializers.signature import specialization_error


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
                            if sp is not None and id(loop) not in made:
                                sp.forms(loop)
                            made[id(loop)] = loop
                            out.append(loop)
                        else:
                            out.append(op)
                    setattr(block, section, out)
        except specialization_error as err:
            raise stage_error(f"specializing for the ISA: {err}") from err
        self.context.params.update(self.params)
        return []
