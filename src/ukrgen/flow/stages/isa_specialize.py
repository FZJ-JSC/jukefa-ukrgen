"""
Specializing the LSC IR for the ISA
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...specializers.signature import signature_specializer, specialization_error


class isa_specialize_stage(stage):
    """
    Adapts every part's program to the ISA, IR to IR, as pre-specialization
    did: afterwards every operation fits one of its signatures. An access
    offset by run-time strides goes through a column pointer, and one at an
    offset no addressing form takes through a scratch address register - both
    explicit address computations in the IR, for the irmods to fuse and the
    schedulers to place.

    Works from the program and the composition metadata only.

    --print-specialized-ir prints the adapted IR and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("SPECIALIZE").debug
        self.params["print-specialized-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the IR specialized for the ISA and exit")
        self.params["max-imm-offset"] = stage_param(
                value=None, required=False,
                description="Largest immediate offset in bytes, either sign, a load or store "
                            "uses (the number in the instruction on RISC-V and x86; AArch64 "
                            "encodes it divided by the access size): beyond it the access's "
                            "address register walks forward - the K1 seems to pay for fld "
                            "offsets above ~104 bytes")

    def progress(self):
        try:
            for program in self.context.programs:
                sp = signature_specializer(self.context, program)
                limit = self.params["max-imm-offset"].value
                sp.max_imm_offset = None if limit in (None, "") else int(limit)
                sp.specialize()
        except specialization_error as err:
            raise stage_error(f"specializing for the ISA: {err}") from err
        text = "\n\n".join(p.render() for p in self.context.programs)
        if self.params["print-specialized-ir"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)
        self.context.params.update(self.params)
        return []
