# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------
"""
A virtual data register's data type - the memory component it is loaded from
or stored to, or the component it holds

Both ends of the allocation need it: the analysis to know which pool a value
comes from (a tile's file is its data type's) and the emitter to form the
instruction (the register's width and element type). Computed once, from the
program, so the two can't disagree.
"""

from asmgen.registers import asm_data_type as adt

from .operations import lsc_load, lsc_store
from .index import lsc_reg_index
from .ir import ir_program

#: the sections whose operations carry data registers (the emitter's own list:
#: init's zeroing and a subtail's are not where a value's type is first seen)
SECTIONS = ("prologue", "body", "epilogue", "tail", "subtail")


def ops_of(program : ir_program) -> list:
    """
    Every operation of a program: its blocks' sections, its cases'
    :param program: the IR
    :return: the operations, a loop's own through the loop's indices (its
             refresh) - the ones whose data registers carry a type
    """
    out : list = []
    for block in list(program.blocks) + [b for case in program.cases for b in case.blocks]:
        for section in SECTIONS:
            out.extend(getattr(block, section, None) or [])
    return out


def register_types(program : ir_program,
                   component_dts : dict[str, adt]) -> dict[tuple[str, int], adt]:
    """
    Data type of every virtual data register
    :param program: the IR
    :param component_dts: component -> its data type (the ctx's)
    :return: an index's value() (its component and number) -> its data type: the
             loaded or stored memory component's, else the component the value
             holds, else the kernel's default - the first, for a value none of
             those name
    """
    comps = component_dts
    dts: dict[tuple[str, int], adt] = {}
    ops = ops_of(program)

    def note(idx : lsc_reg_index, dt : adt) -> None:
        """
        A value's data type, unless a better one was noted
        :param idx: the index a value sits in
        :param dt: the data type to note
        """
        # by the value's own register (value(): a renamed value's owner) - its
        # data type the value's, whose register it is in or not
        dts.setdefault(idx.value(), dt)

    for op in ops:
        if isinstance(op, (lsc_load, lsc_store)):
            note(op.indices[1], comps[op.indices[0].component])
    for op in ops:
        for idx in op.indices:
            if idx.value()[0] in comps:
                note(idx, comps[idx.value()[0]])
    if not comps:
        return dts
    default = next(iter(comps.values()))
    for op in ops:
        for idx in op.indices:
            note(idx, default)
    return dts
