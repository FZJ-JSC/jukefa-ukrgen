from .ukr import ukr_composition
from .gemm import gemm_composition
from .mm import mm_composition
from .pack import pack_composition

ukr_composition_map: dict[str, type[ukr_composition]] = {
    "gemm": gemm_composition,
    "mm": mm_composition,
    "pack": pack_composition,
}
