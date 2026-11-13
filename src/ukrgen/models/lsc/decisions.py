"""
The decisions the allocator makes: the operations generated for every path,
the one it took kept (docs/REGISTER_ALLOCATION.md: decisions)

An operation's `decision` names what its presence depends on - an offset
register it would need, a tail set by the vector length, a loop's columns. The
specializer generates both branches and tags the one that costs a register; the
allocation, which knows the machine, takes or leaves each; `decide` then drops
what was left, so that codegen sees one path and no pass after this re-chooses.
"""

from .ir import SECTIONS, ir_block, ir_program
from .operations import lsc_loop, lsc_operation


def blocks(program : ir_program) -> list:
    """
    Every block of a program: its own, then each case's
    :param program: the IR
    :return: the blocks, in the order they are emitted
    """
    return list(program.blocks) + [b for case in program.cases for b in case.blocks]


def decide(program : ir_program, taken : set[str] | frozenset[str]) -> int:
    """
    Keep the operations whose decision was taken, and the ones without a
    decision; drop the rest
    :param program: the IR, its operations possibly generated for every path
    :param taken: the decisions the allocator took
    :return: how many operations were dropped
    """
    kept = frozenset(taken)
    program.decisions = kept
    dropped = 0
    for block in blocks(program):
        for section in SECTIONS:
            ops, count = pruned(block.sections[section], kept)
            block.sections[section] = ops
            dropped += count
    return dropped


def pruned(ops : list, taken : frozenset[str]) -> tuple[list, int]:
    """
    A run of operations with the untaken decisions dropped, their loops'
    operations pruned the same way
    :param ops: the operations
    :param taken: the decisions the allocator took
    :return: the operations kept, how many were dropped
    """
    out, dropped = [], 0
    for op in ops:
        if op.decision is not None and op.decision not in taken:
            dropped += 1
            continue
        if isinstance(op, lsc_loop):
            dropped += inside(op, taken)
        out.append(op)
    return out, dropped


def inside(loop : lsc_loop, taken : frozenset[str]) -> int:
    """
    A loop's operations pruned: its sections, then what it reads and writes
    from them again
    :param loop: the loop
    :param taken: the decisions the allocator took
    :return: how many operations were dropped
    """
    dropped = 0
    for section in loop.SECTIONS:
        ops, count = pruned(list(loop.sections.get(section) or []), taken)
        loop.sections[section] = ops
        dropped += count
    loop.refresh()
    return dropped
