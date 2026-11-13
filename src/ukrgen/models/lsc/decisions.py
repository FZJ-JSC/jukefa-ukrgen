"""
The decisions the allocator makes: the operations generated for every path,
the one it took kept (docs/REGISTER_ALLOCATION.md: decisions)

An operation's `decision` names what its presence depends on - an offset
register it would need, a tail set by the vector length, a loop's columns. The
specializer generates both branches and tags the one that costs a register; the
allocation, which knows the machine, takes or leaves each; `decide` then drops
what was left, so that codegen sees one path and no pass after this re-chooses.
It runs before the values the steps add are set up, so a path taken away leaves
none behind.
"""

from .ir import SECTIONS, ir_block, ir_program
from .operations import lsc_loop, lsc_operation


def blocks(program : ir_program) -> list[ir_block]:
    """
    Every block of a program: its own, then each case's
    :param program: the IR
    :return: the blocks, in the order they are emitted
    """
    return list(program.blocks) + [b for case in program.cases for b in case.blocks]


def sections(program : ir_program) -> list[list[lsc_operation]]:
    """
    Every run of operations of a program, as the lists themselves: each
    block's sections, each case's, and their loops' - so one can be filtered
    where it is
    :param program: the IR
    :return: the lists, in the order they are emitted
    """
    out : list[list[lsc_operation]] = []

    def visit(ops : list[lsc_operation]) -> None:
        for op in ops:
            if isinstance(op, lsc_loop):
                for name in lsc_loop.SECTIONS:
                    inner = op.sections.setdefault(name, [])
                    out.append(inner)
                    visit(inner)

    for block in blocks(program):
        for section in SECTIONS:
            run = block.sections[section]
            out.append(run)
            visit(run)
    return out


def decide(program : ir_program, taken : set[str] | frozenset[str]) -> int:
    """
    Keep the operations whose decision was taken, and the ones without a
    decision; drop the rest and the values nothing reads afterwards. The
    offsets' decisions become the plan the emitter reserves registers by
    :param program: the IR, its operations possibly generated for every path
    :param taken: the decisions the allocator took
    :return: how many operations were dropped
    """
    kept = frozenset(taken)
    program.decisions = kept
    dropped = 0
    for run in sections(program):
        out, count = pruned(run, kept)
        run[:] = out
        dropped += count
    if dropped:
        # what a loop reads and writes, from the operations it has left
        for loop in loops(program):
            loop.refresh()
    program.offset_plan = plan(program, kept)
    return dropped


def plan(program : ir_program, taken : set[str] | frozenset[str]) -> dict:
    """
    The offsets' plan the emitter reserves registers by: the candidates whose
    decision was taken, their rank from the ranking
    :param program: the IR, its candidates (the speller's) as it left them
    :param taken: the decisions taken
    :return: (the polynomial's text, component) -> rank
    """
    kept = frozenset(taken)
    return {key: rank for name, (rank, key) in (program.offset_candidates or {}).items()
            if name in kept}


def loops(program : ir_program) -> list[lsc_loop]:
    """
    Every loop of a program, the ones inside loops' sections too
    :param program: the IR
    :return: the loops
    """
    out : list[lsc_loop] = []

    def visit(ops : list[lsc_operation]) -> None:
        for op in ops:
            if isinstance(op, lsc_loop):
                out.append(op)
                for name in lsc_loop.SECTIONS:
                    visit(op.sections.get(name) or [])

    for block in blocks(program):
        for section in SECTIONS:
            visit(block.sections[section])
    return out


def pruned(ops : list[lsc_operation], taken : frozenset[str]) -> tuple[list[lsc_operation], int]:
    """
    A run of operations with the untaken decisions dropped
    :param ops: the operations
    :param taken: the decisions the allocator took
    :return: the operations kept, how many were dropped
    """
    out, dropped = [], 0
    for op in ops:
        if op.decision is not None and op.decision not in taken:
            dropped += 1
            continue
        out.append(op)
    return out, dropped
