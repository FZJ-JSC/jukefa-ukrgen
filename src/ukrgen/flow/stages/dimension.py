"""
Microtile size along each index and the order to tile it in
"""

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, stage_error


def composition_indices(composition) -> list[str]:
    """
    Every index of the composition's STOs, in order of first appearance
    """
    indices = []
    for block in composition.get_blocks():
        for name in block.stos:
            for idx in composition.get_sto(name).indices:
                if idx not in indices:
                    indices.append(idx)
    return indices


class dimension_stage(stage):
    """
    Asks how many extents of the chosen implementations the microtile spans
    along each index (--m 2 with an SVE fma bound to m: two vectors), and the
    tiling order, outermost index first.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        composition = context.composition
        self.indices = composition_indices(composition)

        for idx in self.indices:
            self.params[idx] = stage_param(
                    value=None,
                    description=f"Microtile size along {idx}, in extents of the "
                                f"chosen implementations")

        loops = [b.loop_index for b in composition.get_blocks() if b.is_loop]
        default = loops + [i for i in self.indices if i not in loops]
        self.params["order"] = stage_param(
                value=",".join(default),
                default=",".join(default),
                description="Tiling order, outermost index first, comma separated "
                            "(single-letter indices may be run together: kmn)",
                required=False)

    def progress(self):
        dims = {}
        for idx in self.indices:
            value = str(self.params[idx].value)
            if not value.isdigit() or int(value) < 1:
                raise stage_error(f"--{idx} must be a positive integer, got {value}")
            dims[idx] = int(value)

        raw = self.params["order"].value
        order = raw.split(",") if "," in raw else list(raw)
        if sorted(order) != sorted(self.indices):
            raise stage_error(f"--order must list each of {self.indices} once, got {raw}")

        self.context.dims = dims
        self.context.order = tuple(order)
        self.context.params.update(self.params)
        return []
