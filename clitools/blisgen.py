# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

import logging
import os
import sys
import tempfile

from argparse import ArgumentParser

from ukrgen.logging import setup_loggers


def main():
    parser = ArgumentParser(
            description="Generate a BLIS configuration from ukrgen kernel families: every "
                        "microtile size a family builds, the microkernel chosen at run time "
                        "(BLIS_MR_<dt>, BLIS_NR_<dt>), the family's default otherwise")
    parser.add_argument("--debug", nargs="*", help="debug output of these systems")
    for kind in ("gemm", "packm"):
        for ch, dt in (("s", "FP32"), ("d", "FP64")):
            parser.add_argument(f"--{ch}{kind}-config",
                                help=f"the {dt} {kind} kernel family (YAML): its ukrgen "
                                     f"parameters, the sizes to try, its default size")
    parser.add_argument("--config-name",
                        help="the BLIS configuration's name (default: ukrgen_<isa>)")
    parser.add_argument("--parent-config-name",
                        help="a configuration whose kernels this one inherits")
    parser.add_argument("--stack-buf-size", type=int,
                        help="BLIS_STACK_BUF_MAX_SIZE in bytes - the temporary microtile of "
                             "partial tiles; default: the largest kernel's tile at the ISA's "
                             "longest vector")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--from-dir", help="patch the BLIS source in this directory")
    source.add_argument("--from-git", action="store_true",
                        help="patch BLIS cloned from github.com/flame/blis")
    parser.add_argument("--temp-dir", help="where --from-git clones to")
    parser.add_argument("--out-dir", required=True,
                        help="the patched BLIS tree; without a BLIS source, the configuration's "
                             "files alone")
    parser.add_argument("--overwrite", action="store_true", help="replace --out-dir")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 1,
                        help="kernels built at once - each one run of the flow, in its own "
                             "process (default: the CPUs there are)")
    parser.add_argument("--author", required=True,
                        help="Author to insert in the copyright string")
    args = parser.parse_args()

    if args.debug is None:
        setup_loggers()
    elif args.debug:
        setup_loggers(debug_systems=set(args.debug))
    else:
        setup_loggers(debugall=True)

    from ukrgen.injectors.blis.families import configuration
    files = {(kind, dt): getattr(args, f"{ch}{kind}_config")
             for kind in ("gemm", "packm") for ch, dt in (("s", "FP32"), ("d", "FP64"))}
    if not any(files.values()):
        parser.error("no family files: give at least --sgemm-config or --dgemm-config")
    cfg = configuration.from_files(files, name=args.config_name,
                                   stack_buf_size=args.stack_buf_size)

    if not args.from_dir and not args.from_git:
        from ukrgen.injectors.blis.generate import generate
        made = generate(cfg, args.out_dir, stack_size=args.stack_buf_size, jobs=args.jobs)
    else:
        from ukrgen.injectors.blis.patch import patch_blis
        blis_dir = args.from_dir
        if args.from_git:
            from git import Repo
            temp_dir = args.temp_dir or tempfile.mkdtemp()
            blis_dir = os.path.join(temp_dir, "vanillablis")
            Repo.clone_from("https://github.com/flame/blis", blis_dir)
        made = patch_blis(blis_dir, args.out_dir, cfg, args.author,
                          parent=args.parent_config_name, overwrite=args.overwrite,
                          stack_size=args.stack_buf_size, jobs=args.jobs)
    print(f"{cfg.name}: {len(made['kernels'])} kernels, {len(made['skipped'])} sizes skipped, "
          f"{len(made['files'])} files under {args.out_dir}")
    for fam, dt, (m, n), why in made["skipped"]:
        logging.getLogger("BLISGEN").info(f"skipped {fam} {dt} {m}x{n}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
