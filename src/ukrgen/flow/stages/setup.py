"""
First stage: which ISA, which microkernel
"""

from ..isa_map import asmgen_map, make_generator
from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage
from .isaparam import isaparam_stage
from .ukr import ukr_composition_map


class setup_stage(stage):
    """
    Asks for the ISA and the microkernel only. Allocates the asmgen generator and
    selects the composition describing the kernel's STOs; everything later stages
    ask for depends on these two.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        self.params["isa"] = stage_param(
                value=None,
                description="Instruction set to generate for",
                choices=list(asmgen_map.keys()))
        self.params["ukr"] = stage_param(
                value="gemm",
                default="gemm",
                description="Microkernel to generate",
                choices=list(ukr_composition_map.keys()),
                required=False)
        self.params["C-storage"] = stage_param(
                value=None, required=False, multi=True,
                description="C's storages (row, col, any) as branches of the epilogue, picked "
                            "at run time by C's strides; the last the default, its layout "
                            "--C-layout's")

    def progress(self):
        isa = self.params["isa"].value
        ukr = self.params["ukr"].value

        self.context.gen = make_generator(isa)

        composition = ukr_composition_map[ukr]
        composition.validate()
        storages = self.params["C-storage"].value
        if storages and len(storages) > 1:
            from .ukr.storage import storage_branches
            composition = storage_branches(composition, storages)
        self.context.composition = composition

        self.context.params.update(self.params)

        if self.context.gen.get_parameters():
            return [isaparam_stage]
        return []
