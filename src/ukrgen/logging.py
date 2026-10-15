# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

from copy import deepcopy
import logging

def setup_loggers(debugall : bool =False, debug_systems : set[str] = list()):
    """
    Show warnings by default, debug output for the named subsystems, or
    everything with debugall.

    Each module logs to a logger named after its subsystem (STO, MATCHING,
    SOLVE, ...). Previously the root logger was set to DEBUG and only a fixed
    list of subsystems was turned back down, so any logger missing from that
    list printed all of its debug output.
    """
    logging.basicConfig(level=logging.DEBUG if debugall else logging.WARNING)

    for name in debug_systems:
        print(f"{name} debug output enabled")
        logging.getLogger(name).setLevel(logging.DEBUG)
