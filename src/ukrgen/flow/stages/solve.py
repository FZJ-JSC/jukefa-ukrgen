"""
Choosing how each STO is implemented in hardware ("to"s)
"""

from __future__ import annotations
import warnings
import re

import difflib
import itertools
import logging
from dataclasses import dataclass, field

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import asm_data_type as adt

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import (
    ukr_composition, sto_description, sto_kind, read_access, write_access)
from ...matching.math import transformation as tf, get_operand_io
from ...support.data_move import (
    resolution_registry,
    tfr_key,
    dm_direction as dmd,
    dm_location as dml,
    filter_by_step_requirements,
    transformation_resolution,
)
from ...support.dm_resolutions.direct import direct_provider
from ...support.dm_resolutions.strided import strided_provider
from ...support.tiles import index_extents, ONE
from ...support.dm_resolutions.scalar_reduce import scalar_reduce_provider
from ...support.dm_solver import resolved_operation_chain, repeat_fits
from ...support.encoding import encode_all


def default_registry() -> resolution_registry:
    """
    The data movement resolutions currently available
    """
    registry = resolution_registry()
    direct_provider().register_resolutions(registry)
    scalar_reduce_provider().register_resolutions(registry)
    strided_provider().register_resolutions(registry)
    return registry


@dataclass(frozen=True)
class store_candidate:
    """
    One way to write a component to memory

    :param component: component stored
    :param rtype: register type it is stored from
    :param rsln: data movement resolution doing it
    """
    component : str
    rtype : rgt
    rsln : transformation_resolution
    loc : dml = dml.MEMORY

    def encode(self) -> str:
        return f"{self.component}.{self.rtype.name}:{self.rsln.unique_tag}"


@dataclass(frozen=True)
class store_choice:
    """
    One way to store every component of a store STO
    """
    stores : tuple[store_candidate, ...]

    def encode(self) -> str:
        return " ; ".join(s.encode() for s in self.stores)


@dataclass(frozen=True)
class chosen_to:
    """
    The implementation chosen for one STO in one part

    :param encoding: its selection string
    :param impl: the implementation - an operation chain or a store choice
    """
    encoding : str
    impl : resolved_operation_chain | store_choice


@dataclass(frozen=True)
class to_io:
    """
    Register types an implementation takes operands in and leaves them in

    :param reads: operand -> register type the implementation reads it in
    :param writes: operand -> register type it leaves it in
    :param stores: for a store: operand -> how it accesses memory
    :param axes: for a computation: operand written -> the index its vectors
                 run along as the implementation leaves it (None for a scalar)
    :param memory: for a store: operand -> the memory component it is stored
                   into
    """
    reads : dict[str, rgt]
    writes : dict[str, rgt]
    stores : dict[str, dml] = field(default_factory=dict)
    axes : dict[str, str | None] = field(default_factory=dict)
    memory : dict[str, str] = field(default_factory=dict)


def produced_rtype(impl: resolved_operation_chain, component: str) -> rgt | None:
    """
    Register type an implementation leaves a component in

    :param impl: implementation of a compute STO
    :param component: requirement operand name
    :return: register type of the last write to it, or None if it is not written
    """
    for res, step in zip(reversed(impl.resolved_chain), reversed(impl.math_chain)):
        dest = step.hw_ast.left.name
        if step.name_mapping.get(dest) == component:
            # resident in another register type than the operation's: that
            strat = res.operand_strategies.get((dest, dmd.OUT))
            resident = strat.rsln.resident_rtype
            return resident or res.compute_sg.representative.operands[dest].rtype
    return None


def consumed_rtype(impl: resolved_operation_chain, component: str) -> rgt | None:
    """
    Register type an implementation reads a component in

    :param impl: implementation of a compute STO
    :param component: requirement operand name
    :return: register type of the first read of it, or None if it is not read
    """
    for res, step in zip(impl.resolved_chain, impl.math_chain):
        for hw_name, math_name in step.name_mapping.items():
            if math_name == component and get_operand_io(step.hw_ast, hw_name)[0]:
                strat = res.operand_strategies.get((hw_name, dmd.IN))
                resident = strat.rsln.resident_rtype
                return resident or res.compute_sg.representative.operands[hw_name].rtype
    return None


