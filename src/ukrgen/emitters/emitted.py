"""
The emitted program's parts: blocks and their sections, labels (split from
emitters/signature.py)
"""




from dataclasses import dataclass, field






class _labels:
    """The labels' numbers in order - copyable (a loop emitted on trial)"""

    def __init__(self):
        self.n = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.n += 1
        return self.n - 1


@dataclass
class emitted_block:
    """
    A block's sections as assembly. A loop block's body is one iteration;
    advance moves the address registers on to the next, tail_advance does the
    same for one tail iteration.
    """
    name : str
    loop_index : str | None
    sections : dict[str, list[str]] = field(default_factory=dict)
    advance : list[str] = field(default_factory=list)
    #: what the region needs set up at its start: address registers from the
    #: parameters, loop counts
    loads : list[str] = field(default_factory=list)
    #: a loop's counters: iterations, then the tail's
    counters : tuple | None = None
    tail_advance : list[str] = field(default_factory=list)
    #: what an iteration takes off its counter (an element loop's: its unroll)
    step : int = 1
    #: what the prologue takes off it first (a loop over slices': an
    #: iteration's slices, its copies)
    prologue_step : int = 1
    #: whether the count may be 0 - a branch past the loop first (a vector's
    #: elements never are)
    guarded : bool = True
    #: a plain loop: its body only, counted down by its step (an element
    #: loop's) - not software-pipelined, no last iteration of its own
    plain : bool = False
    #: its labels' kind (ukrN_loop; an element loop's ukrN_elements)
    label : str = "loop"


@dataclass
class emitted_program:
    """
    :param setup: address register initialization
    :param bases: memory component -> register holding its base address, to be
                  bound to the kernel's arguments
    :param registers: virtual register -> physical register
    """
    setup : list[str]
    blocks : list[emitted_block]
    cases : list[tuple[str, dict, list[emitted_block]]]
    bases : dict[str, str]
    registers : dict[tuple, str]
    teardown : list[str] = field(default_factory=list)
    data : list[str] = field(default_factory=list)
    #: the program with its control flow - loops, the dispatch on cases -
    #: between setup and teardown
    code : list[str] = field(default_factory=list)
    #: the function's parameters in order, each in the register named - k per
    #: loop, base(X) per component's start address, stride(X,i) in bytes - as
    #: the calling convention passes them (asmgen's callconv)
    params : dict[str, str] = field(default_factory=dict)
    #: the function's boilerplate: saving the callee-saved registers the code
    #: clobbers and loading parameters passed on the stack; restoring, return
    entry : list[str] = field(default_factory=list)
    exit : list[str] = field(default_factory=list)
    #: the generator the program is for: it frames the function (fngen)
    gen : object = None

    def instructions(self, data : bool = True) -> list[str]:
        """
        Every instruction, in program order, ignoring loop structure; then
        the data the program keeps, unless data is False
        """
        kept = list(self.data) if data else []
        out = list(self.setup)
        if self.code:
            return list(self.entry) + out + list(self.code) + list(self.teardown) \
                + list(self.exit) + kept
        for block in self.blocks + [b for _, _, bs in self.cases for b in bs]:
            for lines in block.sections.values():
                out += lines
            out += block.advance + block.tail_advance
        return out + list(self.teardown) + kept

    def function(self, name: str, *, align: int | None = None, offset: int = 0) -> list[str]:
        """
        The program as an assembly function, as asmgen frames one (fngen:
        section, alignment, .global, .type, the label, the instructions,
        .size, the data) - then what the file says once, the GNU-stack note

        :param align: the function's alignment in bytes, if any
        :param offset: where it starts past that boundary, in bytes
        """
        from asmgen.callconv.fngen import fngen  # pylint: disable=import-outside-toplevel
        if self.gen is None:
            raise ValueError("the program has no generator to frame it")
        body = "".join(f"{l}\n" for l in self.instructions(data=False))
        data = "".join(f"{l}\n" for l in self.data)
        text = fngen(self.gen).function(name, body, align=align, offset=offset, data=data)
        return (text + self.gen.asmfile_annotations()).splitlines()

    def render(self) -> str:
        lines = ["// bases: " + ", ".join(f"{c} in {r}" for c, r in self.bases.items())]
        lines += self.setup

        def block_lines(block: emitted_block, indent: str):
            lines.append(f"{indent}// block {block.name}"
                         + (f", loop over {block.loop_index}" if block.loop_index else ""))
            for section, ops in block.sections.items():
                if ops:
                    lines.append(f"{indent}// {section}")
                    lines.extend(indent + op for op in ops)
            if block.advance:
                lines.append(f"{indent}// next iteration")
                lines.extend(indent + op for op in block.advance)

        for block in self.blocks:
            block_lines(block, "")
        for label, _, blocks in self.cases:
            lines.append(f"// case {label}")
            for block in blocks:
                block_lines(block, "  ")
        return "\n".join(lines)
