# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------


import os


def repo_root() -> str:
    """
    The repository's root: the directory holding ukrconfig/, wherever this
    test module sits under it
    :return: the absolute path
    """
    path = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(path, "ukrconfig")):
        parent = os.path.dirname(path)
        if parent == path:
            raise RuntimeError("no ukrconfig/ above this file: not in the repository")
        path = parent
    return path
