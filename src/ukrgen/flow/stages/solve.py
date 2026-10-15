"""
Choosing how each STO is implemented in hardware ("to"s)
"""

from __future__ import annotations

import difflib
import logging
from dataclasses import dataclass

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import asm_data_type as adt

from ..stage_param import stage_param
from ..ukr_context import ukr_context
from .stage import stage, early_exit, stage_error
from .ukr.ukr import sto_description, sto_kind
from ...matching.math import transformation as tf
from ...support.data_move import (
    resolution_registry,
    tfr_key,
    dm_direction as dmd,
    filter_by_step_requirements,
    transformation_resolution,
)
from ...support.dm_resolutions.direct import direct_provider
from ...support.dm_resolutions.scalar_reduce import scalar_reduce_provider
from ...support.dm_solver import resolved_operation_chain
from ...support.encoding import encode_all


def default_registry() -> resolution_registry:
    """
    The data movement resolutions currently available
    """
    registry = resolution_registry()
    direct_provider().register_resolutions(registry)
    scalar_reduce_provider().register_resolutions(registry)
    return registry


@dataclass
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

    def encode(self) -> str:
        return f"{self.component}.{self.rtype.name}:{self.rsln.unique_tag}"


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


class solve_stage(stage):
    """
    For every STO, finds the hardware implementations available for the chosen
    ISA and data types and asks which to use (--<sto>-to). A compute STO can be
    given several, to be fused - e.g. an SME outer product next to SVE FMAs.

    --list-to-candidates prints every candidate and stops.

    Implementations depend on the data types, which is why candidates are only
    computed here and not offered as choices earlier: a data type combination
    no implementation supports is reported at this point.
    """

    def __init__(self, context : ukr_context):
        super().__init__(context)

        self.debug = logging.getLogger("SOLVE").debug

        for sto in context.composition.get_sto_descriptions():
            what = ("implementation(s); several are fused"
                    if sto_kind.COMPUTE == sto.kind else "store implementation")
            self.params[f"{sto.name}-to"] = stage_param(
                    value=None,
                    description=f"{sto.name}: {what}. A candidate string or its index "
                                f"from --list-to-candidates",
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
        impls = self.context.osb.find_hw_implementations(
                req=sto.req, registry=registry, io_dts=io_dts)
        encodings = encode_all(impls, sto.req)
        return dict(sorted(zip(encodings, impls)))

    def store_candidates(self, sto: sto_description, registry: resolution_registry,
                         producible: dict[str, set[rgt]]) -> dict[str, store_candidate]:
        """
        Ways to store each component of a store STO, for every register type an
        earlier STO could leave it in
        """
        cands: dict[str, store_candidate] = {}
        for comp in sto.store_components:
            dt = self.context.component_dts[comp]
            for rtype in sorted(producible.get(comp, set()), key=lambda r: r.name):
                seen = set()
                for tfs in (frozenset({tf.NONE}), frozenset()):
                    key = tfr_key(tfs=tfs, rtype=rtype, ddir=dmd.OUT)
                    for rsln in registry.tfr_map.get(key, []):
                        if rsln.unique_tag in seen or not self.steps_supported(rsln, dt):
                            continue
                        seen.add(rsln.unique_tag)
                        cand = store_candidate(component=comp, rtype=rtype, rsln=rsln)
                        cands[cand.encode()] = cand
        return dict(sorted(cands.items()))

    def steps_supported(self, rsln: transformation_resolution, dt: adt) -> bool:
        """
        Whether every data movement step of a resolution has an instruction
        """
        for step in rsln.steps:
            op = getattr(self.context.gen, step.op, None)
            if op is None or not filter_by_step_requirements(op.get_signatures(), step, dt):
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
                                    producible.setdefault(op, set()).add(rtype)
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
        lines = [f"{self.context.params['ukr'].value} on {self.context.params['isa'].value}: {dts}"]

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
            raise stage_error(
                f"--{name}-to is required. Candidates:\n" +
                "\n".join(f"  [{i}] {enc}" for i, enc in enumerate(cands)))

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
        chosen_rtype: dict[str, set[rgt]] = {}

        for block in composition.get_blocks():
            for name in block.stos:
                sto = composition.get_sto(name)
                cands = candidates[name]
                chosen = self.select(name, self.params[f"{name}-to"].value or [], cands)

                if sto_kind.COMPUTE == sto.kind:
                    for enc in chosen:
                        for op in sto.operands:
                            if sto.io(op)[1]:
                                rtype = produced_rtype(cands[enc], op)
                                if rtype is not None:
                                    chosen_rtype.setdefault(op, set()).add(rtype)
                else:
                    if len(chosen) != 1:
                        raise stage_error(f"--{name}-to takes exactly one candidate")
                    store = cands[chosen[0]]
                    produced = chosen_rtype.get(store.component, set())
                    if store.rtype not in produced:
                        raise stage_error(
                            f"--{name}-to stores {store.component} from "
                            f"{store.rtype.name}, but the chosen implementations leave "
                            f"it in {sorted(r.name for r in produced)}")

                self.context.to_choices[name] = chosen
                self.debug(f"{name}: {chosen}")

        self.context.to_candidates = candidates
        self.context.params.update(self.params)
        return []
