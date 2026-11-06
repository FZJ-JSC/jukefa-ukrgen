"""
Golden kernels: what the family pipeline emits for a few kernels per ISA -
each configuration's families at their first sizes, and the K1's 2v x 14 -
recorded so a change in ukrgen or in asmgen shows. asmgen's 0.6 rework
(its docs/V06_REWORK.md) keeps them byte-identical except where a phase
says otherwise.

SME and SMESVE are here for the loops over tiles' slices
(docs/ADDRESSING_PLAN.md 6.6) - their kernels aren't part of anyone's
records otherwise. A split family builds several kernels at one size: all of
them are recorded, each after a line naming its symbol.

    python -m tests.flow.golden_kernels record   the kernels anew
    python -m tests.flow.golden_kernels diff     which changed
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "golden_kernels")
ROOT = os.path.dirname(os.path.dirname(HERE))
CONFIGS = ["rvv/fma_vf/dgemm.yaml", "neon/fma_lane/dgemm.yaml", "sve/fma_bc_vindex/dgemm.yaml",
           "avx2/fma_bc_blocks/dgemm.yaml", "avx512/fma_bc_blocks/dgemm.yaml",
           # SME: outer products into ZA tiles, the epilogue slice by slice
           "sme/fopa_bc_vindex/dgemm.yaml", "sme/fopa_bc_vindex/sgemm.yaml",
           # SME and SVE split along m or n, its outer-product part tiled
           "smesve/fopa_fma_split/dgemm.yaml", "smesve/fopa_fma_split/sgemm.yaml",
           "smesve/fopa_fma_split_n/dgemm.yaml"]
EXTRA = [
    ("rvv/fma_vf/dgemm.yaml", "vm", 2, 14),
    # vn in the loop order the reference configurations moved off (knm now):
    # its strided case alternates between a row's vectors - kept to watch
    # changes' effect on the wrong order
    ("sve/fma_bc_vindex/dgemm.yaml", "vn@order=kmn", 4, 2),
    # the SME configurations' defaults: four tiles (the first sizes above one)
    ("sme/fopa_bc_vindex/dgemm.yaml", "opa", 2, 4),
    ("sme/fopa_bc_vindex/sgemm.yaml", "opa", 2, 2),
    # a split along n sizes m instead (fopa_fma_split_n: outer products'
    # tiles along n, the FMA part's vectors along m)
    ("smesve/fopa_fma_split_n/dgemm.yaml", "sf", 2, None),
]
#: packing kernels too: the same loops over slices (a tile's columns out
#: through ZA, ztrans; the last one masked to a run-time count, ztail), both
#: element sizes - (configuration, family, the cases recorded)
PACKM = [
    ("sme/fopa_bc_vindex/dpackm.yaml", "pk", ("ztrans",)),
    ("sme/fopa_bc_vindex/spackm.yaml", "pk", ("ztail",)),
]


def _config(path: str):
    """The configuration as its file names it: dgemm/sgemm, dpackm/spackm"""
    from ukrgen.injectors.blis.families import configuration
    stem = os.path.basename(path)[:-len(".yaml")]
    kind = "packm" if stem.endswith("packm") else "gemm"
    dt = "FP64" if stem.startswith("d") else "FP32"
    return configuration.from_files({(kind, dt): os.path.join(ROOT, "ukrconfig", path)})


def kernels() -> list[tuple]:
    """
    (label, configuration, family, m, n, cases) of every kernel recorded - a
    split family's size along the index it doesn't split (m or n, the other
    None), a packing family's the cases it keeps besides the first
    """
    out = []
    for path in CONFIGS:
        for fam in _config(path).families:
            first = lambda name: (fam.sizes.get(name) or [None])[0]
            out.append((path, fam.name, first("m"), first("n")))
    out += [k for k in EXTRA if k not in out]
    out += [(path, fam, None, None) for path, fam, _ in PACKM]
    cases = {path: keep for path, _, keep in PACKM}
    def label(p, f, m, n):
        # the configuration's file too: fopa_bc_vindex's dgemm and sgemm have
        # the same family and sizes (their labels differed by data type alone)
        if p in cases:
            size = "-".join(cases[p])
        elif m is not None and n is not None:
            size = f"{m}x{n}"
        else:
            size = f"m{m}" if n is None else f"n{n}"
        return f"{p[:-len('.yaml')].replace('/', '-')}-{f}-{size}"
    return [(label(p, f, m, n), p, f, m, n, cases.get(p)) for p, f, m, n in out]


def build(path: str, family: str, m: int, n: int, cases: tuple | None = None) -> str:
    """
    The kernel's assembly - a split family's or a packing family's several,
    each after a line naming its symbol - or why it didn't build
    """
    from ukrgen.injectors.blis.families import build_gemm, build_packm
    from ukrgen.injectors.blis.cgen import asm_source
    cfg = _config(path)
    # family@key=value,...: the family with parameters of its own (a loop order
    # kept against the configuration's: vn under kmn, the order vm mirrors)
    family, _, extra = family.partition("@")
    fam = copy.deepcopy(next(f for f in cfg.families if f.name == family))
    fam.params.update(dict(kv.split("=", 1) for kv in extra.split(",") if kv))
    if cases is not None:
        fam.cases = [c for c in fam.cases if c[0] in cases]
    else:
        fam.sizes = {name: [size] for name, size in (("m", m), ("n", n)) if size is not None}
    build_one = build_packm if cases is not None else build_gemm
    try:
        ok, skipped = build_one(cfg.isa, cfg.name, fam)
    except Exception as err:  # pylint: disable=broad-except
        return f"!{type(err).__name__}: {str(err)[:200]}"
    if not ok:
        return f"!skipped: {skipped[0][2][:200]}" if skipped else "!nothing built"
    if 1 == len(ok):
        return asm_source(ok[0])
    return "\n\n".join(f"### {k.symbol}\n{asm_source(k)}" for k in ok)


def path_of(label: str) -> str:
    return os.path.join(DATA, f"{label}.s")


def main(argv):
    if not argv or argv[0] not in ("record", "diff"):
        sys.exit(__doc__)
    for label, path, fam, m, n, cases in kernels():
        text = build(path, fam, m, n, cases)
        if "record" == argv[0]:
            os.makedirs(DATA, exist_ok=True)
            with open(path_of(label), "w") as f:
                f.write(text)
            print(f"{label}: {'fails: ' + text[:80] if text.startswith('!') else str(len(text.splitlines())) + ' lines'}")
        else:
            old = open(path_of(label)).read() if os.path.exists(path_of(label)) else None
            print(f"{label}: {'new' if old is None else ('same' if old == text else 'CHANGED')}")


if __name__ == "__main__":
    main(sys.argv[1:])
