# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

from __future__ import annotations

from ..ukr_context import ukr_context

from ..stage_param import stage_param

class early_exit(Exception):
    """
    Raised from a stage's progress() to stop the run, for tools that answer a
    question about the kernel instead of generating it.

    :param output: text to show the user
    :param code: exit status
    """
    def __init__(self, output : str = "", code : int = 0):
        super().__init__(output)
        self.output = output
        self.code = code


class stage:

    def __init__(self, context : ukr_context):
        self.context  = context
        self.params : dict[str,stage_param] = dict()

    def get_parameter_names(self):
        return list(self.params.keys())

    def set_param(self, name : str, value):
        self.params[name].value = value

    def get_param(self, name : str):
        return self.params[name]

    def progress(self) -> list[stage]:
        """
        Do the stage's work.

        :return: stage classes to run next, before the next stage in the list
        :raises early_exit: to stop the run, e.g. after a tool printed its answer
        """
        return []
