"""
vlen: the machine's vector length as a value - the register a walk by whole
vectors, a loop counting blocks of them and a mask of their lanes all read
"""
from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

from ...models.lsc.ir import SECTIONS, ir_program
from ...models.lsc.operations import lsc_load, lsc_set, lsc_store, set_vl_elements
from .base import lsc_irmod, irmod_placement


def _blocks(program : ir_program) -> list:
    """Every block of the program, its cases' included"""
    return list(program.blocks) + [b for case in program.cases for b in case.blocks]


def _stepped_by_vectors(terms) -> bool:
    """
    Whether an offset's terms are, in part, a vector length
    :param terms: an offset polynomial's terms, or a record's elements' ones
    :return: whether a vector length is among its factors
    """
    return any("VL" in factor for factor in terms)


class vector_length(lsc_irmod):
    """
    The vector length in elements, once per program and element type, where
    anything steps by whole vectors: the walks (`incb`, `cntb`), a loop
    counting vector-length blocks, a mask's lanes. Its register is the
    emitter's to make - RVV's setup keeps the count (vsetvli), SVE's and
    SME's read cntd - but the value is the IR's, so that liveness, the
    renamer and the allocation see a write at the entry and reads after it
    instead of a register the emitter keeps to itself
    (docs/REGISTER_ALLOCATION.md: the state registers into the IR)
    """

    name = "vector_length"
    description = "the vector length in elements as a value where anything steps by vectors"
    placement = irmod_placement.POST_SPECIALIZE
    required = True

    @classmethod
    def triggered(cls, ctx) -> bool:
        """
        Every program: the ones needing no count name no value
        :param ctx: the context after specialization
        :return: True, always
        """
        return True

    def apply(self, program : ir_program) -> int:
        """
        Insert the value's set in the program's entry for each element type a
        vector-length step is taken at
        :param program: the IR, after specialization (builds beside the state)
        :return: the operations added
        """
        dts = set()
        for block in _blocks(program):
            vector = _stepped_by_vectors(dict(block.step.terms))
            for section in SECTIONS:
                for op in getattr(block, section) or []:
                    if not isinstance(op, (lsc_load, lsc_store)) or op.offset is None:
                        continue
                    records = program.offsets.records
                    record = records[op.offset] if 0 <= op.offset < len(records) else None
                    stepped = record is not None and any(
                        _stepped_by_vectors(dict(e.terms)) for _, e in record.elements)
                    if not (vector or stepped):
                        continue
                    comp = op.indices[1].component
                    if comp in self.ctx.component_dts:
                        dts.add(self.ctx.component_dts[comp])
        sets = [lsc_set(f"VL in {adt_size(dt)}-byte elements", 0, rgt.GP, set_vl_elements(dt))
                for dt in sorted(dts, key=adt_size)]
        for s in sets:
            s.decision = None
        program.entry = list(program.entry) + sets
        return len(sets)
