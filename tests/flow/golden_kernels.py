"""
Golden kernels: what the family pipeline emits for a few kernels per ISA -
each configuration's families at their first sizes, and the K1's 2v x 14 -
recorded so a change in ukrgen or in asmgen shows. asmgen's 0.6 rework
(its docs/V06_REWORK.md) keeps them byte-identical except where a phase
says otherwise.

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
           "avx2/fma_bc_blocks/dgemm.yaml", "avx512/fma_bc_blocks/dgemm.yaml"]
EXTRA = [("rvv/fma_vf/dgemm.yaml", "vm", 2, 14)]


def _config(path: str):
    from ukrgen.injectors.blis.families import configuration
    return configuration.from_files({("gemm", "FP64"): os.path.join(ROOT, "ukrconfig", path)})


def kernels() -> list[tuple]:
    """
    (label, configuration, family, m, n) of every kernel recorded
    """
    out = []
    for path in CONFIGS:
        for fam in _config(path).families:
            m, n = fam.sizes["m"][0], fam.sizes["n"][0]
            out.append((path, fam.name, m, n))
    out += [k for k in EXTRA if k not in out]
    return [(f"{p.split('/')[0]}-{p.split('/')[1]}-{f}-{m}x{n}", p, f, m, n) for p, f, m, n in out]


def build(path: str, family: str, m: int, n: int) -> str:
    """
    The kernel's assembly, or why it didn't build
    """
    from ukrgen.injectors.blis.families import build_gemm
    from ukrgen.injectors.blis.cgen import asm_source
    cfg = _config(path)
    fam = copy.deepcopy(next(f for f in cfg.families if f.name == family))
    fam.sizes = {"m": [m], "n": [n]}
    try:
        ok, skipped = build_gemm(cfg.isa, cfg.name, fam)
    except Exception as err:  # pylint: disable=broad-except
        return f"!{type(err).__name__}: {str(err)[:200]}"
    if not ok:
        return f"!skipped: {skipped[0][2][:200]}"
    return asm_source(ok[0])


def path_of(label: str) -> str:
    return os.path.join(DATA, f"{label}.s")


def main(argv):
    if not argv or argv[0] not in ("record", "diff"):
        sys.exit(__doc__)
    for label, path, fam, m, n in kernels():
        text = build(path, fam, m, n)
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
