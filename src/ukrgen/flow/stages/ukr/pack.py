"""
Packing microkernel: Y = kappa*X, as in BLIS packm
"""

from ....matching.math import expression_node as node, operand_ref as ref, operation as op

from .ukr import (
    ukr_composition,
    component_description as component,
    storage_class as storage,
    sto_description as sto,
    sto_kind,
    block_description as block,
    branch_description as branch,
    case_description as case,
    scalar,
)


class pack_composition(ukr_composition):
    """
    Each iteration of the loop over n scales a column of X by kappa and stores it
    into the packed buffer Y. The previous formulation pushed this through the mm
    generator with a square diagonal kappa tile, which is why it required n == k.

    kappa 1 - BLIS's usual - copies: Y = X, the copy's load its only work once
    copy propagation gives Y X's registers.
    """

    @classmethod
    def get_components(cls):
        return [
            component(name="X", storage=storage.MEMORY),
            component(name="Y", storage=storage.MEMORY),
            component(name="kappa", storage=storage.MEMORY,
                      dt_reference="Y", parameterized=False),
        ]

    @classmethod
    def get_sto_descriptions(cls):
        return [
            sto(name="copy", kind=sto_kind.COMPUTE, generator="pack",
                req=node(op.MOVE, ref(name="Y", indices=("m", "n")),
                         ref(name="X", indices=("m", "n")))),
            sto(name="pack", kind=sto_kind.COMPUTE, generator="pack",
                req=node(op.MOVE, ref(name="Y", indices=("m", "n")),
                         node(op.MUL, ref(name="X", indices=("m", "n")), scalar("kappa")))),
            sto(name="store", kind=sto_kind.STORE, store_components=("Y",)),
        ]

    @classmethod
    def get_blocks(cls):
        return [
            branch(cases=(
                case(when={"kappa": 1}, blocks=(
                    block(stos=("copy", "store"), loop_index="n", preload=True, tail=True),)),
                case(blocks=(
                    block(stos=("pack", "store"), loop_index="n", preload=True, tail=True),)),
            )),
        ]
