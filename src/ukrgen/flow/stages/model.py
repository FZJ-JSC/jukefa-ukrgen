"""
The LSC model stage: tiled STOs as loads, stores and computations
"""

import logging

from asmgen.registers import adt_size

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import storage_class, read_access, write_access, sto_kind
from ...lsc_model.addressing import addr_pattern, arg_value, kernel_values
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
                    description=f"Address registers for {comp} - a number, or an "
                                f"expression of the kernel's sizes m, n, k and its "
                                f"element size e (m/4, 2n-2, min(m+1, 4))", required=False)
            self.params[f"{comp}-addr-pattern"] = stage_param(
                    value="phase" if both else "rotate",
                    default="phase" if both else "rotate",
                    description=f"Which of {comp}'s address registers an access uses: "
                                f"rotate (0,1,2,0,...), blocked:<n> (n accesses per "
                                f"register; n an expression of the kernel's sizes m, n, k "
                                f"and R, its address registers: blocked:mn/R, blocked:2*n/R) "
                                f"or phase (one register per STO and direction)",
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
                    value=None, required=False,
                    description=f"Data registers for {comp}. Fewer than its tiles cycles "
                                f"through them, reloading; a component kept in registers "
                                f"between STOs needs one per tile. Not given: one per tile "
                                f"where the register file holds them, else a share of what "
                                f"the accumulators leave")

        self.params["max-tiles"] = stage_param(
                value="0", default="0", required=False,
                description="At most this many matrix tiles (SME's ZA) a kernel uses - 0: the ISA's "
                            "most for its element type (eight of doubles, four of singles)")
        for comp in self.data_components:
            self.params[f"{comp}-max-data-regs"] = stage_param(
                    value=None, required=False,
                    description=f"At most this many data registers for {comp} where they're "
                                f"fitted (no --{comp}-data-regs): its minimal ring - not loading "
                                f"a tile twice an iteration - comes first where the registers "
                                f"allow")
            self.params[f"{comp}-max-preload"] = stage_param(
                    value=None, required=False,
                    description=f"At most this many loop iterations of {comp}'s tiles loaded "
                                f"ahead: registers beyond its minimal ring, where fitted")
        for comp in self.memory:
            self.params[f"{comp}-subtiling"] = stage_param(
                    value=None, required=False,
                    description=f"How {comp}'s loops over subtiles run, overriding the "
                                f"defaults: ';'-separated [resolution:]key=value,... - unroll "
                                f"(subtiles an iteration takes, a factor keeping the count "
                                f"whole), registers (registers an iteration's temporaries "
                                f"rotate through, up to unroll), order (1 forwards, -1 from "
                                f"the last subtile, where the steps allow it). "
                                f"--list-subtilings shows them")
        default_order = [c.name for c in composition.get_components()]
        self.params["resolve-order"] = stage_param(
                value=default_order, default=default_order, multi=True, required=False,
                description="Order in which an operation's components get their data: "
                            "which memory each operation touches first. Components left "
                            "out follow in their declared order")

        self.params["no-preload"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Do not load a loop's streamed operands an iteration ahead")
        self.params["list-subtilings"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="List the loops over subtiles - their counts, the unrolls keeping "
                            "them whole, their settings - and exit")
        self.params["print-ir"] = stage_param(
                value=False, default=False, flag=True, required=False,
                description="Print the LSC IR and exit")

    def progress(self):
        addressing = {}
        for comp in self.memory:
            esize = adt_size(self.context.component_dts[comp])
            spec = str(self.params[f"{comp}-addr-regs"].value)
            try:
                # a number, or an expression of the kernel's sizes (m, n, k) and
                # its element size e - R would be what this expression computes
                count = arg_value(spec, kernel_values(self.context.dims, esize))
            except ValueError as err:
                raise stage_error(f"--{comp}-addr-regs: {err}") from err
            if count < 1:
                raise stage_error(f"--{comp}-addr-regs must be a positive number, "
                                  f"got {spec} ({count})")
            try:
                pattern = addr_pattern.parse(self.params[f"{comp}-addr-pattern"].value,
                                             kernel_values(self.context.dims, esize, count))
            except ValueError as err:
                raise stage_error(f"--{comp}-addr-pattern: {err}") from err
            addressing[comp] = addressing_plan(count, pattern)

        data_regs = {}
        for comp in self.data_components:
            if self.params[f"{comp}-data-regs"].value is None:
                # fitted to the register file by the model
                continue
            value = str(self.params[f"{comp}-data-regs"].value)
            if not value.isdigit() or int(value) < 1:
                raise stage_error(f"--{comp}-data-regs must be a positive integer, got {value}")
            data_regs[comp] = int(value)

        limits = {}
        for kind in ("max-data-regs", "max-preload"):
            limits[kind] = {}
            for comp in self.data_components:
                value = self.params[f"{comp}-{kind}"].value
                if value is None:
                    continue
                if not str(value).isdigit():
                    raise stage_error(f"--{comp}-{kind} must be a whole number, got {value}")
                limits[kind][comp] = int(value)

        subtilings = {}
        for comp in self.memory:
            value = self.params[f"{comp}-subtiling"].value
            entries = []
            for entry in filter(None, (e.strip() for e in str(value or "").split(";"))):
                tag, _, settings = entry.rpartition(":")
                kv = {}
                for item in filter(None, (i.strip() for i in settings.split(","))):
                    key, _, val = item.partition("=")
                    if key not in ("unroll", "registers", "order") or \
                            not val.lstrip("-").isdigit():
                        raise stage_error(f"--{comp}-subtiling: '{item}' is not unroll=N, "
                                          f"registers=N or order=1|-1")
                    kv[key] = int(val)
                entries.append((tag or None, kv))
            if entries:
                subtilings[comp] = entries
        names = [c.name for c in self.context.composition.get_components()]
        order = list(self.params["resolve-order"].value or [])
        unknown = [c for c in order if c not in names]
        if unknown or len(set(order)) != len(order):
            raise stage_error(f"--resolve-order takes each of {', '.join(names)} at most "
                              f"once, got {' '.join(order)}")
        order += [c for c in names if c not in order]

        parts = list(range(len(self.context.to_parts)))
        if len(parts) > 1 and any(self.context.subtail_stos or []):
            raise stage_error("a split microtile with a subtail is not built yet")
        try:
            # a split microtile's parts in one program
            programs = [program_builder(self.context, parts if len(parts) > 1 else 0, addressing,
                                        data_regs, preload=not self.params["no-preload"].value,
                                        resolve_order=order, subtilings=subtilings,
                                        max_data_regs=limits["max-data-regs"],
                                        max_preload=limits["max-preload"]).build()]
        except model_error as err:
            raise stage_error(str(err)) from err
        self.context.programs = programs

        if self.params["list-subtilings"].value:
            raise early_exit("\n".join(subtiling_listing(self.context, programs))
                             or "no loops over subtiles")
        text = "\n\n".join(p.render() for p in programs)
        if self.params["print-ir"].value:
            raise early_exit(text)
        for line in text.splitlines():
            self.debug(line)

        self.context.params.update(self.params)
        return []


def subtiling_listing(context, programs) -> list[str]:
    """
    One line per loop over subtiles: its component, resolution and direction,
    count, the unrolls keeping it whole, order and settings
    """
    from asmgen.registers import adt_size
    from ...models.load_store_operations import lsc_loop
    lines, seen = [], set()
    for program in programs:
        for block in program.blocks:
            for section in ("prologue", "body", "epilogue", "tail"):
                for op in getattr(block, section, None) or []:
                    if not isinstance(op, lsc_loop):
                        continue
                    comp, st = op.info.get("component"), op.subtiling
                    key = (comp, op.walks[0].anchor.rsln, op.info.get("direction"))
                    if key in seen:
                        continue
                    seen.add(key)
                    unrolls = st.count.count_unrolls(16 // adt_size(context.component_dts[comp]))
                    lines.append(f"{comp} ({key[1]}, {key[2]}): {st.count} subtiles of "
                                 f"{st.shape.dima.size}x{st.shape.dimb.size}; unrolls "
                                 f"{', '.join(map(str, unrolls))}; order {st.order:+d}; unroll "
                                 f"{st.unroll}, registers {st.registers} (--{comp}-subtiling)")
    return lines
