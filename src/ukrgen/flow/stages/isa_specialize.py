"""
Specializing the LSC IR for the ISA
"""

import logging

from asmgen.registers import adt_size

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...lsc_model.addressing import arg_value, kernel_values
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
                            "address register walks forward. A number, or an expression of the "
                            "kernel's sizes m, n, k and e, its element size - side by side a "
                            "product - with min and max: ne, one k step of a vm family's B; "
                            "min(ne, 16e-1), within the K1's and K3's free window")

    def imm_limit(self) -> int | None:
        """
        --max-imm-offset for this kernel: a number, or its expression of the
        kernel's sizes and element size evaluated (e where the components
        share one); at least 1
        """
        limit = self.params["max-imm-offset"].value
        if limit in (None, ""):
            return None
        sizes = {adt_size(dt) for dt in self.context.component_dts.values()}
        value = arg_value(str(limit), kernel_values(self.context.dims, sizes.pop() if 1 == len(sizes) else None))
        if value < 1:
            raise stage_error(f"--max-imm-offset {limit} is {value} bytes for this kernel")
        return value

    def progress(self):
        try:
            for program in self.context.programs:
                sp = signature_specializer(self.context, program)
                sp.max_imm_offset = self.imm_limit()
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
