"""
The LSC IR: loads, stores, moves and computations on virtual registers.

It describes what the kernel does to its registers, not the whole program.
Every operation carries the signature group its instruction comes from, so
codegen picks the concrete signature - which addressing form, which
modifiers - once addresses are known. Addresses are references into the
offset database, resolved at codegen.
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


@dataclass
class ir_op:
    pass


@dataclass
class ir_mem(ir_op):
    """
    A load or store step of a data movement resolution

    :param kind: "load" or "store"
    :param reg: register loaded into or stored from
    :param addr: where in memory
    :param resolution: tag of the resolution the step belongs to (direct, gather, ...)
    :param step: the data movement step
    :param sigs: signatures that can execute it
    :param lane: lane accessed, for a resolution moving a vector lane by lane
    """
    kind : str
    reg : vreg
    addr : addr_ref
    resolution : str
    step : object
    sigs : object
    lane : int | None = None

    def render(self, db: offset_db) -> str:
        lane = f".el[{self.lane}]" if self.lane is not None else ""
        where = f"{db[self.addr.offset]}@a{self.addr.reg}"
        if "load" == self.kind:
            return f"{self.reg}{lane} <- {self.resolution}:load {where}"
        return f"{where} <- {self.resolution}:store {self.reg}{lane}"


@dataclass
class ir_move(ir_op):
    """
    A register-to-register step of a data movement resolution (broadcasting a
    scalar into a vector, moving a lane)
    """
    src : vreg
    dest : vreg
    resolution : str
    step : object
    sigs : object
    lane : int | None = None

    def render(self, db: offset_db) -> str:
        lane = f".el[{self.lane}]" if self.lane is not None else ""
        return f"{self.dest} <- {self.resolution}:move {self.src}{lane}"


@dataclass
class ir_compute(ir_op):
    """
    One operation of a chosen implementation

    :param sto: STO it belongs to
    :param opname: asmgen operation
    :param resolution: the solved operation: compute signature group and how
                       each operand gets its data
    :param regs: hardware operand -> register
    :param lanes: hardware operand -> lane, for operands used by element
    :param reads: hardware operands read
    :param writes: hardware operands written
    """
    sto : str
    opname : str
    resolution : object
    regs : dict[str, vreg]
    lanes : dict[str, int]
    reads : tuple[str, ...]
    writes : tuple[str, ...]

    def render(self, db: offset_db) -> str:
        def show(hw):
            lane = self.lanes.get(hw)
            return f"{self.regs[hw]}" + (f".el[{lane}]" if lane is not None else "")
        dests = ",".join(show(hw) for hw in self.writes)
        srcs = ",".join(show(hw) for hw in self.reads)
        return f"{dests} <- {self.opname}({srcs})"


@dataclass
class ir_zero(ir_op):
    """
    Zero a register: an accumulator starting from nothing
    """
    reg : vreg

    def render(self, db: offset_db) -> str:
        return f"{self.reg} <- 0"


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
    subtail : list[ir_op] = field(default_factory=list)
    subtail_step : sym | None = None
    requires_multiple : sym | None = None
    prologue : list[ir_op] = field(default_factory=list)
    body : list[ir_op] = field(default_factory=list)
    epilogue : list[ir_op] = field(default_factory=list)
    tail : list[ir_op] = field(default_factory=list)
    advance : dict[str, int] = field(default_factory=dict)


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

    def render(self) -> str:
        db = self.offsets
        lines = []
        regs = ", ".join(f"{o}: {n} {t.name}" for o, (t, n) in self.registers.items())
        lines.append(f"registers: {regs}")
        for comp, strides in self.strides.items():
            lines.append(f"strides {comp}: " + ", ".join(f"{i}={s}" for i, s in strides.items()))
        for (comp, reg), oid in sorted(self.addr_setup.items()):
            lines.append(f"a{reg} of {comp} starts at {db[oid]}")
        for block in self.blocks:
            lines.append("")
            head = f"block {block.name}"
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
                    lines.append(f"  {section}:")
                    lines.extend(f"    {op.render(db)}" for op in ops)
            for comp, oid in block.advance.items():
                lines.append(f"  advance {comp} by {db[oid]} per iteration")
        return "\n".join(lines)
