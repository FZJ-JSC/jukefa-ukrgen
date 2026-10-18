"""
The values a signature's operand may take
"""

from asmgen.asmblocks.op.domain import constraint_domain


def operand_values(sig, name: str, universe=None, context=None):
    """
    The values a signature's operand may take, from its constraints
    (asmgen's constraint_domain); None where the signature has no such
    operand. universe bounds what nothing else does - a register file
    """
    shape = sig.operands.get(name)
    if shape is None:
        return None
    return constraint_domain(shape.value_constraints, name=name, modifiers=set(sig.modifiers),
                             context=context, universe=universe)
