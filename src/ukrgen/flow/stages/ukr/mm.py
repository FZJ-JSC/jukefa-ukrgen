"""
mm microkernel: C = A*B
"""

from ....matching.math import expression_node as node, operand_ref as ref, operation as op

from .ukr import (
    ukr_composition,
    component_description as component,
    component_init,
    storage_class as storage,
    sto_description as sto,
    sto_kind,
    block_description as block,
)


class mm_composition(ukr_composition):
    """
    C accumulates A*B in registers over k, starting from zero, and is stored.
    """

    @classmethod
    def get_components(cls):
        return [
            component(name="A", storage=storage.MEMORY),
            component(name="B", storage=storage.MEMORY),
            # C is overwritten, not accumulated into: its first read sees zero
            component(name="C", storage=storage.MEMORY, init=component_init.ZERO),
        ]

    @classmethod
    def get_sto_descriptions(cls):
        return [
            sto(name="mm", kind=sto_kind.COMPUTE, generator="mm",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.ADD, ref(name="C", indices=("m", "n")),
                              node(op.REDUCE_SUM,
                                   node(op.MUL, ref(name="A", indices=("m", "k")),
                                                ref(name="B", indices=("k", "n"))),
                                   reduce_dim="k")))),
            sto(name="store", kind=sto_kind.STORE, store_components=("C",)),
        ]

    @classmethod
    def get_blocks(cls):
        return [
            block(stos=("mm",), loop_index="k", preload=True, tail=True),
            block(stos=("store",)),
        ]
