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
    Asks the memory layout of each memory component, per index:

        c  contiguous: unit stride
        p  packed: the slices along this index follow each other directly,
           so its stride is the extent of what lies inside it - known when
           the microtile size is, but not a parameter of the kernel
        s  strided: a stride given to the kernel at run time

    For example:

        --A-layout m:c k:p    a BLIS-packed A panel: element (m,k) at m + k*MR
        --C-layout m:c n:s    column-major C with a leading dimension
        --C-layout m:s n:s    general strides, contiguous along neither

    At most one index is contiguous: it is the innermost, and two would leave
    open which one that is. Packed indices need a contiguous one to be packed
    around; several nest in the order given, innermost first.

    To the solver, packed and strided are the same: a vector along either has
    its lanes apart in memory, so it is loaded or stored strided - by a
    strided access, a gather or scatter, or lane by lane. The difference is
    for addressing: moving along a packed index advances by a constant, while
    a strided one needs its stride at run time.
    """

    KINDS = {"c": "contiguous", "p": "packed", "s": "strided"}

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.indices = component_indices(context.composition)
        aliases = context.composition.storage_aliases
        for comp, indices in self.indices.items():
            example = " ".join(f"{i}:{'c' if 0 == n else 'p'}" for n, i in enumerate(indices))
            # an alias of C for one of its storages: that storage's layout
            from .ukr.storage import LAYOUTS
            preset = list(LAYOUTS[aliases[comp]]) if comp in aliases else None
            self.params[f"{comp}-layout"] = stage_param(
                    value=preset, default=preset, required=preset is None,
                    description=f"Layout of {comp}: for each of {', '.join(indices)}, "
                                f"c (contiguous), p (packed: slices follow each other) "
                                f"or s (strided at run time), e.g. {example}",
                    multi=True)

    def parse(self, comp : str, tokens : list[str]) -> dict[str, str]:
        """
        Per-index layout of a component, in the order given

        :raises stage_error: unless every index is given once as c, p or s, with
                             at most one contiguous, and packed ones only around
                             a contiguous one
        """
        indices = self.indices[comp]
        spec: dict[str, str] = {}
        for token in tokens:
            idx, sep, kind = token.partition(":")
            if not sep or kind not in self.KINDS or idx not in indices:
                raise stage_error(f"--{comp}-layout: {token} is not <index>:c, <index>:p or "
                                  f"<index>:s for an index of {comp} ({', '.join(indices)})")
            if idx in spec:
                raise stage_error(f"--{comp}-layout gives {idx} twice")
            spec[idx] = kind
        missing = [i for i in indices if i not in spec]
        if missing:
            raise stage_error(f"--{comp}-layout is missing {', '.join(missing)}")
        contiguous = [i for i, k in spec.items() if "c" == k]
        if len(contiguous) > 1:
            raise stage_error(
                f"--{comp}-layout: {comp} cannot be contiguous along both "
                f"{' and '.join(contiguous)} - only one is innermost. If the slices along "
                f"the other follow each other directly, as in a packed panel, it is "
                f"packed: {contiguous[0]}:c {contiguous[1]}:p")
        packed = [i for i, k in spec.items() if "p" == k]
        if packed and not contiguous:
            raise stage_error(
                f"--{comp}-layout: {comp} is packed along {', '.join(packed)} but contiguous "
                f"along none - packed slices follow each other, each of them contiguous")
        return spec

    def progress(self):
        strides = {comp: self.parse(comp, self.params[f"{comp}-layout"].value or [])
                   for comp in self.indices}
        self.context.component_strides = strides
        self.context.component_layouts = {
            comp: next((i for i, k in spec.items() if "c" == k), None)
            for comp, spec in strides.items()}
        # innermost first: the contiguous index, then the packed ones in the
        # order given. A packed index's stride is the extent of those before it.
        self.context.component_packing = {
            comp: [i for i, k in spec.items() if "c" == k] +
                  [i for i, k in spec.items() if "p" == k]
            for comp, spec in strides.items()}
        self.context.params.update(self.params)
        return []
