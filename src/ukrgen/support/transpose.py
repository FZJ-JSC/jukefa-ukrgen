"""
In-register transposes: rounds of asmgen's permutes taking a block's rows,
one register each, to its columns - packm across the grain without gathers
or scatters (AMD's zen4 packm does 8x8 doubles in three rounds).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from asmgen.asmblocks.op.opmove import opmove_modifier, permuted
from asmgen.registers import adt_size

#: each pattern's partner: a round computes both from the same two registers
PAIRS = {"zip_lo": "zip_hi", "uzp_even": "uzp_odd", "trn_even": "trn_odd"}


@dataclass(frozen=True)
class round_spec:
    """
    One round: register i and register i ^ distance, for every i without
    that bit, become first(i, i ^ distance) in i and second(...) in i ^ distance
    - two permute forms of the same bits and segment
    """
    distance: int
    first: object       # the signature computing register i
    second: object      # the signature computing register i ^ distance

    def params(self, which: str) -> dict:
        return dict((self.first if "first" == which else self.second).structural_params)


@dataclass(frozen=True)
class network:
    """
    A transpose's rounds, and where each column ends: column j in register
    columns[j]
    """
    rounds: tuple[round_spec, ...]
    columns: tuple[int, ...]


def _form_pairs(gen, dt) -> list[tuple]:
    """the ISA's permutes for dt, partnered: (first, second) of one bits and segment"""
    forms = gen.move.forms(modifiers={opmove_modifier.PERMUTE}, dts={"adreg": dt})
    by = {(s.structural_params["pattern"], s.structural_params["bits"], s.structural_params["segment"]): s
          for s in forms}
    pairs = []
    for (pattern, bits, segment), s in sorted(by.items(), key=lambda kv: (kv[0][1], str(kv[0][2]), kv[0][0])):
        partner = by.get((PAIRS.get(pattern), bits, segment))
        if partner is not None:
            pairs.append((s, partner))
    return pairs


def _apply(state: tuple, rnd: round_spec, ebits: int) -> tuple:
    regs = list(state)
    for i in range(len(regs)):
        j = i ^ rnd.distance
        if i < j:
            a, b = state[i], state[j]
            f, s = rnd.first.structural_params, rnd.second.structural_params
            regs[i] = tuple(permuted(f["pattern"], list(a), list(b), element_bits=ebits,
                                     bits=f["bits"], segment=f["segment"]))
            regs[j] = tuple(permuted(s["pattern"], list(a), list(b), element_bits=ebits,
                                     bits=s["bits"], segment=s["segment"]))
    return tuple(regs)


def _columns(state: tuple, lanes: int) -> tuple | None:
    """where each column is, every register one column in row order; None if not"""
    where = {}
    for r, reg in enumerate(state):
        cols = {e % lanes for e in reg}
        rows = [e // lanes for e in reg]
        if 1 != len(cols) or rows != list(range(lanes)):
            return None
        where[cols.pop()] = r
    return tuple(where[c] for c in range(lanes)) if len(where) == lanes else None


#: networks found, by the generator's class, its permutes, the type and the lanes
_FOUND: dict = {}


def transpose_network(gen, dt, max_rounds: int | None = None) -> network | None:
    """
    The fewest rounds of the ISA's permutes transposing a block of rows of
    dt, as many as the register's elements (its lanes) - found by a breadth-first search
    over the rounds' forms and pairings, checked by permuted(); None where the
    ISA's permutes don't make one (or the vector's length isn't known)
    """
    if gen.is_vla:
        return None
    ebits = 8 * adt_size(dt)
    lanes = gen.simd_size // adt_size(dt)
    if lanes < 2 or lanes & (lanes - 1):
        return None
    depth = (lanes.bit_length() - 1) + 1 if max_rounds is None else max_rounds
    pairs = _form_pairs(gen, dt)
    key = (type(gen), dt, lanes, depth,
           tuple((tuple(sorted(f.structural_params.items(), key=str)), tuple(sorted(g.structural_params.items(), key=str)))
                 for f, g in pairs))
    if key not in _FOUND:
        _FOUND[key] = _search(pairs, lanes, depth, ebits)
    return _FOUND[key]


def _search(pairs, lanes: int, depth: int, ebits: int) -> network | None:
    start = tuple(tuple(r * lanes + c for c in range(lanes)) for r in range(lanes))
    seen = {start}
    queue = deque([(start, ())])
    while queue:
        state, rounds = queue.popleft()
        cols = _columns(state, lanes)
        if cols is not None:
            return network(rounds=rounds, columns=cols)
        if len(rounds) >= depth:
            continue
        for first, second in pairs:
            d = 1
            while d < lanes:
                rnd = round_spec(distance=d, first=first, second=second)
                nxt = _apply(state, rnd, ebits)
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, rounds + (rnd,)))
                d <<= 1
    return None
