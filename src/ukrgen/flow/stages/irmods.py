"""
IR modifications before and after specialization for the ISA
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from ...irmod import lsc as lsc_irmods
from ...irmod.lsc.base import irmod_placement


class irmod_stage_base(stage):
    """
    Runs the IR modifications placed here (see irmod.lsc):

    - required ones whenever they are triggered - an error, naming what is
      missing, if the ISA doesn't meet their requirements
    - optional ones the ISA meets the requirements of, as chosen with the
      stage's option, in the order given; those enabled by default when it
      isn't given

    Every tunable parameter of an available modification is an option
    --<irmod>-<parameter>.
    """

    placement : irmod_placement = None
    option : str = None

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.log = logging.getLogger("IRMOD")
        here = lsc_irmods.irmods_at(self.placement)
        self.available = [m for m in here if not m.unmet_requirements(context)]
        self.required = [m for m in here if m.required]
        optional = [m for m in self.available if not m.required]
        if optional:
            default = [m.name for m in optional if m.default_enabled]
            names = [m.name for m in optional]
            self.params[self.option] = stage_param(
                    value=default, default=default, multi=True, required=False,
                    choices=names + [f"+{n}" for n in names] + [f"-{n}" for n in names],
                    description="IR modifications to run, in order - or changes to the defaults, "
                                "+name and -name only (+structfuse -cluster), in their usual order: " +
                                "; ".join(f"{m.name}: {m.description}" for m in optional))
        for m in self.available:
            for p in m.params:
                self.params[f"{m.name}-{p.name}"] = stage_param(
                        value=p.default, default=p.default, required=False,
                        choices=list(p.choices) if p.choices else None,
                        description=f"{m.name}: {p.description}")

    def run(self, cls):
        values = {}
        for p in cls.params:
            value = self.params[f"{cls.name}-{p.name}"].value
            values[p.name] = p.default if value is None else p.parse(value)
        mod = cls(self.context, **values)
        changed = sum(mod.apply(program) for program in self.context.programs)
        self.log.debug(f"{cls.name}: changed {changed} site(s)")

    def chosen(self) -> list[str]:
        """
        The modifications chosen: as named, in that order - or, given only
        changes (+name, -name), the defaults with those added and removed, in
        the modifications' usual order (a sweep toggling one)
        """
        value = self.params[self.option].value if self.option in self.params else None
        # a string - one given as a value, not a list (a sweep's grid): its
        # names or changes, by commas or spaces
        if isinstance(value, str):
            value = [v for v in value.replace(",", " ").split() if v]
        given = list(value or [])
        changes = [g for g in given if g[:1] in "+-"]
        if not changes:
            return given
        if len(changes) != len(given):
            raise stage_error(f"--{self.option}: names, or changes to the defaults (+name, -name), "
                              f"not both: {given}")
        added = {g[1:] for g in changes if "+" == g[0]}
        removed = {g[1:] for g in changes if "-" == g[0]}
        defaults = set(self.params[self.option].default or [])
        order = [m.name for m in lsc_irmods.irmods_at(self.placement)]
        unknown = sorted((added | removed) - set(order))
        # an unknown one said as a named one would be: kept to be refused
        return [n for n in order if (n in defaults or n in added) and n not in removed] + unknown

    def progress(self):
        for cls in self.required:
            if not cls.triggered(self.context):
                continue
            unmet = cls.unmet_requirements(self.context)
            if unmet:
                raise stage_error(f"{cls.name} is required for this kernel, but the ISA "
                                  f"lacks: {', '.join(unmet)}")
            self.run(cls)
        by_name = {m.name: m for m in self.available}
        chosen = self.chosen()
        for name in chosen:
            if name not in by_name:
                # one this kernel's ISA doesn't meet the requirements of, or
                # none of that name: said, not looked up
                known = {m.name: m for m in lsc_irmods.irmods_at(self.placement)}
                if name in known:
                    unmet = known[name].unmet_requirements(self.context)
                    raise stage_error(f"{name} isn't available for this kernel: {', '.join(unmet)}")
                raise stage_error(f"no IR modification {name} here; these are: {', '.join(sorted(known))}")
            self.run(by_name[name])
        self.finish()
        self.context.params.update(self.params)
        return []

    def finish(self):
        pass


class pre_specialize_irmod_stage(irmod_stage_base):
    """
    IR modifications on the model's IR, before specialization for the ISA
    """
    placement = irmod_placement.PRE_SPECIALIZE
    option = "pre-specialize-irmods"


class post_specialize_irmod_stage(irmod_stage_base):
    """
    IR modifications on the specialized IR, before scheduling.
    --print-modified-ir prints the result and stops.
    """
    placement = irmod_placement.POST_SPECIALIZE
    option = "post-specialize-irmods"

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.params["print-modified-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the IR after the IR modifications and exit")

    def finish(self):
        if self.params["print-modified-ir"].value:
            raise early_exit("\n\n".join(p.render() for p in self.context.programs))
