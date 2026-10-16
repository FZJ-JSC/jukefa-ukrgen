"""
Choosing how each STO is implemented in hardware ("to"s)
"""

from __future__ import annotations

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
from ...support.tiles import index_extents
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
    :param stores: operand -> how storing it accesses memory: as an
                   implementation leaves it, what a store must do; for a store,
                   what it does
    """
    reads : dict[str, rgt]
    writes : dict[str, rgt]
    stores : dict[str, dml] = field(default_factory=dict)


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
            return res.compute_sg.representative.operands[dest].rtype
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
                return res.compute_sg.representative.operands[hw_name].rtype
    return None


def memory_access(gen, impl: resolved_operation_chain, sto: sto_description,
                  operand: str, layouts: dict[str, str | None]) -> dml:
    """
    How an operand as an implementation holds it maps onto memory: strided if
    its vector runs along an index the operand isn't contiguous along
    """
    if operand not in layouts:
        return dml.MEMORY
    extents = index_extents(gen, impl)
    along = [i for i in sto.live_indices(operand) if i in extents]
    if 1 == len(along) and along[0] != layouts[operand]:
        return dml.STRIDED_MEMORY
    return dml.MEMORY


def io_of(sto: sto_description, impl: resolved_operation_chain | store_choice,
          gen=None, layouts: dict[str, str | None] | None = None) -> to_io:
    """
    Register types the implementation of an STO reads and writes its operands in
    """
    if sto_kind.STORE == sto.kind:
        return to_io(reads={s.component: s.rtype for s in impl.stores}, writes={},
                     stores={s.component: s.loc for s in impl.stores})

    reads, writes = {}, {}
    for op in sto.operands:
        is_read, is_written = sto.io(op)
        if is_read and (rtype := consumed_rtype(impl, op)) is not None:
            reads[op] = rtype
        if is_written and (rtype := produced_rtype(impl, op)) is not None:
            writes[op] = rtype
    stores = {op: memory_access(gen, impl, sto, op, layouts or {})
              for op in writes} if gen is not None else {}
    return to_io(reads=reads, writes=writes, stores=stores)


def check_part_chain(composition: type[ukr_composition],
                     ios: dict[str, to_io]) -> list[str]:
    """
    Find where one part's implementations disagree about register types: an STO
    reading a component left in registers by an earlier STO must read it in the
    register type that STO left it in. With fused implementations each part is
    its own chain - a part whose mm accumulates in ZA needs a scale and a store
    working from ZA, while another part's work from Z registers.

    Only components already in registers are checked; loaded and zeroed ones
    have no earlier producer.

    :param composition: the microkernel
    :param ios: STO name -> register types its chosen implementation uses
    :return: one line per disagreement; empty if the chain is consistent
    """
    flow = composition.dataflow()
    held: dict[str, tuple[rgt, str]] = {}
    held_access: dict[str, dml] = {}
    problems = []
    for block in composition.get_blocks():
        for name in block.stos:
            io = ios[name]
            for op in composition.get_sto(name).operands:
                if read_access.RESIDENT != flow[(name, op)].read:
                    continue
                reads, left = io.reads.get(op), held.get(op)
                if reads is not None and left is not None and reads != left[0]:
                    problems.append(f"{name} reads {op} from {reads.name}, but "
                                    f"{left[1]} leaves it in {left[0].name}")
                stores, needed = io.stores.get(op), held_access.get(op)
                if stores is not None and needed is not None and stores != needed \
                        and left is not None:
                    how = {dml.MEMORY: "contiguous", dml.STRIDED_MEMORY: "strided"}
                    problems.append(f"{name} stores {op} {how[stores]}, but as {left[1]} "
                                    f"leaves it the store has to be {how[needed]}")
            for op, rtype in io.writes.items():
                held[op] = (rtype, name)
                if op in io.stores:
                    held_access[op] = io.stores[op]
    return problems


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

    --list-to-candidates prints every candidate and stops.

    Implementations depend on the data types, which is why candidates are only
    computed here and not offered as choices earlier: a data type combination
    no implementation supports is reported at this point.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        self.debug = logging.getLogger("SOLVE").debug

        for sto in context.composition.get_sto_descriptions():
            self.params[f"{sto.name}-to"] = stage_param(
                    value=None,
                    description=f"Implementation of {sto.name}: one per part of the "
                                f"microtile, or one for all parts. A candidate string "
                                f"or its index from --list-to-candidates",
                    required=False,
                    multi=True)

        self.params["list-to-candidates"] = stage_param(
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
                         producible: dict[str, set[rgt]]) -> dict[str, store_choice]:
        """
        Ways to store all components of a store STO: one store per component, for
        every register type an earlier STO could leave it in
        """
        per_component = []
        for comp in sto.store_components:
            dt = self.context.component_dts[comp]
            stores = []
            for rtype, loc in sorted(producible.get(comp, set()),
                                     key=lambda p: (p[0].name, p[1].name)):
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
        Candidates of every STO, in block order
        """
        composition = self.context.composition
        registry = default_registry()

        candidates: dict[str, dict] = {}
        producible: dict[str, set[rgt]] = {}

        for block in composition.get_blocks():
            for name in block.stos:
                sto = composition.get_sto(name)
                if sto_kind.COMPUTE == sto.kind:
                    cands = self.compute_candidates(sto, registry)
                    for impl in cands.values():
                        for op in sto.operands:
                            if sto.io(op)[1]:
                                rtype = produced_rtype(impl, op)
                                if rtype is not None:
                                    access = memory_access(
                                        self.context.gen, impl, sto, op,
                                        self.context.component_layouts)
                                    producible.setdefault(op, set()).add((rtype, access))
                else:
                    cands = self.store_candidates(sto, registry, producible)
                candidates[name] = cands
        return candidates

    # --- listing -----------------------------------------------------------

    def listing(self, candidates: dict[str, dict]) -> str:
        """
        Human-readable list of every candidate
        """
        composition = self.context.composition
        dts = " ".join(f"{c}={dt.name}" for c, dt in self.context.component_dts.items())
        lines = [f"{self.context.params['ukr'].value} on {self.context.params['isa'].value}: {dts}",
                 "Give each --<sto>-to one candidate per part of the microtile, or one "
                 "for all parts."]

        for block in composition.get_blocks():
            for name in block.stos:
                cands = candidates[name]
                where = f", inside the loop over {block.loop_index}" if block.is_loop else ""
                lines.append("")
                lines.append(f"{name}{where}: {len(cands)} candidate(s)")
                if not cands:
                    lines.append("    none for these data types")
                width = len(str(max(len(cands) - 1, 0)))
                for i, enc in enumerate(cands):
                    lines.append(f"  [{i:>{width}}] --{name}-to \"{enc}\"")
        return "\n".join(lines)

    # --- selection ---------------------------------------------------------

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
                f"--{name}-to is required ({len(cands)} candidates):\n" +
                "\n".join(f"  [{i}] {enc}" for i, enc in shown) +
                (f"\n  ... and {more} more: --list-to-candidates lists them all"
                 if more > 0 else ""))

        encodings = list(cands)
        chosen = []
        for value in values:
            value = value.strip()
            if value.isdigit() and int(value) < len(encodings):
                chosen.append(encodings[int(value)])
            elif value in cands:
                chosen.append(value)
            else:
                close = difflib.get_close_matches(value, encodings, n=3, cutoff=0.6)
                hint = ("\nClosest candidates:\n" + "\n".join(f"  {c}" for c in close)) \
                    if close else "\nSee --list-to-candidates"
                raise stage_error(f"--{name}-to: not a candidate: {value}{hint}")
        return chosen

    def sto_operands(self, name: str) -> tuple[str, ...]:
        return self.context.composition.get_sto(name).operands

    def progress(self):
        candidates = self.all_candidates()

        if self.params["list-to-candidates"].value:
            raise early_exit(self.listing(candidates))

        composition = self.context.composition
        order = [name for block in composition.get_blocks() for name in block.stos]

        given = {name: self.params[f"{name}-to"].value or [] for name in order}
        nparts = max([len(values) for values in given.values()] + [1])

        parts: list[dict[str, str]] = [dict() for _ in range(nparts)]
        for name in order:
            values = given[name]
            if values and len(values) not in (1, nparts):
                raise stage_error(f"--{name}-to has {len(values)} values for {nparts} "
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
            problems.extend(where + p for p in check_part_chain(composition, ios))
        if problems:
            raise stage_error("the chosen implementations disagree about register types:\n" +
                              "\n".join(f"  {p}" for p in problems))

        self.context.to_parts = [
            {name: chosen_to(encoding=enc, impl=candidates[name][enc])
             for name, enc in part.items()}
            for part in parts]
        for i, part in enumerate(parts):
            self.debug(f"part {i + 1}: {part}")

        self.context.to_candidates = candidates
        self.context.params.update(self.params)
        return []
