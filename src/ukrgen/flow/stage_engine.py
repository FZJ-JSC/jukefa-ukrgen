# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Type, Callable

from .stages.stage import stage, early_exit

from .ukr_context import ukr_context


@dataclass
class engine_result:
    """
    Outcome of running the stages.

    :param completed: True if every stage ran; False if one exited early
    :param stage: name of the stage that exited early
    :param output: what the exiting stage produced, e.g. a tool's listing
    :param code: exit status the caller should use
    """
    completed : bool
    stage : str|None = None
    output : str|None = None
    code : int = 0


class stage_engine:
    def __init__(self, stages : list[Type[stage]],
                 ctx : ukr_context,
                 prolog : Callable[[stage],None] = lambda s : None,
                 epilog : Callable[[stage],None] = lambda s : None):

        self.stages = stages
        self.ctx = ctx
        self.prolog = prolog
        self.epilog = epilog


    def run(self) -> engine_result:
        """
        Run every stage and the stages they spawn, in order.

        A stage can stop the run by raising early_exit from progress() - used by
        inspection tools that answer a question instead of producing a kernel.

        :return: whether the run completed, and what an early exit produced
        """
        for stage_ctr in self.stages:
            stage_deque = deque([stage_ctr])
            while stage_deque:
                ctr = stage_deque.popleft()
                s  = ctr(context=self.ctx)

                self.prolog(s)

                # check parameters
                for pname in s.get_parameter_names():
                    if s.params[pname].value is None and \
                            s.params[pname].required:
                        raise ValueError(f"Parameter {pname} is required!")

                try:
                    spawned = s.progress()
                except early_exit as ex:
                    return engine_result(completed=False,
                                         stage=type(s).__name__,
                                         output=ex.output,
                                         code=ex.code)

                stage_deque.extend(spawned or [])
                self.epilog(s)

        return engine_result(completed=True)
