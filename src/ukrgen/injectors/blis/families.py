"""
Kernel families for blisgen. A family configures how kernels are built - the
ukrgen parameters every size shares: implementation choices (--mm-tileop,
--store-tileop, ...), register and preload limits, irmods, scheduling - and the
sizes to try; blisgen runs the flow once per size and keeps every kernel the
ISA can build, with what BLIS needs to know of it, and why each other size
was skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ...flow.stage_engine import stage_engine
from ...flow.ukr_context import ukr_context
from ...flow.stages.setup import setup_stage
from ...flow.stages.datatype import datatype_stage
from ...flow.stages.layout import layout_stage
from ...flow.stages.solve import solve_stage
from ...flow.stages.dimension import dimension_stage
from ...flow.stages.sto import sto_stage
from ...flow.stages.model import model_stage
from ...flow.stages.irmods import pre_specialize_irmod_stage, post_specialize_irmod_stage
from ...flow.stages.isa_specialize import isa_specialize_stage
from ...flow.stages.scheduling import schedule_stage
from ...flow.stages.emit import emit_stage
from ...lsc_model.addressing import sym

#: the flow as the command line runs it
PIPELINE = [setup_stage, datatype_stage, layout_stage, solve_stage, dimension_stage, sto_stage,
            model_stage, pre_specialize_irmod_stage, isa_specialize_stage,
            post_specialize_irmod_stage, schedule_stage, emit_stage]

#: BLIS's letter for a data type
DT_CHAR = {"FP32": "s", "FP64": "d"}


def run_flow(params: dict) -> tuple[ukr_context, object]:
    """
    One run of the flow with these parameters - a stage takes those it
    declares
    """
    taken = set()
    def prolog(s):
        for name in s.get_parameter_names():
            if name in params:
                s.set_param(name, params[name])
                taken.add(name)
    ctx = ukr_context()
    result = stage_engine(PIPELINE, ctx, prolog=prolog).run()
    if getattr(result, "completed", False):
        # a parameter no stage took - a key misnamed - does nothing: say so
        ignored = sorted(set(params) - taken)
        if ignored:
            import sys
            print(f"warning: no stage takes {', '.join(ignored)}", file=sys.stderr)
    return ctx, result


def run_unrolled(params: dict, key: str):
    """
    The flow with params[key] the unroll asked - a ceiling: where the kernel
    can't be built so (registers), half of it, down to 1. The flow's result
    and the unroll it took; the last failure where none builds
    """
    asked = int(params.get(key, 1) or 1)
    tries = []
    while asked >= 1:
        tries.append(asked)
        asked //= 2
    error = None
    for unroll in tries:
        try:
            ctx, result = run_flow(dict(params, **{key: str(unroll)}))
            return ctx, result, unroll
        except Exception as err:
            error = err
    raise error


def parse_sizes(value) -> list[int]:
    """
    Sizes to try: a number, a list, or a range "a..b" (both included)
    """
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        return [int(v) for v in value]
    text = str(value).strip()
    if ".." in text:
        lo, hi = text.split("..")
        return list(range(int(lo), int(hi) + 1))
    return [int(text)]


#: family keys and the ukrgen parameters they set
KEYS = {"loop-order": "order", "resolve-order": "resolve-order",
        "schedule": "distances", "cycle-slots": "sched-cycle-slots", "preset": "tileop-preset",
        "vectorize": "tileop-vectorize"}
#: per component: {component: value}
PER_COMPONENT = {"max-data-regs": "{c}-max-data-regs", "max-preload": "{c}-max-preload",
                 "max-addr-regs": "{c}-addr-regs", "addr-pattern": "{c}-addr-pattern"}
#: the loop a family's unroll is along
UNROLL = {"gemm": "k", "packm": "n"}


def key_params(kind: str, entry: dict) -> dict:
    """
    The ukrgen parameters a family's keys set: unroll (k for gemm, n for
    packm), loop-order, resolve-order, schedule (scheduler distance specs),
    and per component max-data-regs, max-preload, max-addr-regs and
    addr-pattern (block, interleave, phase)
    """
    params = {}
    if "unroll" in entry:
        params[UNROLL[kind]] = str(entry["unroll"])
    for key, name in KEYS.items():
        if key in entry:
            params[name] = entry[key]
    for key, name in PER_COMPONENT.items():
        for comp, value in (entry.get(key) or {}).items():
            params[name.format(c=comp)] = str(value)
    return params


def parse_ratios(value) -> list[tuple[int, int]]:
    """
    Ratios a:b - "1..2:1..3", or a list of "a:b" - those where a/b or b/a is
    a whole number, each once as a fraction in lowest terms: 1..2:1..3 is 1:1,
    1:2, 1:3, 2:1
    """
    from math import gcd
    items = value if isinstance(value, list) else [value]
    out = []
    for item in items:
        left, right = str(item).replace(" ", "").split(":")
        for a in parse_sizes(left):
            for b in parse_sizes(right):
                if a % b and b % a:
                    continue
                g = gcd(a, b)
                if (a // g, b // g) not in out:
                    out.append((a // g, b // g))
    return out


@dataclass
class family:
    """
    A family's configuration: its kind (gemm, packm), name, data types,
    shared ukrgen parameters, the sizes to try per index and the default
    size per data type
    """
    kind: str
    name: str
    dtypes: list[str]
    params: dict
    sizes: dict[str, list[int]]
    default: dict[str, tuple] = field(default_factory=dict)
    #: packm: the cases accelerated - (kind, sizes, params): vec (cdim m
    #: vectors, A contiguous along cdim), trans (cdim m elements, A
    #: contiguous along the panel's length)
    cases: list[tuple] = field(default_factory=list)
    #: a split microtile: the index split, and per part its parameters and
    #: sizes along that index
    split: str | None = None
    parts: list[tuple] = field(default_factory=list)
    #: a split's ratios of instructions, first part to second (a, b): the
    #: second part's size along the split index the first's x b / a
    ratios: list[tuple] = field(default_factory=list)
    #: packm: vectors a case keeps in flight at least - its unroll along the
    #: panel, a case of m vectors (rows, trans) unrolled ceil(min_inflight / m)
    min_inflight: int | None = None

    @staticmethod
    def from_yaml(kind: str, entry: dict) -> "family":
        sizes = {idx: parse_sizes(entry[idx]) for idx in ("m", "n") if idx in entry}
        default = {}
        for dt, size in (entry.get("default") or {}).items():
            # 8x3, or a split's parts along an index: 2+2x4
            default[dt] = tuple(parse_sizes(v)[0] for side in str(size).replace(" ", "").split("x")
                                for v in side.split("+"))
        cases = [(case["kind"], parse_sizes(case["m"]),
                  {**key_params(kind, case), **dict(case.get("params") or {})})
                 for case in (entry.get("cases") or [])]
        # the keys first, explicit params over them
        params = key_params(kind, entry)
        params.update(entry.get("params") or {})
        storages = entry.get("c-storage")
        if storages:
            # C's storages as branches of one kernel: its C the last one's -
            # over a C-layout given, which can't agree with the branches
            from ...flow.stages.ukr.storage import LAYOUTS
            storages = [storages] if isinstance(storages, str) else list(storages)
            params["C-storage"] = storages
            params["C-layout"] = list(LAYOUTS[storages[-1]])
        split = entry.get("split")
        parts = []
        for part in (entry.get("parts") or []):
            # a part's preset: a shorthand or a file (preset: or tileop-preset:)
            pp = key_params(kind, part)
            for key in ("tileop-preset", "tileop-vectorize"):
                if key in part:
                    pp[key] = part[key]
            pp.update(part.get("params") or {})
            # with split-ratios the second part's sizes follow the first's
            parts.append((pp, parse_sizes(part[split]) if split in part else []))
        if parts and split not in ("m", "n"):
            raise ValueError(f"family {entry['family']}: split along m or n, not {split}")
        ratios = parse_ratios(entry["split-ratios"]) if "split-ratios" in entry else []
        if ratios and 2 != len(parts):
            raise ValueError(f"family {entry['family']}: split-ratios relate two parts")
        inflight = entry.get("min-inflight")
        return family(kind=kind, name=entry["family"], dtypes=list(entry.get("dtypes", ["FP64"])),
                      params=params, sizes=sizes, default=default, cases=cases,
                      split=split, parts=parts, ratios=ratios,
                      min_inflight=int(inflight) if inflight is not None else None)


@dataclass
class configuration:
    """
    A blisgen configuration: the ISA, the BLIS configuration's name and the
    families of each kind
    """
    isa: str
    name: str
    families: list[family]
    #: BLIS_STACK_BUF_MAX_SIZE in bytes: given (stack-buf-size, or blisgen's
    #: --stack-buf-size), else from the largest kernel
    stack_buf_size: int | None = None
    #: per data type, the cache blocksizes' defaults (mr-in-mc, nr-in-nc, kc)
    blocksizes: dict = field(default_factory=dict)

    @staticmethod
    def from_files(files: dict, name: str | None = None, stack_buf_size: int | None = None,
                   isa: str | None = None) -> "configuration":
        """
        A configuration from a family file per kernel type and data type -
        files maps (kind, data type), e.g. ("gemm", "FP64"), to a path. A
        file names the ISA and holds one family (or a list under families):
        its params, sizes (m, n), default size, and - gemm - the data type's
        cache blocksizes (mr-in-mc, nr-in-nc, kc). The ISAs must agree
        """
        import yaml
        families, blocksizes = [], {}
        for (kind, dt), path in files.items():
            if path is None:
                continue
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            file_isa = data.get("isa")
            if file_isa is not None:
                if isa is not None and file_isa != isa:
                    raise ValueError(f"{path} is for {file_isa}, the other files for {isa}")
                isa = file_isa
            for entry in data.get("families", [data]):
                entry = dict(entry)
                entry["dtypes"] = [dt]
                if "default" in entry and not isinstance(entry["default"], dict):
                    entry["default"] = {dt: entry["default"]}
                entry.setdefault("family", kind)
                families.append(family.from_yaml(kind, entry))
            if "blocksizes" in data:
                blocksizes[dt] = dict(data["blocksizes"])
        if isa is None:
            raise ValueError("no ISA: a family file names it (isa: ...)")
        return configuration(isa=isa, name=name or f"ukrgen_{isa}", families=families,
                             stack_buf_size=stack_buf_size, blocksizes=blocksizes)

    @staticmethod
    def load(path: str) -> "configuration":
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        families = [family.from_yaml(kind, entry)
                    for kind in ("gemm", "packm") for entry in (data.get(kind) or [])]
        return configuration(isa=data["isa"], name=data.get("config-name", f"ukrgen_{data['isa']}"),
                             families=families, stack_buf_size=data.get("stack-buf-size"),
                             blocksizes=dict(data.get("blocksizes") or {}))


@dataclass
class kernel:
    """
    A kernel built: its family, data type and size (the family's units),
    BLIS's mr and nr (elements, as expressions of the vector length VL), its
    symbol, parameters in order, C's layout ("col" or "row") and the emitted
    program
    """
    family: str
    dtype: str
    size: tuple
    mr: str
    nr: str
    symbol: str
    params: list[str]
    c_layout: str
    program: object
    #: the C reading the size of the vectors it uses, as its generator - and
    #: whatever it groups registers by - writes it
    simd_size_c: str = ""
    #: the C function giving its vector length in elements (cgen assigns it)
    vl_fn: str = "ukrgen_vl"
    #: packm: the case (vec, trans)
    case: str = ""
    #: its loop parameter counts chunks of a vector length ("VL"), not elements
    loop_unit: str = ""
    #: its assembly where built in another process (the program stays there)
    asm: str = ""
    #: C's storages its epilogue branches on (row, col, any), the last the default
    c_storages: list = field(default_factory=list)


def part_extent(ctx, part: int, idx: str) -> sym:
    """
    A part's extent along an index: its register tile's extent times its count
    """
    dims = (getattr(ctx, "part_dims", None) or [ctx.dims] * len(ctx.stos))[part]
    for tiling in ctx.stos[part].values():
        if idx in tiling.extents:
            return sym.extent(tiling.extents[idx]) * dims[idx]
    raise KeyError(idx)


def extent_of(ctx, idx: str) -> sym:
    """
    The microtile's extent along an index - as the model computes it: along a
    split index the parts' extents summed
    """
    if len(ctx.stos) > 1 and idx == getattr(ctx, "split_index", None):
        total = part_extent(ctx, 0, idx)
        for part in range(1, len(ctx.stos)):
            total = total + part_extent(ctx, part, idx)
        return total
    return part_extent(ctx, 0, idx)


def size_name(expr: str) -> str:
    """
    A symbol's spelling of a blocksize: 8, 3v (three vectors), ...
    """
    text = str(expr).replace(" ", "")
    if "VL" == text:
        return "1v"
    if text.endswith("*VL"):
        return text[:-3] + "v"
    return text


def c_storage(layout) -> str:
    """
    The C storage a kernel takes: row or col where one index is contiguous;
    any where both are strided at run time (rows and columns a stride apart,
    C's vectors gathered or strided) - BLIS needn't copy C for it
    """
    contiguous = [str(entry).split(":")[0] for entry in layout if str(entry).endswith(":c")]
    if not contiguous:
        return "any"
    return "row" if "n" == contiguous[0] else "col"


def _skip(dt, size, err) -> tuple:
    lines = [l.strip() for l in str(err).splitlines() if l.strip()]
    return ("skipped", (dt, size, lines[0] if lines else type(err).__name__))


def _done(k: "kernel", detach: bool) -> tuple:
    """
    A kernel built; for another process detached - its assembly rendered,
    the program (not one for pickling) dropped
    """
    if detach:
        k.asm = "\n".join(k.program.function(f"{k.symbol}_asm")) + "\n"
        k.program = None
    return ("built", k)


def _call(item):
    fn, args = item
    return fn(*args, detach=True)


def run_tasks(fn, tasks: list, jobs: int = 1) -> list:
    """
    The tasks - each one run of the flow, independent of the others - in
    order: in this process, or across jobs processes
    """
    if jobs <= 1 or len(tasks) <= 1:
        return [fn(*t, detach=False) for t in tasks]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(_call, [(fn, t) for t in tasks]))


def _collect(results: list) -> tuple[list, list]:
    return ([r for kind, r in results if "built" == kind],
            [r for kind, r in results if "skipped" == kind])


def gemm_one(isa: str, config_name: str, fam: family, dt: str, m: int, n: int,
             detach: bool = False) -> tuple:
    """
    One size of a gemm family: ("built", kernel) or ("skipped", (data type,
    size, reason))
    """
    # unrolled along k once unless the family says otherwise
    params = {"isa": isa, "ukr": "gemm", "k": "1"}
    params.update(fam.params)
    for comp in ("A", "B", "C", "AB", "alpha", "beta"):
        params[f"{comp}-data-type"] = dt
    params.update({"m": str(m), "n": str(n)})
    try:
        ctx, result, _ = run_unrolled(params, "k")
    except Exception as err:
        return _skip(dt, (m, n), err)
    if not getattr(result, "completed", False) or not ctx.emitted:
        return _skip(dt, (m, n), "the flow didn't complete")
    mr, nr = str(extent_of(ctx, "m")), str(extent_of(ctx, "n"))
    layout = params.get("C-layout", ["m:c", "n:s"])
    c_layout = c_storage(layout)
    symbol = f"bli_{DT_CHAR[dt]}gemm_{config_name}_{fam.name}_{size_name(mr)}x{size_name(nr)}"
    program = ctx.emitted[0]
    storages = params.get("C-storage") or []
    return _done(kernel(family=fam.name, dtype=dt, size=(m, n), mr=mr, nr=nr, symbol=symbol,
                        params=list(program.params), c_layout=c_layout, program=program,
                        simd_size_c=getattr(ctx.gen, "c_simd_size_function", ""),
                        c_storages=list(storages) if len(storages) > 1 else []), detach)


def build_gemm(isa: str, config_name: str, fam: family,
               jobs: int = 1) -> tuple[list[kernel], list[tuple]]:
    """
    Every size of a gemm family the ISA can build, and (data type, size,
    reason) for each it can't - the sizes across jobs processes
    """
    if fam.parts:
        return build_split_gemm(isa, config_name, fam, jobs)
    ms, ns = fam.sizes.get("m", [1]), fam.sizes.get("n", [1])
    tasks = [(isa, config_name, fam, dt, m, n) for dt in fam.dtypes for m in ms for n in ns]
    return _collect(run_tasks(gemm_one, tasks, jobs))


def packm_one(isa: str, config_name: str, fam: family, dt: str, case: str, m: int,
              case_params: dict, detach: bool = False) -> tuple:
    """
    One case and size of a packm family
    """
    params = {"isa": isa, "ukr": "pack", "n": "1"}
    params.update(fam.params)
    params.update(case_params)
    for comp in ("X", "Y", "kappa"):
        params[f"{comp}-data-type"] = dt
    params["m"] = str(m)
    if fam.min_inflight:
        # at least min_inflight vectors an iteration: m a copy
        params["n"] = str(max(1, -(-fam.min_inflight // m)))
    try:
        ctx, result, _ = run_unrolled(params, "n")
    except Exception as err:
        return _skip(dt, (case, m), err)
    if not getattr(result, "completed", False) or not ctx.emitted:
        return _skip(dt, (case, m), "the flow didn't complete")
    cdim = str(extent_of(ctx, "m"))
    symbol = f"bli_{DT_CHAR[dt]}packm_{config_name}_{fam.name}_{case}{size_name(cdim)}"
    program = ctx.emitted[0]
    # a loop stepping by vectors counts chunks of a vector length
    unit = "VL" if any(("VL",) in dict(getattr(b, "step", None).terms)
                       for p in ctx.programs for b in p.blocks
                       if getattr(b, "step", None) is not None) else ""
    return _done(kernel(family=fam.name, dtype=dt, size=(m, 1), mr=cdim, nr="1", symbol=symbol,
                        params=list(program.params), c_layout="col", program=program, case=case,
                        loop_unit=unit, simd_size_c=getattr(ctx.gen, "c_simd_size_function", "")),
                 detach)


def build_packm(isa: str, config_name: str, fam: family,
                jobs: int = 1) -> tuple[list[kernel], list[tuple]]:
    """
    Every case and size of a packm family the ISA builds - kernels packing
    a full panel of cdim (mr) rows, n long, scaled by kappa - and (data type,
    (case, size), reason) for each it can't
    """
    tasks = [(isa, config_name, fam, dt, case, m, case_params)
             for dt in fam.dtypes for case, ms, case_params in fam.cases for m in ms]
    return _collect(run_tasks(packm_one, tasks, jobs))


def split_one(isa: str, config_name: str, fam: family, dt: str, combo: tuple, o: int,
              detach: bool = False) -> tuple:
    """
    One combination of a split family's parts' sizes
    """
    split = fam.split
    other = "n" if "m" == split else "m"
    keys = list(dict.fromkeys(k for pp, _ in fam.parts for k in pp))
    params = {"isa": isa, "ukr": "gemm", "k": "1"}
    params.update(fam.params)
    for key in keys:
        values = [pp.get(key) for pp, _ in fam.parts]
        params[key] = values if len(set(map(str, values))) > 1 else values[0]
    for comp in ("A", "B", "C", "AB", "alpha", "beta"):
        params[f"{comp}-data-type"] = dt
    params[split] = [str(c) for c in combo]
    params[other] = str(o)
    size = combo + (o,) if "m" == split else (o,) + combo
    try:
        ctx, result, _ = run_unrolled(params, "k")
    except Exception as err:
        return _skip(dt, size, err)
    if not getattr(result, "completed", False) or not ctx.emitted:
        return _skip(dt, size, "the flow didn't complete")
    mr, nr = str(extent_of(ctx, "m")), str(extent_of(ctx, "n"))
    layout = params.get("C-layout", ["m:c", "n:s"])
    names = "_".join(f"{size_name(part_extent(ctx, p, 'm'))}x{size_name(part_extent(ctx, p, 'n'))}"
                     for p in range(len(ctx.stos)))
    program = ctx.emitted[0]
    return _done(kernel(family=fam.name, dtype=dt, size=size, mr=mr, nr=nr,
                        symbol=f"bli_{DT_CHAR[dt]}gemm_{config_name}_{fam.name}_{names}",
                        params=list(program.params),
                        c_layout=c_storage(layout),
                        program=program,
                        simd_size_c=getattr(ctx.gen, "c_simd_size_function", "")), detach)


def build_split_gemm(isa: str, config_name: str, fam: family,
                     jobs: int = 1) -> tuple[list[kernel], list[tuple]]:
    """
    A split family's kernels: every combination of its parts' sizes along the
    split index, and the family's sizes along the other - each part's
    parameters (its preset - a shorthand or a file - its vectorized index, its
    own choices) a list of one value per part where they differ
    """
    other = "n" if "m" == fam.split else "m"
    tasks = [(isa, config_name, fam, dt, combo, o)
             for dt in fam.dtypes for combo in split_combos(fam) for o in fam.sizes.get(other, [1])]
    return _collect(run_tasks(split_one, tasks, jobs))


def split_combos(fam: family) -> list[tuple]:
    """
    A split family's parts' sizes along the split index: with ratios, the
    first part's sizes, the second's following each ratio a:b of their
    instructions - both parts cover the other index alike, so m1 x n
    instructions against m2 x n: m2 = m1 x b / a, where whole; else every
    combination of the parts' sizes
    """
    import itertools
    if not fam.ratios:
        return list(itertools.product(*[sizes for _, sizes in fam.parts]))
    combos = []
    for first in fam.parts[0][1]:
        for a, b in fam.ratios:
            if 0 == (first * b) % a and (first, first * b // a) not in combos:
                combos.append((first, first * b // a))
    return combos
