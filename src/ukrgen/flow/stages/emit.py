"""
Emitting the specialized LSC IR as assembly
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...specializers.signature import signature_emitter, specialization_error


class emit_stage(stage):
    """
    Emits every part's specialized program as assembly: for each operation the
    signature that fits, called through asmgen, with physical registers.
    Codegen's instruction-level part; loop control and the dispatch on cases
    are still to come.

    The result's bases are the registers to bind to the kernel's arguments:
    base addresses, and run-time strides in bytes.

    --print-asm prints the assembly and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("EMIT").debug
        self.params["print-asm"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the emitted assembly and exit")

    def progress(self):
        try:
            self.context.emitted = [signature_emitter(self.context, p).emit()
                                    for p in self.context.programs]
        except specialization_error as err:
            raise stage_error(f"emitting: {err}") from err
        text = "\n\n".join(p.render() for p in self.context.emitted)
        if self.params["print-asm"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)
        self.context.params.update(self.params)
        return []
