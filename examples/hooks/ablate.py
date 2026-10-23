"""
Ablation hooks: a kernel with a kind of instruction taken out of its loops'
bodies, to measure what that kind costs. The kernel computes nonsense then:
for timing only, as ukropt-sweep measures.

drop - operations out of the IR:

    hooks: ["after schedule examples/hooks/ablate.py drop what=vload"]

  what: vload (loads into vector registers), sload (loads into scalar
  registers), fma (arithmetic); several comma-separated. components: only
  these (A,B). loops: the loop indices whose bodies change (k); parts: which
  of a block's parts (body - prologue, epilogue and tail run once a call).
  After schedule, the schedule stays as it was, the operations gone from it;
  before schedule, the scheduler arranges what is left.

drop_lines - lines out of the emitted assembly, after emit:

    hooks: ["after emit examples/hooks/ablate.py drop_lines pattern=^add"]

  pattern: a regular expression, the lines matching it go from the loops'
  bodies (^add: the walks and the loop's advance - pointers stay, every load
  reads what its immediate says from the same registers; the loop's counter
  and branch stay). labels: the loops, by their labels' endings (_loop: the
  main k loop; _loop,_tail: its tail too). Address arithmetic can only go
  this way: the IR's loads use the address registers its computations set.
"""
import re
from asmgen.asmblocks.op.operand import register_type


def _kind(op) -> str | None:
    name = type(op).__name__
    if "lsc_load" == name:
        types = [t for t in (getattr(op, "rtypes", None) or []) if t is not None]
        return "vload" if register_type.VEC in types else "sload"
    if name in ("lsc_addr_compute", "lsc_addr_add"):
        return "addr"
    if "lsc_transformation" == name:
        return "fma" if "fma" == getattr(op, "op", None) else "arith"
    return None


def _component(op) -> str:
    # the data register's owner: the last index written, else the first read
    idx = op.indices[op.writes[-1]] if op.writes else op.indices[0]
    return getattr(idx, "owner", str(idx).rstrip("0123456789"))


def drop(ctx, stage, what="vload", components="", loops="k", parts="body"):
    kinds = set(what.split(","))
    if "addr" in kinds:
        raise ValueError("ablate.drop: address arithmetic can't leave the IR - its loads use the "
                         "registers it sets; take its lines out after emit instead: "
                         "'after emit ... drop_lines pattern=^add'")
    comps = set(c for c in components.split(",") if c)
    loop_set = set(loops.split(","))
    removed = {}
    for prog in ctx.programs:
        for case in [prog, *(getattr(prog, "cases", None) or [])]:
            for block in case.blocks:
                if block.loop_index not in loop_set:
                    continue
                for part in parts.split(","):
                    ops = getattr(block, part)
                    keep = []
                    for op in ops:
                        k = _kind(op)
                        if k in kinds and (not comps or _component(op) in comps):
                            removed[k] = removed.get(k, 0) + 1
                        else:
                            keep.append(op)
                    ops[:] = keep
    if not removed:
        raise ValueError(f"ablate.drop: nothing matched what={what} components={components} "
                         f"loops={loops} parts={parts}")


def drop_lines(ctx, stage, pattern="^add", labels="_loop"):
    """
    After emit: in each loop whose label ends in one of labels (_loop: the
    main k loop - _tail its tail), the lines matching pattern go; the loop's
    counter (the line after its label) and its branch stay
    """
    rx = re.compile(pattern)
    suffixes = tuple(labels.split(","))
    removed = 0
    for prog in ctx.emitted:
        out, inside = [], None
        for line in prog.code:
            text = line.strip()
            if inside is None and text.endswith(":") and text[:-1].endswith(suffixes):
                inside, first = text[:-1], True
                out.append(line)
                continue
            if inside is not None:
                if text.endswith("," + inside) or text.endswith(" " + inside):
                    inside = None               # the branch back: the loop ends
                elif first:
                    first = False               # the counter
                elif rx.search(text):
                    removed += 1
                    continue
            out.append(line)
        prog.code[:] = out
    if not removed:
        raise ValueError(f"ablate.drop_lines: no line matched {pattern!r} in loops ending {labels}")
