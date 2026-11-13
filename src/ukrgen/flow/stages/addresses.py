"""
The addresses stage: the specializer's second half
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...models.lsc.decisions import decide
from ...specializers.signature import specialization_error


class address_stage(stage):
    """
    The addresses of the specialized IR - positions, walks, moves back,
    advances, immediates, offsets - placed by the specializer isa_specialize
    made (its forms done, its state carried), then the processor state the
    accesses' forms need. Apart from isa_specialize so a loop's copies can be
    made between (ADDRESSING_PLAN 6.2-6.4).
    --print-specialized-ir prints the IR specialized for the ISA and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("SPECIALIZE").debug
        self.params["print-specialized-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the IR specialized for the ISA and exit")

    def progress(self):
        try:
            for sp in self.context.specializers or []:
                sp.place()
            # the operations generated for every path: the ones whose decision
            # the allocation left dropped here, before the loops and the
            # scheduler see them (docs/REGISTER_ALLOCATION.md: decisions) - no
            # decision is taken yet, so nothing carries one and this keeps all
            for program in self.context.programs:
                decide(program, program.decisions)
        except specialization_error as err:
            raise stage_error(f"specializing for the ISA: {err}") from err
        text = "\n\n".join(p.render() for p in self.context.programs)
        if self.params["print-specialized-ir"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)
        self.context.params.update(self.params)
        return []
