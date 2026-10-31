"""
A blisgen configuration's files: every family's kernels built, their
assembly and BLIS wrappers, the context initialization choosing among them
at run time, the family header - written under a BLIS tree's layout
(kernels/<config>/3, config/<config>) - and a report of the sizes skipped
"""

from __future__ import annotations

import os
import sys

from ...flow.isa_map import make_generator
from .families import configuration, build_gemm, build_packm, resolve_blocksizes, UNROLL
from .cgen import (asm_source, gemm_wrapper, cntx_init, family_header, stack_buf_size,
                   vl_helpers, packm_dispatch)


def generate(cfg: configuration, out_dir: str, stack_size: int | None = None,
             jobs: int = 1, align: tuple | None = None,
             loop_align: int | None = None) -> dict:
    """
    Write the configuration's files under out_dir; stack_size (bytes)
    overrides the configuration's. Returns what was made: the kernels, the
    sizes skipped (data type, size, reason) and the files written
    """
    gen = make_generator(cfg.isa)
    kernels, skipped = [], []
    # kernels built at a smaller unroll than their family asks: a family's is
    # a ceiling, halved where a kernel doesn't build (registers - a loop's
    # rings aren't renamed): (family, symbol, asked, got)
    reduced = []
    defaults = {}
    for fam in cfg.families:
        build = {"gemm": build_gemm, "packm": build_packm}.get(fam.kind)
        if build is None:
            continue
        if loop_align and "loop-align" not in fam.params:
            fam.params["loop-align"] = loop_align
        built, missed = build(cfg.isa, cfg.name, fam, jobs)
        # where each kernel's code starts: its family's, else the default
        asked = fam.params.get(UNROLL.get(fam.kind, ""))
        for k in built:
            k.align = fam.align or align
            if asked and k.unroll is not None and k.unroll < int(asked):
                reduced.append((fam.name, k.symbol, int(asked), k.unroll))
        kernels += built
        skipped += [(fam.name,) + s for s in missed]
        for dt, size in fam.default.items():
            defaults.setdefault(dt, size)
    written = []
    def write(rel, text):
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        written.append(rel)
    kdir = f"kernels/{cfg.name}/3"
    for k in kernels:
        # aligned as k.align says, offset past the boundary by nops (asm_source)
        text = asm_source(k)
        write(f"{'kernels/' + cfg.name + '/1m' if k.case else kdir}/{k.symbol}.S", text)
    helpers = vl_helpers(kernels, gen)
    write(f"{kdir}/bli_gemm_{cfg.name}.c",
          "#include \"blis.h\"\n\n" + helpers + "\n" +
          "\n".join(gemm_wrapper(k) for k in kernels if not k.case))
    packs = [dt for dt in ("FP32", "FP64") if any(dt == k.dtype and k.case for k in kernels)]
    # the packm family's dispatch order, where it gives one
    order = next((f.dispatch for f in cfg.families if "packm" == f.kind and f.dispatch), None)
    rest = next((f.vec_rest for f in cfg.families if "packm" == f.kind and f.vec_rest is not None), None)
    tail = next((f.vec_tail for f in cfg.families if "packm" == f.kind), "overlap")
    if packs:
        write(f"kernels/{cfg.name}/1m/bli_packm_{cfg.name}.c",
              "#include \"blis.h\"\n\n" + helpers + "\n" +
              "\n".join(packm_dispatch(cfg.name, dt, kernels, order, rest, tail) for dt in packs))
    write(f"config/{cfg.name}/bli_cntx_init_{cfg.name}.c",
          cntx_init(cfg.name, gen, kernels, defaults, cfg.blocksizes))
    # a data type's blocksizes with no gemm kernel of its own do nothing - the
    # reference's stand there: said, not silently dropped
    given = {dt for dt, spec in cfg.blocksizes.items() if spec != resolve_blocksizes({})}
    for dt in sorted(given - {k.dtype for k in kernels if not k.case}):
        print(f"warning: {dt} blocksizes given, no {dt} gemm kernel: the reference's stand",
              file=sys.stderr)
    size = stack_buf_size(cfg.isa, gen, kernels, stack_size or cfg.stack_buf_size)
    write(f"config/{cfg.name}/bli_family_{cfg.name}.h", family_header(cfg.name, size))
    report = [f"{len(kernels)} kernels, {len(skipped)} sizes skipped, stack temporary {size} bytes"]
    report += [f"skipped {fam} {dt} {'x'.join(str(v) for v in size)}: {why}"
               for fam, dt, size, why in skipped]
    if reduced:
        report.append(f"{len(reduced)} kernel{'s' if len(reduced) > 1 else ''} at a smaller unroll than asked")
    report += [f"unroll {got} of {asked}: {fam} {symbol}" for fam, symbol, asked, got in reduced]
    write(f"config/{cfg.name}/blisgen_report.txt", "\n".join(report) + "\n")
    return {"kernels": kernels, "skipped": skipped, "reduced": reduced, "files": written,
            "stack_buf_size": size}
