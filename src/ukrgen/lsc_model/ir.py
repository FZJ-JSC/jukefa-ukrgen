"""
Containers for the LSC IR the model builds.

The operations are the LSC classes the schedulers and the specializer work
on (lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation), carrying in
addition the signatures their instructions come from and their addresses as
records in the offset database. This module holds the blocks and programs
around them, and renders them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from asmgen.asmblocks.op import register_type as rgt

from .addressing import offset_db, sym


@dataclass(frozen=True)
class vreg:
    """
    A virtual register: the index-th register of a component (A, AB), of a
    temporary of a chain (T0), or of scratch space between the steps of a data
    movement, in one register file
    """
    owner : str
    rtype : rgt
    index : int

    def __str__(self):
        return f"{self.owner}{self.index}.{self.rtype.name}"


@dataclass(frozen=True)
class addr_ref:
    """
    Where an access goes: address register reg of component, plus the offset
    registered as offset
    """
    component : str
    reg : int
    offset : int


def render_op(op, db: offset_db) -> str:
    """
    One LSC operation as built by the model, with addresses from the offset
    database and register files from the operation's rtypes
    """
    from ..models.load_store_operations import (
        lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute)

    def reg(pos: int) -> str:
        idx = op.indices[pos]
        rtypes = op.rtypes or []
        rtype = rtypes[pos] if pos < len(rtypes) and rtypes[pos] is not None else None
        text = f"{idx.component}{idx.indices[0]}" + (f".{rtype.name}" if rtype else "")
        return text + (f".el[{idx.indices[1]}]" if len(idx.indices) > 1 else "")

    if isinstance(op, (lsc_load, lsc_store)):
        where = f"{db[op.offset]}@a{op.indices[0].indices[0]}"
        if isinstance(op, lsc_load):
            return f"{reg(1)} <- {op.rsln}:load {where}"
        return f"{where} <- {op.rsln}:store {reg(1)}"
    if isinstance(op, lsc_move):
        return f"{reg(1)} <- {op.rsln}:move {reg(0)}"
    if isinstance(op, lsc_zero):
        return f"{reg(0)} <- 0"
    if isinstance(op, lsc_addr_compute):
        comp = op.indices[0].component
        return (f"{comp}@a{op.indices[1].indices[0]} <- {comp}@a{op.indices[0].indices[0]} "
                f"+ {op.delta}")
    if isinstance(op, lsc_transformation):
        dests = ",".join(reg(i) for i in op.writes)
        srcs = ",".join(reg(i) for i in op.reads)
        return f"{dests} <- {op.op}({srcs})"
    return str(op)


@dataclass
class ir_block:
    """
    A block of the composition as operations.

    A straight-line block has only a body. A loop block runs prologue once,
    body once per loop iteration, then epilogue; tail handles the iterations
    left over when the loop count is not a multiple of the iteration's size.
    With preloading, the prologue loads the first iteration's streamed data,
    the body loads the next iteration's into each register right after its
    last use, and the epilogue is the last iteration, which loads nothing.

    :param step: elements of the loop index one iteration covers: the unroll
                 times what one operation covers along it - 1 for an FMA,
                 VL for an operation vectorizing the loop index
    :param unroll: operations along the loop index per iteration: the size
                   given for it, e.g. --k for gemm's loop over k
    :param tail_step: elements one tail iteration covers: one operation of the
                      main implementation. Only with an unroll above 1.
    :param subtail_step: elements one subtail iteration covers: one, with the
                         subtail implementation, for a main one covering more
    :param requires_multiple: without a subtail where one would be needed: the
                              loop count must be a multiple of this, which the
                              kernel's wrapper has to ensure
    :param advance: component -> offset each address register advances per
                    iteration
    """
    name : str
    loop_index : str | None = None
    step : sym = field(default_factory=lambda: sym.const(1))
    unroll : int = 1
    tail_step : sym | None = None
    subtail : list = field(default_factory=list)
    subtail_step : sym | None = None
    requires_multiple : sym | None = None
    prologue : list = field(default_factory=list)
    body : list = field(default_factory=list)
    epilogue : list = field(default_factory=list)
    tail : list = field(default_factory=list)
    advance : dict[str, int] = field(default_factory=dict)
    #: its components' address registers advanced in the IR (not the emitter's)
    advance_in_ir : bool = False
    #: how far ahead its loads run of the body's iteration
    preload_shift : object = None


@dataclass
class ir_case:
    """
    One case of the branch ending the kernel: its blocks run when every
    condition holds, the first such case in order winning

    :param when: scalar component -> value it must equal; empty for the default
    """
    label : str
    when : dict
    blocks : list[ir_block]


@dataclass
class ir_program:
    """
    The kernel as IR blocks, with what codegen needs to resolve addresses

    :param offsets: every offset an access or setup refers to
    :param strides: memory component -> index -> stride in elements
    :param addr_setup: (component, address register) -> offset it starts at
    :param registers: owner -> (register type, registers used)
    """
    blocks : list[ir_block]
    offsets : offset_db
    strides : dict[str, dict[str, sym]]
    addr_setup : dict[tuple[str, int], int]
    registers : dict[str, tuple[rgt, int]]
    cases : list[ir_case] = field(default_factory=list)
    #: the index each component's vector registers run along
    vector_indices : dict[str, str] = field(default_factory=dict)
    #: components whose registers are groups: how many registers, the method
    groups : dict[str, tuple[int, str]] = field(default_factory=dict)
    #: indices whose last vector is masked (irmod tailmask): its elements a
    #: run-time parameter, tail(<index>), the mask set from it once
    tails : set[str] = field(default_factory=set)
    #: those of them whose last vector's accesses run at a shorter vector
    #: length (tailmask route vl: RVV's vsetvli around each) - not masked
    tail_vl : set[str] = field(default_factory=set)
    #: run once before every path, and once after them: the ISA's engine
    #: switched on and off as state (SME's smstart, smstop - streaming mode
    #: and ZA), the setup's and teardown's own switches left out
    entry : list = field(default_factory=list)
    exit : list = field(default_factory=list)
    #: the engine on around the kernel by the caller (--assume-state): no
    #: switch, the setup's own left out too, its clobbers not the kernel's
    engine_assumed : bool = False
    #: general registers the emitter may give offset polynomials an address
    #: move needs (a strided walk's row change: rs - (n - R) cs), computed once
    #: - the moves used most, saving the most instructions, first
    offset_registers : int = 0

    def render(self) -> str:
        db = self.offsets
        lines = []
        regs = ", ".join(f"{o}: {n} {t.name}" for o, (t, n) in self.registers.items())
        lines.append(f"registers: {regs}")
        for comp, strides in self.strides.items():
            lines.append(f"strides {comp}: " + ", ".join(f"{i}={s}" for i, s in strides.items()))
        for (comp, reg), oid in sorted(self.addr_setup.items()):
            lines.append(f"a{reg} of {comp} starts at {db[oid]}")
        def render_block(block, indent=""):
            lines.append("")
            head = f"{indent}block {block.name}"
            if block.loop_index:
                head += (f", loop over {block.loop_index} by {block.step} per iteration "
                         f"(unrolled {block.unroll}x)")
                if block.tail:
                    head += f", tail by {block.tail_step}"
                if block.subtail:
                    head += f", subtail by {block.subtail_step}"
                if block.requires_multiple is not None:
                    head += (f"; {block.loop_index} must be a multiple of "
                             f"{block.requires_multiple}")
            lines.append(head)
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                ops = getattr(block, section)
                if ops:
                    lines.append(f"{indent}  {section}:")
                    lines.extend(f"{indent}    {render_op(op, db)}" for op in ops)
            for comp, oid in block.advance.items():
                lines.append(f"{indent}  advance {comp} by {db[oid]} per iteration")

        for block in self.blocks:
            render_block(block)
        for case in self.cases:
            lines += ["", f"case {case.label}:"]
            for block in case.blocks:
                render_block(block, "  ")
        return "\n".join(lines)