def vector_axis(gen, impl: resolved_operation_chain, sto: sto_description,
                operand: str) -> str | None:
    """
    The index an operand's vectors run along as an implementation leaves it;
    None for a scalar
    """
    extents = index_extents(gen, impl)
    along = [i for i in sto.live_indices(operand) if i in extents]
    return along[0] if 1 == len(along) else None


def access_for(axis: str | None, layouts: dict[str, str | None], memory: str) -> dml:
    """
    How storing vectors running along axis accesses a memory component: strided
    if that is not the index the memory is contiguous along
    """
    if memory not in layouts or axis is None or axis == layouts[memory]:
        return dml.MEMORY
    return dml.STRIDED_MEMORY


def io_of(sto: sto_description, impl: resolved_operation_chain | store_choice,
          gen=None, layouts: dict[str, str | None] | None = None) -> to_io:
    """
    Register types the implementation of an STO reads and writes its operands
    in, and for the operands it writes, the index their vectors run along
    """
    if sto_kind.STORE == sto.kind:
        return to_io(reads={s.component: s.rtype for s in impl.stores}, writes={},
                     stores={s.component: s.loc for s in impl.stores},
                     memory={s.component: sto.memory_of(s.component) for s in impl.stores})

    reads, writes, axes = {}, {}, {}
    for op in sto.operands:
        is_read, is_written = sto.io(op)
        if is_read and (rtype := consumed_rtype(impl, op)) is not None:
            reads[op] = rtype
        if is_written and (rtype := produced_rtype(impl, op)) is not None:
            writes[op] = rtype
            if gen is not None:
                axes[op] = vector_axis(gen, impl, sto, op)
    return to_io(reads=reads, writes=writes, axes=axes)


def check_part_chain(composition: type[ukr_composition],
                     ios: dict[str, to_io],
                     layouts: dict[str, str | None] | None = None) -> list[str]:
    """
    Find where one part's implementations disagree, along every path through
    the kernel: an STO reading a component that an earlier STO left in
    registers must read it in the register type that STO left it in, and a
    store must access memory strided exactly when the vectors it stores run
    along an index the memory is not contiguous along. With fused
    implementations each part is its own chain - a part whose mm accumulates
    in ZA needs scales and stores working from ZA in every case.

    Only components already in registers are checked; loaded and zeroed ones
    have no earlier producer. Paths through STOs without an implementation in
    ios are skipped.

    :return: one line per disagreement, naming the case; empty if consistent
    """
    how = {dml.MEMORY: "contiguous", dml.STRIDED_MEMORY: "strided"}
    problems: list[str] = []
    for case, path in composition.paths():
        if any(name not in ios for block in path for name in block.stos):
            continue
        where = f"case {case.label}: " if case is not None else ""
        flow = composition.dataflow(path)
        held: dict[str, tuple[rgt, str]] = {}
        axes: dict[str, str | None] = {}
        for block in path:
            for name in block.stos:
                io = ios[name]
                for op in composition.get_sto(name).operands:
                    if read_access.RESIDENT != flow[(name, op)].read:
                        continue
                    reads, left = io.reads.get(op), held.get(op)
                    if reads is not None and left is not None and reads != left[0]:
                        problems.append(f"{where}{name} reads {op} from {reads.name}, but "
                                        f"{left[1]} leaves it in {left[0].name}")
                    if op in io.stores and left is not None and op in axes:
                        needed = access_for(axes[op], layouts or {}, io.memory.get(op, op))
                        if io.stores[op] != needed:
                            problems.append(f"{where}{name} stores {op} {how[io.stores[op]]}, "
                                            f"but as {left[1]} leaves it the store has to be "
                                            f"{how[needed]}")
                for op, rtype in io.writes.items():
                    held[op] = (rtype, name)
                    if op in io.axes:
                        axes[op] = io.axes[op]
    return list(dict.fromkeys(problems))


