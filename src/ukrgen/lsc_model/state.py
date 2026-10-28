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


def merge_switches(program) -> int:
    """
    Adjacent short-length regions as one, after scheduling: an lsc_state
    setting a value back (vlen max) followed by one setting the same value the
    region before had (tail(m)), nothing between reading or writing that
    state - both dropped. A pipelined loop's last-vector store and the next
    column's load so share their region. How many pairs it dropped
    """
    dropped = 0
    for block, section in blocks_and_sections(program):
        ops = list(getattr(block, section) or [])
        out, k = [], 0
        while k < len(ops):
            op = ops[k]
            if isinstance(op, lsc_state) and len(out) and _drop_pair(out, ops, k):
                k = _next_switch(ops, k) + 1
                dropped += 1
                continue
            out.append(op)
            k += 1
        setattr(block, section, out)
    return dropped


def _previous_values(out: list) -> dict | None:
    """the values the last lsc_state already placed set"""
    for op in reversed(out):
        if isinstance(op, lsc_state):
            return op.values
    return None


def _next_switch(ops: list, k: int) -> int:
    """the next operation after k reading or writing state k's lsc_state sets"""
    names = set(ops[k].values)
    for j in range(k + 1, len(ops)):
        if names & (ops[j].reads_state | ops[j].writes_state):
            return j
    return len(ops)


def _drop_pair(out: list, ops: list, k: int) -> bool:
    """whether ops[k] sets back what the next switch sets again, unread between"""
    before = _previous_values(out)
    j = _next_switch(ops, k)
    if before is None or j >= len(ops) or not isinstance(ops[j], lsc_state):
        return False
    return ops[j].values == before and set(ops[k].values) == set(before)
