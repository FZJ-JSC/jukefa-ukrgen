"""
Kernel families for blisgen. A family configures how kernels are built - the
ukrgen parameters every size shares: implementation choices (--mm-to,
--store-to, ...), register and preload limits, irmods, scheduling - and the
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
    def prolog(s):
        for name in s.get_parameter_names():
            if name in params:
                s.set_param(name, params[name])
    ctx = ukr_context()
    result = stage_engine(PIPELINE, ctx, prolog=prolog).run()
    return ctx, result


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

    @staticmethod
    def from_yaml(kind: str, entry: dict) -> "family":
        sizes = {idx: parse_sizes(entry[idx]) for idx in ("m", "n") if idx in entry}
        default = {}
        for dt, size in (entry.get("default") or {}).items():
            default[dt] = tuple(parse_sizes(v)[0] for v in str(size).split("x"))
        return family(kind=kind, name=entry["family"], dtypes=list(entry.get("dtypes", ["FP64"])),
                      params=dict(entry.get("params") or {}), sizes=sizes, default=default)


@dataclass
class configuration:
    """
    A blisgen configuration: the ISA, the BLIS configuration's name and the
    families of each kind
    """
    isa: str
    name: str
    families: list[family]

    @staticmethod
    def load(path: str) -> "configuration":
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        families = [family.from_yaml(kind, entry)
                    for kind in ("gemm", "packm") for entry in (data.get(kind) or [])]
        return configuration(isa=data["isa"], name=data.get("config-name", f"ukrgen_{data['isa']}"),
                             families=families)


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


def extent_of(ctx, idx: str) -> sym:
    """
    The microtile's extent along an index: the register tile's extent times
    its count - as the model computes it
    """
    for tiling in ctx.stos[0].values():
        if idx in tiling.extents:
            return sym.extent(tiling.extents[idx]) * ctx.dims[idx]
    raise KeyError(idx)


def size_name(expr: str) -> str:
    """
    A symbol's spelling of a blocksize: 8, 3v (three vectors), ...
    """
    text = str(expr).replace(" ", "")
    if "VL" == text:
        return "v"
    if text.endswith("*VL"):
        return text[:-3] + "v"
    return text


def build_gemm(isa: str, config_name: str, fam: family) -> tuple[list[kernel], list[tuple]]:
    """
    Every size of a gemm family the ISA can build, and (data type, size,
    reason) for each it can't
    """
    built, skipped = [], []
    ms, ns = fam.sizes.get("m", [1]), fam.sizes.get("n", [1])
    for dt in fam.dtypes:
        for m in ms:
            for n in ns:
                # unrolled along k once unless the family says otherwise
                params = {"isa": isa, "ukr": "gemm", "k": "1"}
                params.update(fam.params)
                for comp in ("A", "B", "C", "AB", "alpha", "beta"):
                    params[f"{comp}-data-type"] = dt
                params.update({"m": str(m), "n": str(n)})
                try:
                    ctx, result = run_flow(params)
                except Exception as err:
                    lines = [l.strip() for l in str(err).splitlines() if l.strip()]
                    skipped.append((dt, (m, n), lines[0] if lines else type(err).__name__))
                    continue
                if not getattr(result, "completed", False) or not ctx.emitted:
                    skipped.append((dt, (m, n), "the flow didn't complete"))
                    continue
                mr, nr = str(extent_of(ctx, "m")), str(extent_of(ctx, "n"))
                layout = params.get("C-layout", ["m:c", "n:s"])
                c_layout = "row" if str(layout[0]).startswith("n") else "col"
                symbol = f"bli_{DT_CHAR[dt]}gemm_{config_name}_{fam.name}_" \
                         f"{size_name(mr)}x{size_name(nr)}"
                program = ctx.emitted[0]
                built.append(kernel(family=fam.name, dtype=dt, size=(m, n), mr=mr, nr=nr,
                                    symbol=symbol, params=list(program.params), c_layout=c_layout,
                                    program=program))
    return built, skipped
