"""
A component's storages as branches of the kernel's epilogue: what the
composition's components are, now that the ukr is known
"""
import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, stage_error
from .ukr.storage import storage_branches

#: the storages a component's storage option takes, the last the default
STORAGES = ("row", "col", "any")


class storage_stage(stage):
    """
    A component's storages (--C-storage, --Y-storage, ...): each but the last a
    branch of the kernel's epilogue, picked at run time by the component's
    stride along its contiguous index, the last the default (the component
    itself, its layout --C-layout's).

    The options are declared here, not with the ISA's and the ukr's: the
    composition's components are only known once the ukr has been chosen, and
    what they expand into is the composition itself (alias components, one
    case each, the epilogue's STOs copied to reference them) - so they are
    applied before the layout stage reads the composition, and after the stage
    that chose the ukr
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("STORAGE").debug
        # the composition the setup stage built: its components are what the
        # options are for (a component without a storage option, like A, takes
        # none)
        for comp in context.composition.get_components():
            self.params[f"{comp.name}-storage"] = stage_param(
                    value=[], required=False, multi=True,
                    description=f"{comp.name}'s storages ({', '.join(STORAGES[:-1])}, "
                                f"{STORAGES[-1]}) as branches of the epilogue, picked at run "
                                f"time by {comp.name}'s strides; the last the default, its layout "
                                f"--{comp.name}-layout's")

    def progress(self):
        """
        Expand the composition: one alias component and one case per storage
        before the default, the epilogue's STOs copied to reference them
        """
        composition = self.context.composition
        for comp in [c.name for c in composition.get_components()]:
            storages = self.params[f"{comp}-storage"].value
            if not isinstance(storages, list) or not storages:
                continue
            for s in storages:
                if s not in STORAGES:
                    raise stage_error(f"--{comp}-storage {s}: one of {', '.join(STORAGES)}")
            if len(storages) > 1:
                composition = storage_branches(composition, storages, comp)
                self.debug(f"{comp}: storages {storages} as branches")
        self.context.composition = composition
        return []
