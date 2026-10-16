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


        # With --help, stop at the first stage with a question left unanswered:
        # the help then shows everything given so far plus what this stage
        # asks. That includes options argparse doesn't require but the stage
        # does - the solve stage's --<sto>-to, optional only so that
        # --list-to-candidates works before any choice is made. Parsing first
        # would fail on a missing argument instead of helping.
        argv = sys.argv[1:]
        if any(a in argv for a in helpargs):
            def given(pname):
                return any(a == f"--{pname}" or a.startswith(f"--{pname}=") for a in argv)
            def unanswered(pname):
                param = s.get_param(pname)
                return not param.flag and not given(pname) and \
                    (param.required or param.value is None)
            if any(unanswered(p) for p in params):
                self.parser.print_help()
                sys.exit(0)

        args, self.rest = self.parser.parse_known_args()

        for pname in params:

            apname = pname.replace("-", "_")
            val = args.__dict__[apname]

            s.set_param(pname, val)


def main():

    ukr_ctx = ukr_context()

    # No abbreviations: the parser grows stage by stage, so an option of a
    # later stage would be taken for an abbreviation of an earlier one's -
    # --m (a dimension) for --mm-to, silently replacing the chosen
    # implementation.
    parser = ArgumentParser(add_help=False, allow_abbrev=False)

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

    def unrecognized() -> list[str]:
        return [a for a in prolog.rest if a.startswith("-") and a not in helpargs]

    try:
        result = se.run()
    except stage_error as err:
        # asked for help: the parser holds every option up to the stage that
        # couldn't proceed, which is what is needed next
        if any(a in sys.argv[1:] for a in helpargs):
            parser.print_help()
            sys.exit(0)
        print(f"error: {err}", file=sys.stderr)
        if unrecognized():
            print(f"note: not recognized by the stages so far (or mistyped): "
                  f"{' '.join(unrecognized())}", file=sys.stderr)
        sys.exit(2)

    if any(a in prolog.rest for a in helpargs):
        parser.print_help()
        sys.exit(0)

    if not result.completed:
        print(result.output)
        if unrecognized():
            print(f"note: not recognized by the stages so far (or mistyped): "
                  f"{' '.join(unrecognized())}", file=sys.stderr)
        sys.exit(result.code)

    # every stage has run, so anything left over belongs to none of them
    if unrecognized():
        print(f"error: unrecognized arguments: {' '.join(unrecognized())}", file=sys.stderr)
        sys.exit(2)

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
