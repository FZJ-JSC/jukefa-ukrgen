# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

import logging
import sys

from argparse import ArgumentParser

from ukrgen.flow.stages.stage import stage, stage_error
from ukrgen.flow.stages.setup import setup_stage
from ukrgen.flow.stages.datatype import datatype_stage
from ukrgen.flow.stages.layout import layout_stage
from ukrgen.flow.stages.solve import solve_stage
from ukrgen.flow.stages.dimension import dimension_stage
from ukrgen.flow.stages.sto import sto_stage

from ukrgen.flow.ukr_context import ukr_context
from ukrgen.flow.stage_engine import stage_engine

from ukrgen.logging import setup_loggers

helpargs=['-h','--help']

class argparse_prolog:
    def __init__(self, parser : ArgumentParser):
        self.parser=parser
        self.rest=list()

    def __call__(self, s: stage):
        params = s.get_parameter_names()

        if not params:
            return

        for pname in params:
            param = s.get_param(pname)
            if param.flag:
                self.parser.add_argument(
                    f"--{pname}",
                    action="store_true",
                    help=param.description)
                continue
            self.parser.add_argument(
                f"--{pname}",
                nargs="+" if param.multi else None,
                help=param.description,
                default=param.default,
                choices=param.choices,
                required=param.required)


        # With --help, stop at the first stage still missing a required argument:
        # the help then shows everything given so far plus what this stage needs.
        # Parsing first would fail on that missing argument instead of helping.
        argv = sys.argv[1:]
        if any(a in argv for a in helpargs):
            def given(pname):
                return any(a == f"--{pname}" or a.startswith(f"--{pname}=") for a in argv)
            if any(s.get_param(p).required and not given(p) for p in params):
                self.parser.print_help()
                sys.exit(0)

        args, self.rest = self.parser.parse_known_args()

        for pname in params:

            apname = pname.replace("-", "_")
            val = args.__dict__[apname]

            s.set_param(pname, val)


def main():

    ukr_ctx = ukr_context()

    parser = ArgumentParser(add_help=False)

    parser.add_argument("--debug",
                        help="Enables debug output for a specific subsystem; without any arguments, all debug output is enabled",
                        nargs="*",
                        type=str)

    args,rest = parser.parse_known_args()

    debugall = False
    debug_systems = list()

    if args.debug is not None:
        if len(args.debug) > 0:
            debug_systems = set(args.debug)
        else:
            debugall = True

    setup_loggers(debugall=debugall, debug_systems=debug_systems)

    # The flow is being reworked onto operation signatures. It currently ends
    # once every STO is tiled with its chosen implementation; the later stages
    # (model, scheduling, codegen) still run on the old asmgen API and are
    # reconnected as they are ported.
    stages = [
        setup_stage,
        datatype_stage,
        layout_stage,
        solve_stage,
        dimension_stage,
        sto_stage,
    ]

    prolog = argparse_prolog(parser=parser)

    se = stage_engine(stages=stages,
                      ctx=ukr_ctx,
                      prolog=prolog)

    try:
        result = se.run()
    except stage_error as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(2)

    # prolog won't print help if there are any parameters not consumed
    # by stages
    if any(a in prolog.rest for a in helpargs):
        parser.print_help()
        sys.exit(0)

    if not result.completed:
        print(result.output)
        sys.exit(result.code)

    if "full_function" in ukr_ctx.asmblocks:
        print(ukr_ctx.asmblocks["full_function"])
        return

    for sto in ukr_ctx.to_parts[0]:
        encodings = [part[sto].encoding for part in ukr_ctx.to_parts]
        if 1 == len(set(encodings)):
            encodings = encodings[:1]
        print(f"--{sto}-to " + " ".join(f'"{enc}"' for enc in encodings))
    print("(the flow currently ends after tiling the STOs; see --print-stos)", file=sys.stderr)

if __name__ == "__main__":
    main()
