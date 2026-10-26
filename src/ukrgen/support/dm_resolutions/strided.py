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
    temp_ref,
    dm_repeat,
    orig_ref,
    resolution_provider,
)



def block_lane_loads(chain: tuple, no_gather) -> list:
    """
    A vector filled block by block, at block sizes chain (bits, outermost
    first): each innermost block's lanes loaded into a scratch, which is
    inserted into the next level's scratch - or, outermost, the vector - as a
    block of its size
    """
    regs = [temp_ref(tag=str(i)) for i in range(len(chain))] + [orig_ref()]
    steps = [dm_step(op="load", dest=regs[0], dest_rtype=rgt.VEC,
                     opd_mod_reqs={regs[0]: {omod.ILANE, omod.ZEROOTHERS}},
                     forbidden_op_mods=no_gather,
                     repeat=dm_repeat(levels=chain + ("lane",), side="out"))]
    for i in range(len(chain)):
        steps.append(dm_step(op="move", dest=regs[i + 1], dest_rtype=rgt.VEC,
                             src=[regs[i]], src_rtypes=[rgt.VEC],
                             opd_mod_reqs={regs[i + 1]: {omod.IBLOCK}},
                             repeat=dm_repeat(levels=chain[:len(chain) - i], side="out")))
    return steps

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
                     repeat=dm_repeat(levels=("lane",), side="out"))]))
            registry.add_resolution(key_out, tr(unique_tag="lanes", steps=[
                store(opd_mod_reqs={orig_ref(): {omod.ILANE}}, forbidden_op_mods=no_gather,
                      repeat=dm_repeat(levels=("lane",), side="in"))]))

            # Where lane loads reach only the low 128-bit block and don't keep
            # the lanes above (AVX: ZEROOTHERS), the vector is filled block by
            # block: a block's lanes into a scratch register in increasing
            # order, then the scratch inserted as the block
            # block_lanes: 128-bit blocks inserted into the vector;
            # block_lanes_256 (AVX-512): 128-bit blocks into a 256-bit
            # scratch, then 256-bit inserts - two on the destination
            # instead of four, the halves built independently. The same
            # resolution, one level more
            registry.add_resolution(key_in, tr(unique_tag="block_lanes",
                                               steps=block_lane_loads((128,), no_gather)))
            registry.add_resolution(key_in, tr(unique_tag="block_lanes_256",
                                               steps=block_lane_loads((256, 128), no_gather)))
            # a loop over the vector's elements where their number is
            # known at run time only: each loaded into a scalar, filled
            # into the vector shifting it in place (RVV vfslide1down)
            scalar = temp_ref(tag="0")
            registry.add_resolution(key_in, tr(unique_tag="vla_lanes", steps=[
                dm_step(op="load", dest=scalar, dest_rtype=rgt.FP,
                        repeat=dm_repeat(levels=("element",))),
                dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                        src=[scalar], src_rtypes=[rgt.FP],
                        opd_mod_reqs={orig_ref(): {omod.ILANESHIFT, omod.FILLOTHERS}},
                        repeat=dm_repeat(levels=("element",)))]))
            # and draining one: lane 0 into a scalar, stored; the loop
            # shifts the vector down after (RVV vfmv.f.s, vslidedown)
            registry.add_resolution(key_out, tr(unique_tag="vla_lanes", steps=[
                dm_step(op="move", dest=scalar, dest_rtype=rgt.FP,
                        src=[orig_ref()], src_rtypes=[rgt.VEC],
                        opd_mod_reqs={orig_ref(): {omod.ILANE}},
                        repeat=dm_repeat(levels=("element",))),
                dm_step(op="store", src=[scalar], src_rtypes=[rgt.FP],
                        repeat=dm_repeat(levels=("element",)))]))
            # stores: each block extracted into a scratch, its lanes stored
            scratch = temp_ref(tag="0")
            registry.add_resolution(key_out, tr(unique_tag="block_lanes", steps=[
                dm_step(op="move", dest=scratch, dest_rtype=rgt.VEC,
                        src=[orig_ref()], src_rtypes=[rgt.VEC],
                        opd_mod_reqs={orig_ref(): {omod.IBLOCK}},
                        repeat=dm_repeat(levels=(128,), side="in")),
                dm_step(op="store", src=[scratch], src_rtypes=[rgt.VEC],
                        opd_mod_reqs={scratch: {omod.ILANE}},
                        forbidden_op_mods=no_gather,
                        repeat=dm_repeat(levels=(128, "lane"), side="in"))]))
