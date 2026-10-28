"""
Processor state through a program: what each operation's signatures
require (asmgen's state_requires) checked against the state the ISA's setup
leaves and lsc_state operations set - each access keeping the signatures
whose requirements hold where it is
"""
from __future__ import annotations

from ..irmod.lsc.base import blocks_and_sections
from ..models.load_store_operations import lsc_load, lsc_state, lsc_store


def satisfied(requires: dict[str, str], state: dict[str, str]) -> bool:
    """whether state meets requirements: name -> "!=None" (set), "==v", "!=v" """
    for name, condition in requires.items():
        value = state.get(name)
        if "!=None" == condition:
            ok = value is not None
        elif condition.startswith("=="):
            ok = value == condition[2:]
        elif condition.startswith("!="):
            ok = value != condition[2:]
        else:
            raise ValueError(f"state requirement {name}: {condition!r} - !=None, ==value or !=value")
        if not ok:
            return False
    return True


def check_state(program, initial: dict[str, str]) -> list[str]:
    """
    The state through each section, from the setup's: an access's
    signatures pruned to those whose requirements hold (none left: a
    problem, said); a section ending in other state than it began - a loop's
    iterations would differ - a problem. The problems, empty where none
    """
    problems = []
    for block, section in blocks_and_sections(program):
        state = dict(initial)
        for op in getattr(block, section) or []:
            if isinstance(op, lsc_state):
                state.update(op.values)
                continue
            if not isinstance(op, (lsc_load, lsc_store)):
                continue
            sigs = op.state_sigs()
            held = [s for s in sigs if satisfied(s.state_requires, state)]
            if sigs and not held:
                needs = sorted({f"{k} {v}" for s in sigs for k, v in s.state_requires.items()})
                problems.append(f"{section}: {op.indices[1]}'s {type(op).__name__[4:]}: no form whose state "
                                f"requirements hold ({', '.join(needs)}; the state "
                                f"{', '.join(f'{k}={v}' for k, v in sorted(state.items())) or 'none'})")
            elif len(held) < len(sigs):
                op.sigs = held
        if state != dict(initial):
            problems.append(f"{section}: ends with other state than it began with "
                            f"({', '.join(f'{k}={v}' for k, v in sorted(state.items()))})")
    return problems
