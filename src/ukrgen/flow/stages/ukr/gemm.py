"""
gemm microkernel: C = beta*C + alpha*A*B
"""

from ....matching.math import expression_node as node, operand_ref as ref, operation as op

from .ukr import (
    ukr_composition,
    component_description as component,
    storage_class as storage,
    sto_description as sto,
    sto_kind,
    block_description as block,
    scalar,
)


class gemm_composition(ukr_composition):
    """
    A*B accumulates in registers over k, then C is scaled by beta, alpha*AB is
    added and the result stored.
    """

    @classmethod
    def get_components(cls):
        return [
            component(name="A", storage=storage.MEMORY),
            component(name="B", storage=storage.MEMORY),
            component(name="AB", storage=storage.REGISTER),
            component(name="C", storage=storage.MEMORY),
            component(name="alpha", storage=storage.MEMORY,
                      dt_reference="C", parameterized=False),
            component(name="beta", storage=storage.MEMORY,
                      dt_reference="C", parameterized=False),
        ]

    @classmethod
    def get_sto_descriptions(cls):
        return [
            sto(name="mm", kind=sto_kind.COMPUTE, generator="mm",
                req=node(op.MOVE, ref(name="AB", indices=("m", "n")),
                         node(op.ADD, ref(name="AB", indices=("m", "n")),
                              node(op.REDUCE_SUM,
                                   node(op.MUL, ref(name="A", indices=("m", "k")),
                                                ref(name="B", indices=("k", "n"))),
                                   reduce_dim="k")))),
            sto(name="betascale", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.MUL, ref(name="C", indices=("m", "n")), scalar("beta")))),
            sto(name="alphascale", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.ADD, ref(name="C", indices=("m", "n")),
                              node(op.MUL, ref(name="AB", indices=("m", "n")),
                                   scalar("alpha"))))),
            sto(name="store", kind=sto_kind.STORE, store_components=("C",)),
        ]

    @classmethod
    def get_blocks(cls):
        return [
            block(stos=("mm",), loop_index="k", preload=True, tail=True),
            block(stos=("betascale", "alphascale", "store")),
        ]
