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
    branch_description as branch,
    case_description as case,
    scalar,
)


class gemm_composition(ukr_composition):
    """
    A*B accumulates in registers over k; then the epilogue depends on alpha
    and beta, each case with STOs of its own:

        beta 0, alpha 1    C = AB           store AB into C
        beta 0             C = alpha*AB     C is never read
        beta 1, alpha 1    C = C + AB
        beta 1             C = C + alpha*AB
        alpha 1            AB = AB + beta*C, stored into C: one fma
        otherwise          C = beta*C, then C = C + alpha*AB

    beta 0 is a correctness case, not only an optimization: C is not read, so
    NaNs or infinities in it do not survive. alpha 0 is handled before the
    kernel is called.
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
            sto(name="alphamul", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.MUL, ref(name="AB", indices=("m", "n")), scalar("alpha")))),
            sto(name="add", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.ADD, ref(name="C", indices=("m", "n")),
                              ref(name="AB", indices=("m", "n"))))),
            # alphascale's requirement, but C comes from memory rather than
            # from betascale: another STO, with other candidates
            sto(name="alphaadd", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="C", indices=("m", "n")),
                         node(op.ADD, ref(name="C", indices=("m", "n")),
                              node(op.MUL, ref(name="AB", indices=("m", "n")),
                                   scalar("alpha"))))),
            # accumulating into AB keeps it one fma: C = beta*C + AB would need
            # the result in a register other than the accumulator
            sto(name="betaadd", kind=sto_kind.COMPUTE, generator="scale",
                req=node(op.MOVE, ref(name="AB", indices=("m", "n")),
                         node(op.ADD, ref(name="AB", indices=("m", "n")),
                              node(op.MUL, ref(name="C", indices=("m", "n")),
                                   scalar("beta"))))),
            sto(name="store_ab", kind=sto_kind.STORE, store_components=("AB",),
                store_into=(("AB", "C"),)),
        ]

    @classmethod
    def get_blocks(cls):
        return [
            block(stos=("mm",), loop_index="k", preload=True, tail=True),
            branch(cases=(
                case(when={"beta": 0, "alpha": 1}, blocks=(block(stos=("store_ab",)),)),
                case(when={"beta": 0}, blocks=(block(stos=("alphamul", "store")),)),
                case(when={"beta": 1, "alpha": 1}, blocks=(block(stos=("add", "store")),)),
                case(when={"beta": 1}, blocks=(block(stos=("alphaadd", "store")),)),
                case(when={"alpha": 1}, blocks=(block(stos=("betaadd", "store_ab")),)),
                case(blocks=(block(stos=("betascale", "alphascale", "store")),)),
            )),
        ]
