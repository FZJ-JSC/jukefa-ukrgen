"""
Resolutions for direct loads/stores
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
    dm_step,
    orig_ref,
    temp_ref,
    dm_repeat,
    resident_ref,
    dm_location as dml,
    resolution_provider
)


# Gathers, scatters and strided accesses are separate resolutions
# (strided_provider): a direct access is contiguous.
STRIDED_FORMS = {memmod.VINDEX, memmod.GSTRIDE}


class direct_provider(resolution_provider):
    """
    Provides resolutions for direct loads/stores
    """
    def register_resolutions(self, registry : resolution_registry):


        for rtype in rgt:

            # Direct load
            registry.add_resolution(
                key=tfr_key(tfs=frozenset(),
                            rtype=rtype, ddir=dmd.IN),
                rsln=tr(
                    unique_tag='direct',
                    steps=[
                        dm_step(op="load", dest=orig_ref(), dest_rtype=rtype,
                                forbidden_opd_mods={orig_ref(): {omod.BCAST,omod.GLANE,omod.ILANE,omod.ROW,omod.COL}},
                                forbidden_op_mods=STRIDED_FORMS)
                        ]))

            # Direct store
            registry.add_resolution(
                key=tfr_key(tfs=frozenset(),
                            rtype=rtype, ddir=dmd.OUT),
                rsln=tr(
                    unique_tag='direct',
                    steps=[
                        dm_step(op="store", src=[orig_ref()], src_rtypes=[rtype],
                                forbidden_opd_mods={orig_ref(): {omod.GLANE,omod.ILANE,omod.ROW,omod.COL}},
                                forbidden_op_mods=STRIDED_FORMS)
                        ]))
            
            if rgt.TILE == rtype:
                # a tile moves slice by slice (SME): a row or a column per
                # iteration, as many as the tile has at run time - its slices
                # contiguous in memory, the loop walking the other index. A
                # tile operand of an operation (a copy's) has tf.NONE
                for tag, mod in (("slices_col", omod.COL), ("slices_row", omod.ROW)):
                    for tfs_mem in (frozenset(), frozenset({tf.NONE})):
                        registry.add_resolution(
                            key=tfr_key(tfs=tfs_mem, rtype=rtype, ddir=dmd.IN),
                            rsln=tr(unique_tag=tag, steps=[
                                dm_step(op="load", dest=orig_ref(), dest_rtype=rtype,
                                        opd_mod_reqs={orig_ref(): {mod}},
                                        forbidden_op_mods=STRIDED_FORMS,
                                        repeat=dm_repeat(levels=("slice",), side="out"))]))
                        registry.add_resolution(
                            key=tfr_key(tfs=tfs_mem, rtype=rtype, ddir=dmd.OUT),
                            rsln=tr(unique_tag=tag, steps=[
                                dm_step(op="store", src=[orig_ref()], src_rtypes=[rtype],
                                        opd_mod_reqs={orig_ref(): {mod}},
                                        forbidden_op_mods=STRIDED_FORMS,
                                        repeat=dm_repeat(levels=("slice",), side="in"))]))
            if rgt.VEC == rtype:
                # a vector operation on a tile resident in registers (an
                # accumulator an outer product left): each slice moved into the
                # operation's vector and back, as many as the tile has at run
                # time - the operand stays a tile around the operation
                for tag, mod in (("slice_vec_col", omod.COL), ("slice_vec_row", omod.ROW)):
                    for tfs_reg in (frozenset(), frozenset({tf.NONE})):
                        registry.add_resolution(
                            key=tfr_key(tfs=tfs_reg, rtype=rgt.VEC, ddir=dmd.IN, loc=dml.REGISTER),
                            rsln=tr(unique_tag=tag, resident_rtype=rgt.TILE, steps=[
                                dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                                        src=[resident_ref()], src_rtypes=[rgt.TILE],
                                        opd_mod_reqs={resident_ref(): {mod}},
                                        repeat=dm_repeat(levels=("slice",), side="in"))]))
                        registry.add_resolution(
                            key=tfr_key(tfs=tfs_reg, rtype=rgt.VEC, ddir=dmd.OUT, loc=dml.REGISTER),
                            rsln=tr(unique_tag=tag, resident_rtype=rgt.TILE, steps=[
                                dm_step(op="move", dest=resident_ref(), dest_rtype=rgt.TILE,
                                        src=[orig_ref()], src_rtypes=[rgt.VEC],
                                        opd_mod_reqs={resident_ref(): {mod}},
                                        repeat=dm_repeat(levels=("slice",), side="out"))]))
            # Exactly the same, but with tf.NONE instead of an empty set

            # Direct load
            registry.add_resolution(
                key=tfr_key(tfs=frozenset({tf.NONE}),
                            rtype=rtype, ddir=dmd.IN),
                rsln=tr(
                    unique_tag='direct',
                    steps=[
                        dm_step(op="load", dest=orig_ref(), dest_rtype=rtype,
                                forbidden_opd_mods={orig_ref(): {omod.BCAST,omod.GLANE,omod.ILANE,omod.ROW,omod.COL}},
                                forbidden_op_mods=STRIDED_FORMS)
                        ]))

            # Direct store
            registry.add_resolution(
                key=tfr_key(tfs=frozenset({tf.NONE}),
                            rtype=rtype, ddir=dmd.OUT),
                rsln=tr(
                    unique_tag='direct',
                    steps=[
                        dm_step(op="store", src=[orig_ref()], src_rtypes=[rtype],
                                forbidden_opd_mods={orig_ref(): {omod.GLANE,omod.ILANE,omod.ROW,omod.COL}},
                                forbidden_op_mods=STRIDED_FORMS)
                        ]))
