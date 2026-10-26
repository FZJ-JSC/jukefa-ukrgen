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
    for block in composition.all_blocks():
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
                                f"chosen implementations; one value per part of the "
                                f"microtile where it is split along {idx} - the parts "
                                f"one after another along it",
                    multi=True)

        loops = [b.loop_index for b in composition.all_blocks() if b.is_loop]
        default = loops + [i for i in self.indices if i not in loops]
        self.params["order"] = stage_param(
                value=",".join(default),
                default=",".join(default),
                description="Tiling order, outermost index first, comma separated "
                            "(single-letter indices may be run together: kmn)",
                required=False)

    def progress(self):
        values = {}
        for idx in self.indices:
            raw = self.params[idx].value
            raw = raw if isinstance(raw, (list, tuple)) else [raw]
            for value in map(str, raw):
                if not value.isdigit() or int(value) < 1:
                    raise stage_error(f"--{idx} must be positive integers, got {value}")
            values[idx] = [int(v) for v in raw]
        split = [idx for idx, v in values.items() if len(v) > 1]
        if len(split) > 1:
            raise stage_error(f"the microtile is split along one index, not {', '.join(split)}: "
                              f"give one of them a value per part")
        parts = len(values[split[0]]) if split else 1
        wanted = len(self.context.to_parts or [None])
        if split and parts != wanted:
            raise stage_error(f"--{split[0]} gives {parts} parts, the implementations "
                              f"(--<sto>-to) {wanted}")
        self.context.split_index = split[0] if split else None
        self.context.part_dims = [{idx: v[p] if len(v) > 1 else v[0] for idx, v in values.items()}
                                  for p in range(max(parts, wanted))]
        dims = self.context.part_dims[0]

        raw = self.params["order"].value
        order = raw.split(",") if "," in raw else list(raw)
        if sorted(order) != sorted(self.indices):
            raise stage_error(f"--order must list each of {self.indices} once, got {raw}")

        self.context.dims = dims
        self.context.order = tuple(order)
        self.context.params.update(self.params)
        return []
