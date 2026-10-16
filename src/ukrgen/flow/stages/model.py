"""
The LSC model stage: tiled STOs as loads, stores and computations
"""

import logging

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import storage_class, read_access, write_access, sto_kind
from ...lsc_model.addressing import addr_pattern
from ...lsc_model.builder import program_builder, addressing_plan, model_error


class model_stage(stage):
    """
    Builds the LSC IR of every part.

    Per memory component it asks how many address registers to use and which
    access uses which (--<c>-addr-regs, --<c>-addr-pattern). A component that is
    loaded and later stored, like C, defaults to two registers and the phase
    pattern: one for its loads, one for its stores, so the stores start where
    the loads did without rewinding.

    --<c>-data-regs gives each component's data registers, except accumulators,
    which get one per tile they accumulate. With fewer registers than tiles, a
    tile still held keeps its register and new data goes where it costs the
    fewest reloads. --resolve-order sets which component's data an operation
    loads first, shaping the order memory is touched in.

    --print-ir prints the IR and stops.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)
        self.debug = logging.getLogger("MODEL").debug
        composition = context.composition
        flow = composition.dataflow()

        loaded, stored = set(), set()
        for (sto, comp), access in flow.items():
            if access.read in (read_access.LOAD, read_access.STREAM):
                loaded.add(comp)
            if access.write in (write_access.MEMORY, write_access.MEMORY_STREAM):
                # a store may write one component into another's memory
                stored.add(composition.get_sto(sto).memory_of(comp))

        self.memory = [c.name for c in composition.get_components()
                       if storage_class.MEMORY == c.storage and (c.name in loaded | stored)]
        for comp in self.memory:
            both = comp in loaded and comp in stored
            self.params[f"{comp}-addr-regs"] = stage_param(
                    value="2" if both else "1", default="2" if both else "1",
                    description=f"Address registers for {comp}", required=False)
            self.params[f"{comp}-addr-pattern"] = stage_param(
                    value="phase" if both else "rotate",
                    default="phase" if both else "rotate",
                    description=f"Which of {comp}'s address registers an access uses: "
                                f"rotate (0,1,2,0,...), blocked:<n> (n accesses per "
                                f"register) or phase (one register per STO and direction)",
                    required=False)

        # Accumulators get one register per tile they accumulate, counted
        # automatically: fewer would mean spilling them, which needs memory
        # to spill to that BLIS kernels don't have.
        self.accumulators = {a for block in composition.all_blocks() if block.is_loop
                             for sto in block.stos for a in composition.accumulators(sto)}
        self.data_components = [c for c in composition.get_parameterized_components()
                                if c not in self.accumulators]
        for comp in self.data_components:
            self.params[f"{comp}-data-regs"] = stage_param(
                    value=None,
                    description=f"Data registers for {comp}. Fewer than its tiles cycles "
                                f"through them, reloading; a component kept in registers "
                                f"between STOs needs one per tile")

        default_order = [c.name for c in composition.get_components()]
        self.params["resolve-order"] = stage_param(
                value=default_order, default=default_order, multi=True, required=False,
                description="Order in which an operation's components get their data: "
                            "which memory each operation touches first. Components left "
                            "out follow in their declared order")

        self.params["no-preload"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Do not load a loop's streamed operands an iteration ahead")
        self.params["print-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the LSC IR and exit")

    def progress(self):
        addressing = {}
        for comp in self.memory:
            count = str(self.params[f"{comp}-addr-regs"].value)
            if not count.isdigit() or int(count) < 1:
                raise stage_error(f"--{comp}-addr-regs must be a positive integer, got {count}")
            try:
                pattern = addr_pattern.parse(self.params[f"{comp}-addr-pattern"].value)
            except ValueError as err:
                raise stage_error(f"--{comp}-addr-pattern: {err}") from err
            addressing[comp] = addressing_plan(int(count), pattern)

        data_regs = {}
        for comp in self.data_components:
            value = str(self.params[f"{comp}-data-regs"].value)
            if not value.isdigit() or int(value) < 1:
                raise stage_error(f"--{comp}-data-regs must be a positive integer, got {value}")
            data_regs[comp] = int(value)

        names = [c.name for c in self.context.composition.get_components()]
        order = list(self.params["resolve-order"].value or [])
        unknown = [c for c in order if c not in names]
        if unknown or len(set(order)) != len(order):
            raise stage_error(f"--resolve-order takes each of {', '.join(names)} at most "
                              f"once, got {' '.join(order)}")
        order += [c for c in names if c not in order]

        try:
            programs = [program_builder(self.context, part, addressing, data_regs,
                                        preload=not self.params["no-preload"].value,
                                        resolve_order=order).build()
                        for part in range(len(self.context.to_parts))]
        except model_error as err:
            raise stage_error(str(err)) from err
        self.context.programs = programs

        text = "\n\n".join(p.render() for p in programs)
        if self.params["print-ir"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)

        self.context.params.update(self.params)
        return []
