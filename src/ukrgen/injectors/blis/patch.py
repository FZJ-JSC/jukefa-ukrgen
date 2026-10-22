"""
A BLIS tree patched with a blisgen configuration: the tree copied, the
configuration registered (config_registry, the architecture's id and
family), its files written - the generated kernels, wrappers, context
initialization and family header, kernel definitions, make definitions,
kernel prototypes - and PR 960 (environment overrides of the cache
blocksizes) applied to frame/base/bli_gks.c
"""

from __future__ import annotations

import datetime
import os
import shutil
import subprocess

from mako.template import Template

from . import templates as T
from .families import configuration
from .generate import generate
from ...codegen.isa_compiler_support import isa_flags

#: PR 960 (flame/blis): BLIS_MR_IN_MC_<dt>, BLIS_NR_IN_NC_<dt>, BLIS_KC_<dt>
#: and their _MAX variants override the selected configuration's blocksizes
PR960 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patches",
                     "pr960-dynamic-blocksizes.diff")


class patch_error(RuntimeError):
    pass


#: insertions placed otherwise than the old templates place them: anchored
#: on what doesn't change from one BLIS to the next - the configuration
#: added at the head of INSERT_GENTCONF's list, not after its last RISC-V
#: entries
ANCHORS = {
    ("frame/include/bli_gentconf_macro_defs.h", 1):
        ("#define INSERT_GENTCONF \\\n", "INSERT_GENTCONF_${configname.upper()} \\\n", True),
}


def register(out_dir: str, params: dict):
    """
    The configuration's registration: each insertion at its anchor
    """
    for rel, insertions in T.patches.items():
        insertions = [ANCHORS.get((rel, i), ins) for i, ins in enumerate(insertions)]
        path = os.path.join(out_dir, rel)
        if not os.path.exists(path):
            raise patch_error(f"{rel} not found in the BLIS tree")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for anchor, text, after in insertions:
            anchor = Template(anchor).render(**params)
            text = Template(text).render(**params)
            at = content.find(anchor)
            if at < 0:
                raise patch_error(f"{rel}: anchor not found: {anchor.strip()[:80]!r}")
            at = at + len(anchor) if after else at
            content = content[:at] + text + content[at:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def apply_pr960(out_dir: str):
    """
    PR 960 into frame/base/bli_gks.c - already there: left as it is
    """
    with open(os.path.join(out_dir, "frame/base/bli_gks.c"), encoding="utf-8") as f:
        if "bli_gks_apply_env_blkszs" in f.read():
            return
    r = subprocess.run(["patch", "-p1", "-d", out_dir, "-i", PR960], capture_output=True, text=True)
    if r.returncode:
        raise patch_error(f"PR 960 doesn't apply to this BLIS: {r.stdout.strip()} {r.stderr.strip()}")


def patch_blis(blis_dir: str, out_dir: str, cfg: configuration, author: str,
               parent: str | None = None, overwrite: bool = False,
               stack_size: int | None = None, jobs: int = 1,
               align: tuple | None = None) -> dict:
    """
    out_dir: a copy of the BLIS tree at blis_dir with the configuration in
    it. parent names a configuration whose kernels it inherits (registry:
    <config>: <config>/<config>/<parent>). Returns generate()'s account
    """
    if os.path.exists(out_dir):
        if not overwrite:
            raise patch_error(f"{out_dir} exists (overwrite it with --overwrite)")
        shutil.rmtree(out_dir)
    shutil.copytree(blis_dir, out_dir, symlinks=True,
                    ignore=shutil.ignore_patterns(".git"))
    params = {"configname": cfg.name, "parent_configname": parent, "author": author,
              "year": datetime.datetime.today().strftime("%Y"),
              "archflags": isa_flags[cfg.isa]}
    params["license"] = Template(T.components["license"]).render(**params)
    register(out_dir, params)
    made = generate(cfg, out_dir, stack_size=stack_size, jobs=jobs, align=align)
    def write(rel, text):
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    name = cfg.name
    write(f"config/{name}/bli_kernel_defs_{name}.h",
          Template(T.files["config/${configname}/bli_kernel_defs_${configname}.h"]).render(**params))
    write(f"config/{name}/make_defs.mk",
          Template(T.files["config/${configname}/make_defs.mk"]).render(**params))
    protos = "".join(f"GEMM_UKR_PROT( {'float' if 'FP32' == k.dtype else 'double'}, "
                     f"{'s' if 'FP32' == k.dtype else 'd'}, {k.symbol[5:]} )\n"
                     for k in made["kernels"])
    write(f"kernels/{name}/bli_kernels_{name}.h", params["license"] + "\n" + protos)
    apply_pr960(out_dir)
    return made
