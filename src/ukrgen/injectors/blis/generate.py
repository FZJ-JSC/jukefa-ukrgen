"""
A blisgen configuration's files: every family's kernels built, their
assembly and BLIS wrappers, the context initialization choosing among them
at run time, the family header - written under a BLIS tree's layout
(kernels/<config>/3, config/<config>) - and a report of the sizes skipped
"""

from __future__ import annotations

import os

from ...flow.isa_map import make_generator
from .families import configuration, build_gemm, build_packm
from .cgen import (asm_source, gemm_wrapper, cntx_init, family_header, stack_buf_size,
                   vl_helpers, packm_dispatch)


def generate(cfg: configuration, out_dir: str, stack_size: int | None = None) -> dict:
    """
    Write the configuration's files under out_dir; stack_size (bytes)
    overrides the configuration's. Returns what was made: the kernels, the
    sizes skipped (data type, size, reason) and the files written
    """
    gen = make_generator(cfg.isa)
    kernels, skipped = [], []
    defaults = {}
    for fam in cfg.families:
        build = {"gemm": build_gemm, "packm": build_packm}.get(fam.kind)
        if build is None:
            continue
        built, missed = build(cfg.isa, cfg.name, fam)
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
        write(f"{'kernels/' + cfg.name + '/1m' if k.case else kdir}/{k.symbol}.S", asm_source(k))
    helpers = vl_helpers(kernels, gen)
    write(f"{kdir}/bli_gemm_{cfg.name}.c",
          "#include \"blis.h\"\n\n" + helpers + "\n" +
          "\n".join(gemm_wrapper(k) for k in kernels if not k.case))
    packs = [dt for dt in ("FP32", "FP64") if any(dt == k.dtype and k.case for k in kernels)]
    if packs:
        write(f"kernels/{cfg.name}/1m/bli_packm_{cfg.name}.c",
              "#include \"blis.h\"\n\n" + helpers + "\n" +
              "\n".join(packm_dispatch(cfg.name, dt, kernels) for dt in packs))
    write(f"config/{cfg.name}/bli_cntx_init_{cfg.name}.c",
          cntx_init(cfg.name, gen, kernels, defaults, cfg.blocksizes))
    size = stack_buf_size(cfg.isa, gen, kernels, stack_size or cfg.stack_buf_size)
    write(f"config/{cfg.name}/bli_family_{cfg.name}.h", family_header(cfg.name, size))
    report = [f"{len(kernels)} kernels, {len(skipped)} sizes skipped, stack temporary {size} bytes"]
    report += [f"skipped {fam} {dt} {m}x{n}: {why}" for fam, dt, (m, n), why in skipped]
    write(f"config/{cfg.name}/blisgen_report.txt", "\n".join(report) + "\n")
    return {"kernels": kernels, "skipped": skipped, "files": written, "stack_buf_size": size}
