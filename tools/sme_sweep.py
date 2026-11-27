#!/usr/bin/env python3
"""
The SME and SMESVE configurations' kernels and their instruction counts: the
sweep to run after a codegen change, the twelve families `ukrconfig/sme` and
`ukrconfig/smesve` build to, with what each one became.

    uv run --group test python tools/sme_sweep.py
    uv run --group test python tools/sme_sweep.py --compare before.txt

A line per family - its kernels and their instructions - then the total and
what didn't build. `--compare` reads a run's output and prints what each
family and the total changed by, so that a step meaning to move the counts
shows what it moved, and one that doesn't stays at +0.

An instruction is what `emitted_program.instructions` has without the data a
program keeps: the entry, the setup, the code of each case, the teardown and
the exit - `--data` counts the kept data too. The totals are this tool's own
baseline (257 kernels, 107,109 instructions at §6.6's sections), not the
figures docs/ADDRESSING_PLAN.md records: those came from a scratch script
whose counter differed, so compare runs of this tool with each other.
"""
import argparse
import os
import sys

from ukrgen.injectors.blis.families import build_gemm, build_packm, configuration

#: the files a configuration directory has, and the kernel type and data type
#: each one's family is
FILES = {"dgemm": ("gemm", "FP64"), "sgemm": ("gemm", "FP32"),
         "dpackm": ("packm", "FP64"), "spackm": ("packm", "FP32")}

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ukrconfig")
ISAS = ("sme", "smesve")


def configs() -> list[tuple[str, str, str]]:
    """
    Every configuration of the SME and SMESVE directories
    :return: (isa, its name, its directory) for each, in name order
    """
    out = []
    for isa in ISAS:
        directory = os.path.join(ROOT, isa)
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                out.append((isa, name, path))
    return out


def files_of(directory : str) -> dict:
    """
    The family files a configuration directory holds
    :param directory: the configuration's
    :return: (kernel type, data type) -> the file, the ones it has
    """
    out = {}
    for stem, key in FILES.items():
        path = os.path.join(directory, f"{stem}.yaml")
        if os.path.exists(path):
            out[key] = path
    return out


def counted(kernels : list, data : bool = False) -> int:
    """
    The instructions a family's kernels have together
    :param kernels: the built kernels
    :param data: count the data they keep too - the constants a broadcast reads
    :return: every kernel's instructions, summed
    """
    return sum(len(kernel.program.instructions(data)) for kernel in kernels)


def sweep(data : bool = False) -> list[tuple[str, int, int, int]]:
    """
    Build every kernel of every configuration and count them
    :param data: count the data each program keeps too
    :return: (family label, kernels, instructions, kernels that didn't build)
             for each, in configuration order
    """
    out = []
    for isa, name, directory in configs():
        config = configuration.from_files(files_of(directory), name=f"{isa}-{name}")
        for family in config.families:
            # the configuration's ISA, not the directory's name: ukrconfig/smesve's
            # files build SME code - streaming SVE, the same isa
            builder = build_gemm if "gemm" == family.kind else build_packm
            built, skipped = builder(config.isa, f"{isa}-{name}", family)
            out.append((f"{isa}/{name}/{family.name}", len(built), counted(built, data),
                        len(skipped)))
    return out


def main(argv : list[str]) -> int:
    """
    Print the sweep, and what it changed since a run
    :param argv: the command line's arguments
    :return: the exit status - 0 where every family built
    """
    summary = (__doc__ or "the SME and SMESVE sweep").strip().splitlines()[0]
    parser = argparse.ArgumentParser(description=summary)
    parser.add_argument("--compare", metavar="RUN", default=None,
                        help="a previous run's output, to print the changes from")
    parser.add_argument("--data", action="store_true",
                        help="count the data each program keeps, not just instructions")
    args = parser.parse_args(argv)

    before = {}
    if args.compare is not None:
        with open(args.compare) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4 and parts[1].isdigit():
                    before[parts[0].rstrip(":")] = int(parts[3])
    rows = sweep(args.data)
    total_kernels = total_instructions = total_skipped = 0
    for label, kernels, instructions, skipped in rows:
        total_kernels += kernels
        total_instructions += instructions
        total_skipped += skipped
        change = ""
        if label in before:
            change = f"  ({instructions - before[label]:+d})"
        suffix = f", {skipped} skipped" if skipped else ""
        print(f"{label}: {kernels} kernels, {instructions} instructions{suffix}{change}")
    print(f"TOTAL: {total_kernels} kernels, {total_instructions} instructions"
          + (f", {total_skipped} skipped" if total_skipped else ""))
    if before:
        print(f"      {total_instructions - sum(before.values()):+d} instructions "
              f"over the {len(before)} families compared")
    return 0 if not total_skipped else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
