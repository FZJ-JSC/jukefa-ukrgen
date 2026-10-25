# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# ------------------------------------------------------------------------------
"""
What the signature emitter writes through asmgen's operations - add, sub,
mul, shift, move, set, load - one call each: the general purpose arithmetic,
moves, constants and loads it needs, as asmgen's old wrappers (mov_greg,
add_greg_imm, zero_vreg, ...) wrote them, which asmgen 0.6 retires.
"""
from __future__ import annotations

from asmgen.asmblocks.op.opd3 import opd3_modifier
from asmgen.asmblocks.op.operand import operand_modifier
from asmgen.asmblocks.op.move import move_modifier
from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.asmblocks.op.opmem import opmem_modifier
from asmgen.asmblocks.op.scalar import BITS_GP
from asmgen.registers import asm_data_type as adt

#: general purpose registers' arithmetic: 64 bits
GP = adt.UINT64


def mov(gen, *, src, dst) -> str:
    """dst = src"""
    return gen.move(dregs=[src, dst], dts=[GP, GP])


def set_imm(gen, *, reg, imm: int) -> str:
    """reg = imm"""
    return gen.set(dreg=reg, dt=GP, modifiers={opset_modifier.CONST}, value=imm)


def add_imm(gen, *, reg, imm: int) -> str:
    """reg += imm"""
    return gen.add(adreg=reg, bimm=imm, cdreg=reg, a_dt=GP, c_dt=GP)


def arith(gen, op: str, *, dst, reg1, reg2) -> str:
    """dst = reg1 op reg2 - op add or sub"""
    return getattr(gen, op)(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP)


def add(gen, *, dst, reg1, reg2) -> str:
    """dst = reg1 + reg2"""
    return arith(gen, "add", dst=dst, reg1=reg1, reg2=reg2)


def shifted(gen, op: str, *, dst, reg1, reg2, shift: int) -> str:
    """dst = reg1 op (reg2 << shift) - op add or sub"""
    return getattr(gen, op)(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP,
                            operand_modifiers={"bdreg": {operand_modifier.ISHIFT}},
                            bdreg_shift=shift)


def shift_left(gen, *, reg, bit_count: int) -> str:
    """reg <<= bit_count"""
    return gen.shift(adreg=reg, bimm=bit_count, cdreg=reg, a_dt=GP, c_dt=GP,
                     modifiers={opd3_modifier.SHL})


def mul(gen, *, dst, reg1, reg2) -> str:
    """dst = reg1 * reg2"""
    return gen.mul(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP)


def mul_imm(gen, *, src, dst, factor: int) -> str:
    """
    dst = src * factor: by the immediate where the ISA multiplies by one
    (x86's imul), else the factor set into dst first - dst then can't be src
    """
    imm = dict(adreg=src, bimm=factor, cdreg=dst, a_dt=GP, c_dt=GP)
    if gen.mul.fits(**imm):
        return gen.mul(**imm)
    if src == dst:
        raise ValueError(f"{dst} holds the factor {factor}: it can't be the multiplicand")
    return set_imm(gen, reg=dst, imm=factor) + mul(gen, dst=dst, reg1=src, reg2=dst)


def zero(gen, *, reg, dt) -> str:
    """reg = 0: a vector, tile or FP register"""
    return gen.set(dreg=reg, dt=dt, modifiers={opset_modifier.CONST}, constant="zero")


def bits_to_freg(gen, *, src, dst, dt) -> str:
    """dst, an FP register of dt, = the bits of the general purpose register src"""
    return gen.move(dregs=[src, dst], dts=[BITS_GP[dt], dt], modifiers={move_modifier.BITS})


def load(gen, *, areg, offset: int, dst, dt=GP) -> str:
    """dst = the dt at areg + offset - an offset only where it isn't 0"""
    kwargs = {"modifiers": {opmem_modifier.IOFFSET}, "ioffset": offset} if offset else {}
    return gen.load(dregs=[dst], areg=areg, dt=dt, **kwargs)


def add_vectors(gen, *, reg, offset: int) -> str:
    """
    reg += offset vectors' bytes: counted in vector lengths where they're the
    machine's (SVE's addvl), in bytes where they're known
    """
    if gen.is_vla:
        return gen.add(adreg=reg, bimm=offset, cdreg=reg, a_dt=GP, c_dt=GP,
                       modifiers={opd3_modifier.VOFFSET})
    return add_imm(gen, reg=reg, imm=offset * gen.simd_size)
