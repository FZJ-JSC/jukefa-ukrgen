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

from asmgen.asmblocks.op.optransform import optransform_modifier
from asmgen.asmblocks.op.operand import operand_modifier
from asmgen.asmblocks.op.opmove import opmove_modifier
from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.asmblocks.op.opmem import opmem_modifier
from asmgen.asmblocks.op.scalar import BITS_GP
from asmgen.asmblocks.noarch import asmgen
from asmgen.registers import asm_data_type as adt, data_reg, freg_base, greg_base

#: general purpose registers' arithmetic: 64 bits
GP = adt.UINT64


def mov(gen: asmgen, *, src: greg_base, dst: greg_base) -> str:
    """dst = src"""
    return gen.move(dregs=[src, dst], dts=[GP, GP])


def set_imm(gen: asmgen, *, reg: greg_base, imm: int) -> str:
    """reg = imm"""
    return gen.set(dreg=reg, dt=GP, modifiers={opset_modifier.CONST}, value=imm)


def add_imm(gen: asmgen, *, reg: greg_base, imm: int) -> str:
    """reg += imm"""
    return gen.add(adreg=reg, bimm=imm, cdreg=reg, a_dt=GP, c_dt=GP)


def arith(gen: asmgen, op: str, *, dst: greg_base, reg1: greg_base, reg2: greg_base) -> str:
    """dst = reg1 op reg2 - op add or sub"""
    return getattr(gen, op)(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP)


def add(gen: asmgen, *, dst: greg_base, reg1: greg_base, reg2: greg_base) -> str:
    """dst = reg1 + reg2"""
    return arith(gen, "add", dst=dst, reg1=reg1, reg2=reg2)


def shifted(gen: asmgen, op: str, *, dst: greg_base, reg1: greg_base, reg2: greg_base,
            shift: int) -> str:
    """dst = reg1 op (reg2 << shift) - op add or sub"""
    return getattr(gen, op)(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP,
                            operand_modifiers={"bdreg": {operand_modifier.ISHIFT}},
                            bdreg_shift=shift)


def shift_left(gen: asmgen, *, reg: greg_base, bit_count: int) -> str:
    """reg <<= bit_count"""
    return gen.shift(adreg=reg, bimm=bit_count, cdreg=reg, a_dt=GP, c_dt=GP,
                     modifiers={optransform_modifier.SHL})


def mul(gen: asmgen, *, dst: greg_base, reg1: greg_base, reg2: greg_base) -> str:
    """dst = reg1 * reg2"""
    return gen.mul(adreg=reg1, bdreg=reg2, cdreg=dst, a_dt=GP, b_dt=GP, c_dt=GP)


def mul_imm(gen: asmgen, *, src: greg_base, dst: greg_base, factor: int) -> str:
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


def zero(gen: asmgen, *, reg: data_reg, dt: adt) -> str:
    """reg = 0: a vector, tile or FP register"""
    return gen.set(dreg=reg, dt=dt, modifiers={opset_modifier.CONST}, constant="zero")


def bits_to_freg(gen: asmgen, *, src: greg_base, dst: freg_base, dt: adt) -> str:
    """dst, an FP register of dt, = the bits of the general purpose register src"""
    return gen.move(dregs=[src, dst], dts=[BITS_GP[dt], dt], modifiers={opmove_modifier.BITS})


def load(gen: asmgen, *, areg: greg_base, offset: int, dst: greg_base | freg_base,
         dt: adt = GP) -> str:
    """dst = the dt at areg + offset - an offset only where it isn't 0"""
    kwargs = {"modifiers": {opmem_modifier.IOFFSET}, "ioffset": offset} if offset else {}
    return gen.load(dregs=[dst], areg=areg, dt=dt, **kwargs)


def adds_vectors(gen: asmgen) -> bool:
    """
    Whether the ISA adds counts of vector lengths to an address register as
    immediates (SVE's and SME's incb, decb, addvl): a sum of two such moves
    then costs no more than they did - RVV's take a register
    """
    if not gen.is_vla:
        return False
    reg = gen.greg(0)
    return bool(gen.add.fits(adreg=reg, bimm=1, cdreg=reg, a_dt=GP, c_dt=GP,
                             modifiers={optransform_modifier.VOFFSET}))


def add_vectors(gen: asmgen, *, reg: greg_base, offset: int) -> str:
    """
    reg += offset vectors' bytes: counted in vector lengths where they're the
    machine's - one add where it holds the count (SVE's incb, addvl), steps of
    the most it holds where not - in bytes where they're known
    """
    if not gen.is_vla:
        return add_imm(gen, reg=reg, imm=offset * gen.simd_size)
    def call(n):
        return dict(adreg=reg, bimm=n, cdreg=reg, a_dt=GP, c_dt=GP, modifiers={optransform_modifier.VOFFSET})
    out, left = "", offset
    while left and not gen.add.fits(**call(left)):
        step = next(n for n in range(abs(left) - 1, 0, -1) if gen.add.fits(**call(n if left > 0 else -n)))
        step = step if left > 0 else -step
        out += gen.add(**call(step))
        left -= step
    if left:
        out += gen.add(**call(left))
    return out
