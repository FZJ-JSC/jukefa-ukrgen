"""
Data types of the microkernel's components
"""

import logging

from asmgen.registers import asm_data_type as adt

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage
from ...support.op import op_support_builder


def dt_names(dts) -> list[str]:
    """
    Every name, aliases included, that refers to one of the given data types.

    Iterating asm_data_type skips aliases (FP64 for DOUBLE, FP32 for SINGLE, ...),
    so the names are taken from __members__ to accept either spelling.

    :param dts: data types to name
    :return: sorted names
    """
    wanted = set(dts)
    return sorted(name for name, dt in adt.__members__.items() if dt in wanted)


class datatype_stage(stage):
    """
    Asks for the data type of every component that has one of its own.

    The choices are every data type the ISA can load or store, not only those
    some full implementation supports: checking matches and data resolutions for
    every combination takes minutes. A combination that turns out to be
    unsupported is reported by the stage that solves for implementations.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        self.debug = logging.getLogger("DATATYPE").debug

        osb = op_support_builder(gen=context.gen)
        osb.determine_base_support()
        context.osb = osb

        choices = dt_names(osb.get_all_ldst_opd_dts())

        for comp in context.composition.get_typed_components():
            self.params[f"{comp}-data-type"] = stage_param(
                    value=None,
                    description=f"Data type of {comp}",
                    choices=choices)

    def progress(self):
        composition = self.context.composition

        own = {comp: adt[self.params[f"{comp}-data-type"].value]
               for comp in composition.get_typed_components()}

        self.context.component_dts = {
            comp.name: own[composition.dt_source(comp.name)]
            for comp in composition.get_components()}

        self.debug(f"component data types: {self.context.component_dts}")

        self.context.params.update(self.params)
        return []
