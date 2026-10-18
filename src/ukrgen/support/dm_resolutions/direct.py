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
                # contiguous in memory, the loop walking the other index
                for tag, mod in (("slices_col", omod.COL), ("slices_row", omod.ROW)):
                    registry.add_resolution(
                        key=tfr_key(tfs=frozenset(), rtype=rtype, ddir=dmd.IN),
                        rsln=tr(unique_tag=tag, steps=[
                            dm_step(op="load", dest=orig_ref(), dest_rtype=rtype,
                                    opd_mod_reqs={orig_ref(): {mod}},
                                    forbidden_op_mods=STRIDED_FORMS,
                                    repeat=dm_repeat(levels=("slice",), side="out"))]))
                    registry.add_resolution(
                        key=tfr_key(tfs=frozenset(), rtype=rtype, ddir=dmd.OUT),
                        rsln=tr(unique_tag=tag, steps=[
                            dm_step(op="store", src=[orig_ref()], src_rtypes=[rtype],
                                    opd_mod_reqs={orig_ref(): {mod}},
                                    forbidden_op_mods=STRIDED_FORMS,
                                    repeat=dm_repeat(levels=("slice",), side="in"))]))
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