class solve_stage(stage):
    SHOWN_CANDIDATES = 10

    """
    For every STO, finds the hardware implementations available for the chosen
    ISA and data types and asks which to use (--<sto>-to).

    Fusing implementations - e.g. an SME outer product next to SVE FMAs - splits
    the microtile into parts, each with its own chain of implementations through
    every STO: what one part's mm leaves in ZA, that part's scale and store must
    take from ZA. So every --<sto>-to takes one value per part, or a single value
    used by every part. The number of parts is the longest list given.

    --list-tileop-candidates prints every candidate and stops.

    Implementations depend on the data types, which is why candidates are only
    computed here and not offered as choices earlier: a data type combination
    no implementation supports is reported at this point.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        self.debug = logging.getLogger("SOLVE").debug

        for sto in context.composition.get_sto_descriptions():
            self.params[f"{sto.name}-tileop"] = stage_param(
                    value=None,
                    description=f"Implementation of {sto.name}: one per part of the "
                                f"microtile, or one for all parts. A candidate string "
                                f"or its index from --list-tileop-candidates",
                    required=False,
                    multi=True)

        for block in context.composition.all_blocks():
            if not block.is_loop:
                continue
            for name in block.stos:
                if sto_kind.COMPUTE != context.composition.get_sto(name).kind:
                    continue
                # optional: an empty default, so it is not a question --help
                # stops at
                self.params[f"{name}-subtail-tileop"] = stage_param(
                        value=[],
                        default=[],
                        description=f"Implementation for the remainder of the loop over "
                                    f"{block.loop_index} shorter than one operation of "
                                    f"--{name}-tileop: a candidate covering one element of "
                                    f"{block.loop_index}. Only for an implementation "
                                    f"covering more; without it the loop count must be "
                                    f"a multiple of what that covers",
                        required=False,
                        multi=True)

        self.params["tileop-preset"] = stage_param(
                value=None, required=False,
                description="Every STO's tile operation from a preset - a shorthand (gemm_fma_bc, "
                            "gemm_fma_bc_vindex, gemm_fma_bc_blocks, gemm_fma_vf, "
                            "gemm_fma_blocklane_vindex, gemm_fopa_bc_vindex) or a YAML file of "
                            "the same form: for each STO the first of the preset's alternatives "
                            "the ISA offers. --COMP-tileop given wins")
        self.params["tileop-vectorize"] = stage_param(
                value=None, required=False,
                description="The index the preset's vectors run along (m, n): its variant. "
                            "Not given: C's contiguous index first, then the others")
        self.params["list-tileop-candidates"] = stage_param(
                value=False,
                default=False,
                description="List the implementation candidates of every STO and exit",
                required=False,
                flag=True)

    # --- candidates ------------------------------------------------------

    def compute_candidates(self, sto: sto_description,
                           registry: resolution_registry) -> dict[str, resolved_operation_chain]:
        """
        Implementations of a compute STO, keyed by their encoding
        """
        io_dts = {op: self.context.component_dts[op] for op in sto.operands}
        layouts = {op: self.context.component_layouts[op] for op in sto.operands
                   if op in self.context.component_layouts}
        impls = self.context.osb.find_hw_implementations(
                req=sto.req, registry=registry, io_dts=io_dts,
                io_locs=self.operand_locations(sto), io_layouts=layouts)
        encodings = encode_all(impls, sto.req)
        return dict(sorted(zip(encodings, impls)))

    def operand_locations(self, sto: sto_description) -> dict[str, tuple[dml, dml]]:
        """
        Where each operand of a compute STO comes from and goes to, as the
        composition's data flow says: loaded or streamed operands come from
        memory, while zeroed and resident ones are already in registers. Compute
        STOs leave their results in registers; store STOs write memory.
        """
        flow = self.context.composition.dataflow()
        locs = {}
        for op in sto.operands:
            access = flow[(sto.name, op)]
            loc_in = dml.REGISTER if access.read in (read_access.RESIDENT,
                                                     read_access.ZERO) else dml.MEMORY
            loc_out = dml.REGISTER if access.write in (None, write_access.REGISTER) \
                else dml.MEMORY
            locs[op] = (loc_in, loc_out)
        return locs

    def store_candidates(self, sto: sto_description, registry: resolution_registry,
                         producible: dict[str, set]) -> dict[str, store_choice]:
        """
        Ways to store all components of a store STO: one store per component,
        for every register type and vector direction an earlier STO could leave
        it in, into the memory it is stored to
        """
        per_component = []
        for comp in sto.store_components:
            memory = sto.memory_of(comp)
            dt = self.context.component_dts[memory]
            kinds = {(rtype, access_for(axis, self.context.component_layouts, memory))
                     for rtype, axis in producible.get(comp, set())}
            stores = []
            for rtype, loc in sorted(kinds, key=lambda p: (p[0].name, p[1].name)):
                seen = set()
                for tfs in (frozenset({tf.NONE}), frozenset()):
                    key = tfr_key(tfs=tfs, rtype=rtype, ddir=dmd.OUT, loc=loc)
                    for rsln in registry.tfr_map.get(key, []):
                        if rsln.unique_tag in seen or not self.steps_supported(rsln, dt):
                            continue
                        seen.add(rsln.unique_tag)
                        stores.append(store_candidate(component=comp, rtype=rtype,
                                                      rsln=rsln, loc=loc))
            per_component.append(stores)

        choices = [store_choice(stores=combo) for combo in itertools.product(*per_component)]
        return dict(sorted((c.encode(), c) for c in choices))

    def steps_supported(self, rsln: transformation_resolution, dt: adt) -> bool:
        """
        Whether every data movement step of a resolution has an instruction
        """
        for step in rsln.steps:
            op = getattr(self.context.gen, step.op, None)
            if op is None:
                return False
            sigs = filter_by_step_requirements(op.get_signatures(), step, dt)
            if not [s for s in sigs if repeat_fits(self.context.gen, s, step, dt)]:
                return False
        return True

    def all_candidates(self) -> dict[str, dict]:
        """
        Candidates of every STO of every case, in the order the kernel first
        runs them. Stores are offered for whatever any implementation before
        them in any case could leave
        """
        composition = self.context.composition
        registry = default_registry()
        order = composition.sto_order()

        candidates: dict[str, dict] = {}
        producible: dict[str, set] = {}
        for name in order:
            sto = composition.get_sto(name)
            if sto_kind.COMPUTE != sto.kind:
                continue
            cands = self.compute_candidates(sto, registry)
            for impl in cands.values():
                for op in sto.operands:
                    if sto.io(op)[1] and (rtype := produced_rtype(impl, op)) is not None:
                        producible.setdefault(op, set()).add(
                            (rtype, vector_axis(self.context.gen, impl, sto, op)))
            candidates[name] = cands
        for name in order:
            sto = composition.get_sto(name)
            if sto_kind.STORE == sto.kind:
                candidates[name] = self.store_candidates(sto, registry, producible)
        return {name: candidates[name] for name in order}

    def listing(self, candidates: dict[str, dict]) -> str:
        """
        Human-readable list of every candidate, by case
        """
        composition = self.context.composition
        dts = " ".join(f"{c}={dt.name}" for c, dt in self.context.component_dts.items())
        lines = [f"{self.context.params['ukr'].value} on {self.context.params['isa'].value}: {dts}",
                 "Give each --<sto>-to one candidate per part of the microtile, or one "
                 "for all parts."]
        shown: set[str] = set()
        for case, path in composition.paths():
            if case is not None:
                lines += ["", f"case {case.label}:"]
            for block in path:
                for name in block.stos:
                    if name in shown:
                        if case is not None and any(block is b for b in case.blocks):
                            lines.append(f"  {name}: listed above")
                        continue
                    shown.add(name)
                    cands = candidates[name]
                    where = f", inside the loop over {block.loop_index}" if block.is_loop else ""
                    lines.append("")
                    lines.append(f"{name}{where}: {len(cands)} candidate(s)")
                    if block.is_loop and sto_kind.COMPUTE == composition.get_sto(name).kind:
                        lines.append(f"  (--{name}-subtail-tileop takes one covering a single "
                                     f"element of {block.loop_index}, for a main one "
                                     f"covering more)")
                    if not cands:
                        lines.append("    none for these data types")
                    width = len(str(max(len(cands) - 1, 0)))
                    for i, enc in enumerate(cands):
                        lines.append(f"  [{i:>{width}}] --{name}-tileop \"{enc}\"")
        return "\n".join(lines)

    def select(self, name: str, values: list[str], cands: dict[str, object]) -> list[str]:
        """
        Resolve a --<sto>-to selection to candidate encodings

        :raises stage_error: on an unknown or missing selection
        """
        if not cands:
            raise stage_error(
                f"{name}: no implementation for data types "
                f"{ {op: self.context.component_dts[op].name for op in self.sto_operands(name)} }")
        if not values:
            shown = list(enumerate(cands))[:self.SHOWN_CANDIDATES]
            more = len(cands) - len(shown)
            raise stage_error(
                f"--{name}-tileop is required ({len(cands)} candidates):\n" +
                "\n".join(f"  [{i}] {enc}" for i, enc in shown) +
                (f"\n  ... and {more} more: --list-tileop-candidates lists them all"
                 if more > 0 else ""))

        encodings = list(cands)
        chosen = []
        for value in values:
            value = value.strip()
            # op names before asmgen 0.6 renamed fadd and fmul: the same candidates
            renamed = re.sub(r"(?<![\w.])f(mul|add)(?=[(\[])", r"\1", value)
            if renamed != value:
                warnings.warn(f"--{name}-tileop: fmul and fadd are mul and add (asmgen 0.6): {value}",
                              DeprecationWarning, stacklevel=2)
                value = renamed
            if value.isdigit() and int(value) < len(encodings):
                chosen.append(encodings[int(value)])
            elif value in cands:
                chosen.append(value)
            else:
                close = difflib.get_close_matches(value, encodings, n=3, cutoff=0.6)
                hint = ("\nClosest candidates:\n" + "\n".join(f"  {c}" for c in close)) \
                    if close else "\nSee --list-tileop-candidates"
                raise stage_error(f"--{name}-tileop: not a candidate: {value}{hint}")
        return chosen

    def loop_extent(self, impl, index: str):
        return index_extents(self.context.gen, impl).get(index, ONE)

    def select_subtails(self, candidates: dict, parts: list[dict[str, str]]) -> list[dict]:
        """
        Subtail implementations per part: each covers one element of the loop
        index where the main one covers more, and leaves the accumulators in
        the registers the main one uses
        """
        composition = self.context.composition
        subtails: list[dict] = [dict() for _ in parts]
        for block in composition.all_blocks():
            if not block.is_loop:
                continue
            k = block.loop_index
            for name in block.stos:
                key = f"{name}-subtail-tileop"
                values = self.params[key].value if key in self.params else None
                if not values:
                    continue
                if len(values) not in (1, len(parts)):
                    raise stage_error(f"--{key} has {len(values)} values for {len(parts)} "
                                      f"parts: give one per part, or one for all parts")
                chosen = self.select(f"{name}-subtail", values, candidates[name])
                chosen = chosen * len(parts) if 1 == len(chosen) else chosen
                for i, enc in enumerate(chosen):
                    main = candidates[name][parts[i][name]]
                    impl = candidates[name][enc]
                    if ONE == self.loop_extent(main, k):
                        raise stage_error(
                            f"--{key}: not needed, --{name}-tileop already covers one element "
                            f"of {k} per operation")
                    if ONE != self.loop_extent(impl, k):
                        raise stage_error(f"--{key}: {enc} covers more than one element of {k}")
                    for acc in sorted(composition.accumulators(name)):
                        if produced_rtype(impl, acc) != produced_rtype(main, acc):
                            raise stage_error(
                                f"--{key}: {enc} leaves {acc} in "
                                f"{produced_rtype(impl, acc).name}, the main implementation "
                                f"in {produced_rtype(main, acc).name}")
                    subtails[i][name] = chosen_to(encoding=enc, impl=impl)
        return subtails

    def apply_preset(self, candidates: dict, order: list[str]):
        """
        The STOs given no tile operation take the preset's (--tileop-preset)
        """
        preset_name = self.params["tileop-preset"].value
        if not preset_name:
            return
        from .. import presets
        given = {n for n in order if self.params[f"{n}-tileop"].value}
        # one preset - and vectorized index - per part of a split microtile,
        # or one for all
        names = list(preset_name) if isinstance(preset_name, (list, tuple)) else [preset_name]
        vectorize = self.params["tileop-vectorize"].value
        vectorize = list(vectorize) if isinstance(vectorize, (list, tuple)) else [vectorize] * len(names)
        if len(vectorize) != len(names):
            raise stage_error(f"--tileop-vectorize has {len(vectorize)} values for "
                              f"{len(names)} presets")
        per_part = []
        aliases = self.context.composition.storage_aliases
        by_suffix = {storage[0]: alias for alias, storage in aliases.items()}
        def with_copies(preset):
            # a storage's copies of the epilogue STOs (store.r, ...) take their
            # STO's entry, C renamed to the storage's alias of it
            import re
            tileops = dict(preset["tileops"])
            for n in order:
                if "." not in n:
                    continue
                base, suffix = n.split(".", 1)
                alias = by_suffix.get(suffix)
                if alias and base in tileops:
                    rename = lambda t: re.sub(r"(?<![A-Za-z0-9_])C\.", f"{alias}.", t)
                    t = tileops[base]
                    tileops[n] = [rename(x) for x in t] if isinstance(t, list) else rename(t)
            return dict(preset, tileops=tileops)
        for name, vec in zip(names, vectorize):
            try:
                per_part.append(presets.select(
                    with_copies(presets.load(str(name))), {n: candidates[n] for n in order if n in candidates},
                    given, vectorize=vec or None,
                    # with C's storages as branches each STO's C - C or an
                    # alias of it - has its own contiguous index
                    contiguous=dict({c: (self.context.component_layouts or {}).get(c)
                                     for c in ["C", *aliases]}, __by_suffix__=by_suffix) if aliases
                    else (self.context.component_layouts or {}).get("C")))
            except ValueError as err:
                raise stage_error(f"--tileop-preset {name}: {err}") from err
        for sto in dict.fromkeys(k for chosen in per_part for k in chosen):
            values = [chosen.get(sto) for chosen in per_part]
            if None in values:
                raise stage_error(f"--tileop-preset: the parts' presets don't all give {sto} "
                                  f"a tile operation")
            self.params[f"{sto}-tileop"].value = values if len(set(values)) > 1 else values[:1]

    def sto_operands(self, name: str) -> tuple[str, ...]:
        return self.context.composition.get_sto(name).operands

    def progress(self):
        candidates = self.all_candidates()

        if self.params["list-tileop-candidates"].value:
            raise early_exit(self.listing(candidates))

        composition = self.context.composition
        order = composition.sto_order()
        self.apply_preset(candidates, order)

        given = {name: self.params[f"{name}-tileop"].value or [] for name in order}
        nparts = max([len(values) for values in given.values()] + [1])

        parts: list[dict[str, str]] = [dict() for _ in range(nparts)]
        for name in order:
            values = given[name]
            if values and len(values) not in (1, nparts):
                raise stage_error(f"--{name}-tileop has {len(values)} values for {nparts} "
                                  f"parts: give one per part, or one for all parts")
            chosen = self.select(name, values, candidates[name])
            if 1 == len(chosen):
                chosen = chosen * nparts
            for part, enc in zip(parts, chosen):
                part[name] = enc

        problems = []
        for i, part in enumerate(parts):
            ios = {name: io_of(composition.get_sto(name), candidates[name][enc],
                               self.context.gen, self.context.component_layouts)
                   for name, enc in part.items()}
            where = f"part {i + 1}: " if nparts > 1 else ""
            problems.extend(where + p for p in check_part_chain(
                composition, ios, self.context.component_layouts))
        if problems:
            raise stage_error("the chosen implementations disagree about register types:\n" +
                              "\n".join(f"  {p}" for p in problems))

        self.context.subtail_parts = self.select_subtails(candidates, parts)

        self.context.to_parts = [
            {name: chosen_to(encoding=enc, impl=candidates[name][enc])
             for name, enc in part.items()}
            for part in parts]
        for i, part in enumerate(parts):
            self.debug(f"part {i + 1}: {part}")

        self.context.to_candidates = candidates
        self.context.params.update(self.params)
        return []
