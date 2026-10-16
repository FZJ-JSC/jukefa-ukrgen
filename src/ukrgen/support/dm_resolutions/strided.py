"""
Resolutions for vectors whose lanes are apart in memory
"""

from asmgen.asmblocks.op import (
    register_type as rgt,
    operand_modifier as omod,
    opmem_modifier as memmod,
)

from ...matching.math import transformation as tf
from ..data_move import (
    resolution_registry,
    tfr_key,
    transformation_resolution as tr,
    dm_direction as dmd,
    dm_location as dml,
    dm_step,
    dm_repeat,
    orig_ref,
    resolution_provider,
)


class strided_provider(resolution_provider):
    """
    A vector running along an index the operand is not contiguous along:

    strided:        one strided load or store (RVV vlse/vsse)
    gather/scatter: one indexed load or store, the address model supplying the
                    index vector (SVE scalar+vector, AVX gathers, RVV indexed)
    lanes:          one load or store per lane (NEON ld1/st1 to a lane); only
                    where the lane immediate covers every lane of the vector

    Loading lanes into a narrower register and inserting it (AVX's 128-bit
    lanes) needs move instructions, still being added to asmgen.
    """

    def register_resolutions(self, registry : resolution_registry):
        for tfs in (frozenset({tf.NONE}), frozenset()):
            key_in = tfr_key(tfs=tfs, rtype=rgt.VEC, ddir=dmd.IN, loc=dml.STRIDED_MEMORY)
            key_out = tfr_key(tfs=tfs, rtype=rgt.VEC, ddir=dmd.OUT, loc=dml.STRIDED_MEMORY)

            def load(**kw):
                return dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC, **kw)

            def store(**kw):
                return dm_step(op="store", src=[orig_ref()], src_rtypes=[rgt.VEC], **kw)

            no_lanes_in = {orig_ref(): {omod.BCAST, omod.GLANE, omod.ILANE}}
            no_lanes_out = {orig_ref(): {omod.GLANE, omod.ILANE}}

            registry.add_resolution(key_in, tr(unique_tag="strided", steps=[
                load(op_mod_reqs={memmod.GSTRIDE}, forbidden_opd_mods=no_lanes_in)]))
            registry.add_resolution(key_out, tr(unique_tag="strided", steps=[
                store(op_mod_reqs={memmod.GSTRIDE}, forbidden_opd_mods=no_lanes_out)]))

            registry.add_resolution(key_in, tr(unique_tag="gather", steps=[
                load(op_mod_reqs={memmod.VINDEX}, forbidden_opd_mods=no_lanes_in)]))
            registry.add_resolution(key_out, tr(unique_tag="scatter", steps=[
                store(op_mod_reqs={memmod.VINDEX}, forbidden_opd_mods=no_lanes_out)]))

            no_gather = {memmod.VINDEX, memmod.GSTRIDE, memmod.STRUCT}
            registry.add_resolution(key_in, tr(unique_tag="lanes", steps=[
                load(opd_mod_reqs={orig_ref(): {omod.ILANE}}, forbidden_op_mods=no_gather,
                     repeat=dm_repeat(lane_operand="adreg_lane"))]))
            registry.add_resolution(key_out, tr(unique_tag="lanes", steps=[
                store(opd_mod_reqs={orig_ref(): {omod.ILANE}}, forbidden_op_mods=no_gather,
                      repeat=dm_repeat(lane_operand="adreg_lane"))]))
