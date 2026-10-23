"""
Hooks: a script's function run before or after a stage of the flow, given
the flow's context - what the stages have built so far (stos, irs,
asmblocks, emitted, ...) - to look at or to change.

A hook is a flow parameter (--hooks; hooks: in a family's params; a
ukropt-sweep setting), each a string

    WHEN STAGE SCRIPT [FUNCTION] [KEY=VALUE ...]

WHEN is before or after; STAGE a stage's name, with or without _stage
(sto, isa_specialize, schedule, emit - and stages others spawn:
lsc_schedule, blis_ukr_codegen, ...); SCRIPT a Python file; FUNCTION its
function, hook if not given, called as FUNCTION(ctx, stage, KEY=VALUE, ...)
with the values as strings. A stage running more than once runs its hooks
each time. Hooks are parsed by the setup stage: none can run before it.
"""
from __future__ import annotations

import importlib.util
import os
import shlex
import sys
from dataclasses import dataclass, field


@dataclass
class hook:
    """
    One hook: when, after or before which stage, what to call
    """
    when: str
    stage: str
    script: str
    function: str = "hook"
    args: dict = field(default_factory=dict)
    ran: int = 0

    def matches(self, when: str, stage_name: str) -> bool:
        return when == self.when and self.stage in (stage_name, stage_name.removesuffix("_stage"))

    def __str__(self):
        args = " ".join(f"{k}={v}" for k, v in self.args.items())
        return f"{self.when} {self.stage} {self.script} {self.function}{' ' + args if args else ''}"


def parse(spec: str) -> hook:
    """
    A hook from its string: WHEN STAGE SCRIPT [FUNCTION] [KEY=VALUE ...]
    """
    words = shlex.split(str(spec))
    if len(words) < 3 or words[0] not in ("before", "after"):
        raise ValueError(f"hook {spec!r}: WHEN STAGE SCRIPT [FUNCTION] [KEY=VALUE ...], "
                         f"WHEN before or after")
    when, stage, script, rest = words[0], words[1], words[2], words[3:]
    function = "hook"
    if rest and "=" not in rest[0]:
        function, rest = rest[0], rest[1:]
    args = {}
    for word in rest:
        key, eq, value = word.partition("=")
        if not eq or not key:
            raise ValueError(f"hook {spec!r}: {word!r} isn't KEY=VALUE")
        args[key] = value
    if not os.path.isfile(script):
        raise ValueError(f"hook {spec!r}: no script {script}")
    return hook(when=when, stage=stage.removesuffix("_stage"), script=script,
                function=function, args=args)


_modules: dict = {}


def _function(h: hook):
    path = os.path.abspath(h.script)
    if path not in _modules:
        spec = importlib.util.spec_from_file_location(
            f"ukrgen_hook_{len(_modules)}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _modules[path] = module
    fn = getattr(_modules[path], h.function, None)
    if not callable(fn):
        raise ValueError(f"hook {h}: {h.script} has no function {h.function}")
    return fn


def run(ctx, stage, when: str):
    """
    The hooks for this stage at this point, in the order given
    """
    name = type(stage).__name__
    for h in getattr(ctx, "hooks", None) or []:
        if h.matches(when, name):
            _function(h)(ctx, stage, **h.args)
            h.ran += 1


def report_unused(ctx, stages_run: list[str]):
    """
    A warning for each hook whose stage never ran - a misspelled stage does
    nothing otherwise
    """
    for h in getattr(ctx, "hooks", None) or []:
        if not h.ran:
            names = ", ".join(dict.fromkeys(n.removesuffix("_stage") for n in stages_run))
            print(f"warning: hook '{h}' never ran: the stages were {names}", file=sys.stderr)
