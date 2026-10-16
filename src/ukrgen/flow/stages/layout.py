"""
Memory layout of the microkernel's components
"""

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, stage_error
from .ukr.ukr import storage_class, sto_kind


def component_indices(composition) -> dict[str, tuple[str, ...]]:
    """
    Indices each memory component varies along, in its first compute STO
    """
    found: dict[str, tuple[str, ...]] = {}
    for sto in composition.get_sto_descriptions():
        if sto_kind.COMPUTE != sto.kind:
            continue
        for op in sto.operands:
            comp = composition.get_component(op)
            live = sto.live_indices(op)
            if storage_class.MEMORY == comp.storage and live:
                found.setdefault(op, live)
    return found


class layout_stage(stage):
    """
    Asks the memory layout of each memory component, per index: c if it is
    contiguous along the index (unit stride), s if strided:

        --A-layout m:c k:s    column-major A with a leading dimension
        --C-layout m:s n:s    general strides, contiguous along neither

    Any combination is allowed except two contiguous indices, which no 2-D
    layout has. A vector a solution runs along a strided index is loaded or
    stored strided - by a strided access, a gather or scatter, or lane by
    lane - and which of those exist depends on the ISA, so they are among the
    candidates rather than chosen here.
    """

    KINDS = {"c": "contiguous", "s": "strided"}

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.indices = component_indices(context.composition)
        for comp, indices in self.indices.items():
            example = " ".join(f"{i}:{'c' if 0 == n else 's'}" for n, i in enumerate(indices))
            self.params[f"{comp}-layout"] = stage_param(
                    value=None,
                    description=f"Layout of {comp}: for each of {', '.join(indices)}, "
                                f"c (contiguous) or s (strided), e.g. {example}",
                    multi=True)

    def parse(self, comp : str, tokens : list[str]) -> dict[str, str]:
        """
        Per-index layout of a component

        :raises stage_error: unless every index is given once as c or s, with
                             at most one contiguous
        """
        indices = self.indices[comp]
        spec: dict[str, str] = {}
        for token in tokens:
            idx, sep, kind = token.partition(":")
            if not sep or kind not in self.KINDS or idx not in indices:
                raise stage_error(f"--{comp}-layout: {token} is not <index>:c or <index>:s "
                                  f"for an index of {comp} ({', '.join(indices)})")
            if idx in spec:
                raise stage_error(f"--{comp}-layout gives {idx} twice")
            spec[idx] = kind
        missing = [i for i in indices if i not in spec]
        if missing:
            raise stage_error(f"--{comp}-layout is missing {', '.join(missing)}")
        contiguous = [i for i, k in spec.items() if "c" == k]
        if len(contiguous) > 1:
            raise stage_error(f"--{comp}-layout: {comp} cannot be contiguous along both "
                              f"{' and '.join(contiguous)}")
        return spec

    def progress(self):
        strides = {comp: self.parse(comp, self.params[f"{comp}-layout"].value or [])
                   for comp in self.indices}
        self.context.component_strides = strides
        self.context.component_layouts = {
            comp: next((i for i, k in spec.items() if "c" == k), None)
            for comp, spec in strides.items()}
        self.context.params.update(self.params)
        return []
