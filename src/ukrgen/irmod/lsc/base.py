"""
The base of IR modifications on LSC IR programs, and their metadata
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, ClassVar


class irmod_placement(Enum):
    """
    Where in the flow an IR modification runs
    """
    #: on the model's IR, before addressing is fitted to the ISA
    PRE_SPECIALIZE = auto()
    #: on the IR specialized for the ISA, before scheduling
    POST_SPECIALIZE = auto()
    #: on the scheduled IR, before emission (no stage runs these yet)
    POST_SCHEDULE = auto()


@dataclass(frozen=True)
class irmod_param:
    """
    A tunable parameter of an IR modification: --<irmod>-<name> on the
    command line

    :param parse: turns the command line's string into the value
    """
    name : str
    description : str
    default : object = None
    choices : tuple | None = None
    parse : Callable = str


class lsc_irmod:
    """
    An IR modification of LSC IR programs. Implementations set the metadata
    below and implement apply().

    Required modifications run whenever triggered() says the kernel needs
    them - widening, for mixed data types, would be one; optional ones are
    offered to the user, enabled or not by default.
    """

    #: name on the command line
    name : ClassVar[str]
    #: one line for the help
    description : ClassVar[str]
    #: where in the flow it runs
    placement : ClassVar[irmod_placement]
    #: run whenever triggered, rather than offered as a choice
    required : ClassVar[bool] = False
    #: for optional modifications: on unless the user chooses otherwise
    default_enabled : ClassVar[bool] = True
    #: what every site it changes must satisfy - what check() checks
    constraints : ClassVar[str] = ""
    #: registers it needs beyond the program's own, per register file
    allocations : ClassVar[dict[str, int]] = {}
    #: tunable parameters
    params : ClassVar[tuple[irmod_param, ...]] = ()

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        """
        What the ISA or the kernel lacks for this modification - signatures,
        fixed-width vectors and the like. An optional modification with unmet
        requirements is not offered; a required one fails.

        :return: one line per requirement not met; empty if it can run
        """
        return []

    @classmethod
    def triggered(cls, ctx) -> bool:
        """
        For a required modification: whether this kernel needs it
        """
        return False

    def __init__(self, ctx, **values):
        self.ctx = ctx
        self.values = {p.name: values.get(p.name, p.default) for p in self.params}

    def apply(self, program) -> int:
        """
        Modify a program in place

        :return: how many sites were changed
        """
        raise NotImplementedError


def first_blocks(program) -> list:
    """
    The blocks the program's paths begin with: its first block, or - the
    branch the whole kernel (packm's kappa cases) - each case's first
    """
    if program.blocks:
        return [program.blocks[0]]
    return [case.blocks[0] for case in program.cases if case.blocks]


def all_blocks(program) -> list:
    """
    Every block of the program: its own, then its cases'
    """
    return program.blocks + [b for case in program.cases for b in case.blocks]


def blocks_and_sections(program):
    """
    Every section of every block of a program, as (block, section name)
    """
    for block in all_blocks(program):
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            yield block, section
