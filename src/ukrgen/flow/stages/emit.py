"""
Emitting the specialized LSC IR as assembly
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...emitters.signature import signature_emitter, emit_program
from ...specializers.signature import specialization_error


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
        self.params["loop-align"] = stage_param(
                value=None, required=False,
                description="Loops' heads on a boundary of this many bytes (a power of two): "
                            ".balign before each loop's label - the code falling into the loop "
                            "runs the padding's nops once")
        self.params["loop-gregs"] = stage_param(
                value=None, required=False,
                description="General registers a loop over tiles' slices may take beyond what "
                            "lives around it - counter, slice index, pointers: within it, an "
                            "access column (tiles a vector length apart sharing one) gets a "
                            "pointer of its own, stepped once an iteration; beyond, the "
                            "plan's address registers walk from tile to tile. Not given: no "
                            "limit")

    def progress(self):
        value = self.params["loop-gregs"].value
        if value is not None and (not str(value).isdigit() or int(value) < 2):
            raise stage_error(f"--loop-gregs takes at least 2 (a counter and a slice index), "
                              f"got {value}")
        self.context.loop_gregs = int(value) if value is not None else None
        align = self.params["loop-align"].value
        if align not in (None, "") and (int(align) <= 0 or int(align) & (int(align) - 1)):
            raise stage_error(f"--loop-align {align}: a power of two")
        self.context.loop_align = int(align) if align not in (None, "") else None
        try:
            self.context.emitted = [emit_program(self.context, p)
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
