"""
Hooks that print what the flow has built - a start for writing hooks:

    --hooks "after schedule examples/hooks/dump.py blocks"
    --hooks "after schedule examples/hooks/dump.py ctxfields"

blocks: per program (and its cases) each block's parts - prologue, body,
epilogue, tail - and their operations by kind, with one load's and one
FMA's fields. ctxfields: the context's filled fields. irs: the older flow's
IR blocks (ctx.irs).
"""


def irs(ctx, stage, depth="3"):
    """Each IR block: its operation kinds, nested blocks (loops) indented"""
    def walk(ops, d, out):
        counts = {}
        for op in ops:
            counts[type(op).__name__] = counts.get(type(op).__name__, 0) + 1
        out.append("  " * d + ", ".join(f"{v} {k}" for k, v in counts.items()))
        for op in ops:
            if hasattr(op, "block") and d < int(depth):
                walk(op.block, d + 1, out)
    for name, ops in ctx.irs.items():
        out = []
        walk(ops, 1, out)
        print(f"[{type(stage).__name__}] {name}:\n" + "\n".join(out))

def ctxfields(ctx, stage):
    """What the context holds: each filled field, its type and size"""
    for k, v in vars(ctx).items():
        if v in (None, [], {}, (), "") or k == "params":
            continue
        size = len(v) if hasattr(v, "__len__") else ""
        first = ""
        if isinstance(v, list) and v:
            first = f" first: {type(v[0]).__name__}"
            if hasattr(v[0], "__dict__"):
                first += " " + str(sorted(vars(v[0]).keys()))[:150]
        print(f"[{type(stage).__name__}] {k}: {type(v).__name__} {size}{first}")

def blocks(ctx, stage):
    """Each program's blocks: op kinds per part; a load's and an FMA's fields"""
    shown = set()
    for prog in ctx.programs:
        for case in [prog] + list(getattr(prog, "cases", None) or []):
            for b in case.blocks:
                parts = []
                for part in ("prologue", "body", "epilogue", "tail"):
                    ops = getattr(b, part)
                    if ops:
                        counts = {}
                        for op in ops:
                            counts[type(op).__name__] = counts.get(type(op).__name__, 0) + 1
                        parts.append(f"{part}: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
                        for op in ops:
                            k = type(op).__name__
                            if k in ("lsc_load", "lsc_transformation") and k not in shown:
                                shown.add(k)
                                print(f"  a {k}: " + ", ".join(f"{a}={str(v)[:40]}" for a, v in vars(op).items()
                                                            if a not in ("sigs", "step", "tiles")))
                print(f"[{getattr(case, 'label', 'program')}] block {b.name} (loop {b.loop_index}, unroll {b.unroll})")
                for p in parts:
                    print("    " + p)
