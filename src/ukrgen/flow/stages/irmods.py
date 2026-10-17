"""
IR modifications on the specialized LSC IR
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...lsc_model.irmods import IRMODS, MODEL_IRMODS


class irmod_stage(stage):
    """
    Runs IR modifications over every part's specialized program, in the order
    given:

        ldinc  fuse address computations into post-increment accesses, where
               the accesses' signatures post-increment

    --print-modified-ir prints the result and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("IRMOD").debug
        self.params["irmods"] = stage_param(
                value=["ldinc"], default=["ldinc"], multi=True, required=False,
                choices=list(IRMODS),
                description="IR modifications to run, in order (default: ldinc)")
        self.params["print-modified-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the IR after the IR modifications and exit")

    def progress(self):
        for name in self.params["irmods"].value or []:
            for program in self.context.programs:
                IRMODS[name](self.context, program)
        text = "\n\n".join(p.render() for p in self.context.programs)
        if self.params["print-modified-ir"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)
        self.context.params.update(self.params)
        return []


class model_irmod_stage(stage):
    """
    Runs IR modifications over the model's IR, before specialization for the
    ISA, in the order given:

        lanefuse  fuse loads into all lanes of a register into one load where
                  the lanes are contiguous
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.params["model-irmods"] = stage_param(
                value=["lanefuse"], default=["lanefuse"], multi=True, required=False,
                choices=list(MODEL_IRMODS),
                description="IR modifications before specialization, in order "
                            "(default: lanefuse)")

    def progress(self):
        for name in self.params["model-irmods"].value or []:
            for program in self.context.programs:
                MODEL_IRMODS[name](self.context, program)
        self.context.params.update(self.params)
        return []
