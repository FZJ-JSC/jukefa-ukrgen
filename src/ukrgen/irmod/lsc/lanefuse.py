"""
lanefuse: loads into all lanes of a register fused into one load
"""

from __future__ import annotations

from asmgen.asmblocks.op import register_type as rgt
from asmgen.registers import adt_size

from ...models.load_store_operations import lsc_load, ldst_modifier
from ...models.lsc.index import lsc_reg_index
from ...lsc_model.addressing import sym
from ...support.data_move import dm_step, orig_ref, filter_by_step_requirements
from ...support.sig_group import group_sigs
from .base import lsc_irmod, irmod_placement, blocks_and_sections


class lanefuse(lsc_irmod):
    """
    An operation using one element of a register at a time (an FMA by element)
    gets its elements loaded lane by lane, which works for any layout. Where a
    register's lanes allow it, one plain load at the first of the lane loads
    does the same. Strided lanes stay as they are until strided and indexed
    loads are specialized.

    Runs on the model's IR, before specialization gives each lane load an
    address of its own.
    """

    name = "lanefuse"
    description = "fuse loads into all lanes of a register into one load"
    placement = irmod_placement.PRE_SPECIALIZE
    constraints = ("every lane of the register loaded, with no write to it in between, "
                   "through one address register, from contiguous memory: lane l at "
                   "lane 0's offset plus l")

    @classmethod
    def unmet_requirements(cls, ctx) -> list[str]:
        return ["fixed-width vectors"] if ctx.gen.is_vla else []

    def plain_load(self, comp):
        step = dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC)
        sigs = filter_by_step_requirements(self.ctx.gen.load.get_signatures(), step,
                                           self.ctx.component_dts[comp])
        return step, (group_sigs(sigs) if sigs else None)

    def check(self, program, lanes: dict[int, object]) -> bool:
        """
        Whether a set of lane loads into one register, by lane, can be one load
        """
        first = lanes[0]
        comp = first.indices[0].component
        count = self.ctx.gen.simd_size // adt_size(self.ctx.component_dts[comp])
        if set(lanes) != set(range(count)):
            return False
        db, strides = program.offsets, program.strides.get(comp, {})
        base = db.elements_offset(first.offset, strides)
        return all(op.indices[0].indices == first.indices[0].indices
                   and db.elements_offset(op.offset, strides) - base == sym.const(lane)
                   for lane, op in lanes.items())

    def fuse(self, program, ops: list) -> tuple[list, int]:
        runs: dict[tuple, dict[int, int]] = {}
        replace, drop = {}, set()
        for pos, op in enumerate(ops):
            if isinstance(op, lsc_load) and ldst_modifier.lane in op.mods:
                key = (op.indices[1].component, op.indices[1].indices[0])
                lane = op.properties.get("lane")
                run = runs.get(key)
                if run is None or lane in run:
                    run = runs[key] = {}
                run[lane] = pos
                comp = op.indices[0].component
                count = self.ctx.gen.simd_size // adt_size(self.ctx.component_dts[comp])
                if len(run) < count:
                    continue
                runs.pop(key)
                step, sigs = self.plain_load(comp)
                if sigs and self.check(program, {l: ops[p] for l, p in run.items()}):
                    first = ops[run[0]]
                    at = min(run.values())
                    replace[at] = lsc_load(
                        comp, key[1], first.indices[0].indices[0], None, None,
                        first.tiles[1], set(), data=lsc_reg_index(key[0], [key[1]]),
                        rsln=first.rsln, step=step, sigs=sigs, offset=first.offset,
                        rtypes=first.rtypes)
                    drop |= {p for p in run.values() if p != at}
                continue
            # anything else writing a register ends its run
            for p in op.writes:
                idx = op.indices[p]
                runs.pop((idx.component, idx.indices[0]), None)
        return [replace.get(i, op) for i, op in enumerate(ops) if i not in drop], len(replace)

    def apply(self, program) -> int:
        total = 0
        for block, section in blocks_and_sections(program):
            ops, fused = self.fuse(program, getattr(block, section))
            setattr(block, section, ops)
            total += fused
        return total
