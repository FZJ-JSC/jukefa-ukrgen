from dataclasses import replace
"""
Resolutions for SCALAR_REDUCE transformation

A scalar-reduced operand is one element of its requirement's - whatever the
transformation is applied to - so the key these are registered under carries
the operand's *floating-point* register type, not VEC: the type a
scalar-reduced operand is left with (dm_solver's deduce_operand_rtype, which
reads the transformed AST). What the operation then does with the element is
what these resolutions differ in: take it in a floating-point register
(use_scalar, a vector-scalar instruction's form; scalar_direct, a scalar
instruction's), build a vector from it (bc_scalar, bc_load, bc_lane,
bc_lanes, bc_block, scalar_to_lane) or take it out of one for a store
(use_lane, lane_to_scalar).
"""


from asmgen.asmblocks.op import (
    register_type as rgt,
    operand_modifier as omod,
)

from ...matching.math import transformation as tf

from ..data_move import (
    dm_repeat,
    resolution_registry,
    tfr_key,
    transformation_resolution as tr,
    dm_direction as dmd,
    dm_location as dml,
    dm_step,
    orig_ref,
    temp_ref,
    resolution_provider
)


class scalar_reduce_provider(resolution_provider):
    """
    Provides resolutions for a SCALAR_REDUCE operand: one element, in whichever
    register type the instruction that consumes it takes
    """
    def register_resolutions(self, registry : resolution_registry):
        before = {key: set(registry.tfr_tags.get(key, set())) for key in registry.tfr_map}
        self._register(registry)

        # Moving one element serves any memory layout, so these resolutions
        # also apply where the operand's vectors would be strided. The
        # exceptions load a whole vector to take lanes from it, which needs
        # consecutive elements along a contiguous index.
        for key, rslns in list(registry.tfr_map.items()):
            if tf.SCALAR_REDUCE not in key.tfs or dml.MEMORY != key.loc:
                continue
            for rsln in rslns:
                if rsln.unique_tag in before.get(key, set()):
                    continue
                if dmd.IN == key.ddir and rsln.unique_tag in self.WHOLE_VECTOR_IN:
                    continue
                registry.add_resolution(key=replace(key, loc=dml.STRIDED_MEMORY), rsln=rsln)

    # use_lane loads one lane per element, so it works for any layout; a full
    # set of lanes is fused into one load by an irmod where they are contiguous
    WHOLE_VECTOR_IN = frozenset({"bc_lane", "bc_block"})

    #: What a plain register operand is not. A scalar instruction takes the
    #: register itself, so any form that names part of one - a lane or a block
    #: of it, a broadcast into it, a tile's row or column, a vector-scalar
    #: form - is another resolution's business: VF's is use_scalar, a lane's is
    #: use_lane or bc_*, a slice's the tile ones. Requiring nothing of the
    #: modifiers instead let scalar_direct match RVV's vf forms, whose scalar
    #: operand is an FP register with VF on its shape: 228 candidates on RVV's
    #: gemm that say "a vector instruction" and no scalar instruction at all.
    NOT_A_PLAIN_REGISTER = frozenset({
        omod.VF, omod.BCAST,
        omod.ILANE, omod.GLANE, omod.BLOCKLANE, omod.BLOCK, omod.IBLOCK,
        omod.ILANESHIFT, omod.ILANEROT, omod.IBLOCKSHIFT, omod.IBLOCKROT,
        omod.ROW, omod.COL,
    })

    def _register(self, registry : resolution_registry):

        # example RVV:
        #  fld f0, (t0)
        #  vfmacc.vf v0, f0, v1
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.FP, ddir=dmd.IN),
            rsln=tr(
                unique_tag='use_scalar',
                opd_mod_reqs={omod.VF},
                steps=[
                    dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.FP)
                    ]))

        # example riscv64 (a scalar FMA, no vector operand anywhere):
        #  fld f0, (t0)
        #  fmadd.d f2,f0,f1,f2
        # The same move as use_scalar's without the VF modifier: use_scalar
        # says "this operation's other operands are vectors, this one is the
        # scalar it takes", this one says "the operation is scalar". So it is
        # registered under the operand's floating-point type - the one its
        # transformation leaves it with, dm_solver's deduce_operand_rtype - and
        # not under VEC, where the resolutions above are.
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.FP, ddir=dmd.IN),
            rsln=tr(
                unique_tag='scalar_direct',
                forbidden_opd_mods=self.NOT_A_PLAIN_REGISTER,
                steps=[
                    dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.FP)
                    ]))

        # example SVE:
        #  fld d0, [x5]
        #  dup z1.d, z0.d[0]
        #  fmla z2.d, p0/m, z3.d, z1.d
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='bc_scalar',
                steps=[
                   dm_step(op="load", dest=temp_ref(tag="0"), dest_rtype=rgt.FP),
                   dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                           src=[temp_ref(tag="0")],src_rtypes=[rgt.FP],
                           opd_mod_reqs={orig_ref(): {omod.BCAST}})
                   ]))

        # example SVE:
        #  ld1rd z0.d, p0/m, [x5]
        #  fmla z2.d, p0/m, z3.d, z1.d
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='bc_load',
                steps=[
                    dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC,
                            opd_mod_reqs={orig_ref(): {omod.BCAST}})
                    ]))

        # example NEON:
        #  ld1 v0.d[1], [x5]
        #  dup v1.2d, v0.d[1]
        #  fmla v2.2d, v3.2d, v1.2d
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='bc_lane',
                steps=[
                    dm_step(op="load", dest=temp_ref(tag="0"), dest_rtype=rgt.VEC,
                            opd_mod_reqs={temp_ref(tag="0") : {omod.ILANE}}),
                    dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                            src=[temp_ref(tag="0")],src_rtypes=[rgt.VEC],
                            opd_mod_reqs={
                                temp_ref(tag="0") : {omod.ILANE},
                                orig_ref(): {omod.BCAST}
                                })
                    ]))

        # example NEON, a vector of elements, a broadcast per lane:
        #  ld1 {v0.2d}, [x5]
        #  dup v1.2d, v0.d[0]
        #  dup v2.2d, v0.d[1]
        #  fmla v3.2d, v4.2d, v1.2d
        #  fmla v5.2d, v4.2d, v2.2d
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='bc_lanes',
                steps=[
                    dm_step(op="load", dest=temp_ref(tag="0"), dest_rtype=rgt.VEC,
                            forbidden_opd_mods={temp_ref(tag="0"): {omod.ILANE, omod.BCAST}}),
                    dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                            src=[temp_ref(tag="0")], src_rtypes=[rgt.VEC],
                            opd_mod_reqs={
                                temp_ref(tag="0") : {omod.ILANE},
                                orig_ref(): {omod.BCAST}
                                },
                            repeat=dm_repeat(levels=("lane",), side="in", group=True))
                    ]))

        # example SVE, an FMA using one element of each 128-bit block:
        # ld1rqd {z1.d}, p0/z, [x5]          (b0 b1 | b0 b1 | ...)
        # fmla z2.d, z3.d, z1.d[0]
        # fmla z4.d, z3.d, z1.d[1]
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='bc_block',
                opd_mod_reqs={omod.BLOCKLANE},
                steps=[
                    dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC,
                            opd_mod_reqs={orig_ref() : {omod.BLOCK, omod.BCAST}}),
                    ]))

        # example NEON:
        # ld1 {v1.d}[0], [x5]
        # ld1 {v1.d}[1], [x6]
        # fmla v2.2d, v3.2d, v1.d[0]
        # fmla v4.2d, v3.2d, v1.d[1]
        # (the lanefuse irmod makes the two loads one where they are contiguous)
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='use_lane',
                opd_mod_reqs={omod.ILANE},
                # each element is loaded into the lane the operation uses it
                # from: any layout works
                steps=[
                    dm_step(op="load", dest=orig_ref(), dest_rtype=rgt.VEC,
                            opd_mod_reqs={orig_ref() : {omod.ILANE}}),
                    ]))

        # example neon:
        # ldr d0, [x5]
        # fmov v1.d[1], d0
        # fmla v2.2d, v3.2d, v1.d[1]
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.IN),
            rsln=tr(
                unique_tag='scalar_to_lane',
                opd_mod_reqs={omod.ILANE},
                steps=[
                   dm_step(op="load", dest=temp_ref(tag="0"), dest_rtype=rgt.FP),
                   dm_step(op="move", dest=orig_ref(), dest_rtype=rgt.VEC,
                           src=[temp_ref(tag="0")],src_rtypes=[rgt.FP],
                           opd_mod_reqs={orig_ref(): {omod.ILANE}})
                   ]))

        # STORE:


        # if the output is a scalar we can just store a scalar?
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.FP, ddir=dmd.OUT),
            rsln = tr(
                unique_tag='use_scalar',
                opd_mod_reqs={omod.VF},
                steps=[
                    dm_step(op="store", src=[orig_ref()], src_rtypes=[rgt.FP]),
                    ]))

        # example riscv64 (a scalar operation): the artifact is in a
        # floating-point register already
        #  fsd f2, (t0)
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.FP, ddir=dmd.OUT),
            rsln=tr(
                unique_tag='scalar_direct',
                forbidden_opd_mods=self.NOT_A_PLAIN_REGISTER,
                steps=[
                    dm_step(op="store", src=[orig_ref()], src_rtypes=[rgt.FP])
                    ]))


        # example NEON:
        # st1 v0.d[1], [x5]
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.OUT),
            rsln = tr(
                unique_tag='use_lane',
                # We can probably weaken the requirement without breaking correctness,
                # Allowing for weird stuff like fma(bcast:a, bcast:b, bcast:c) -> store_lane:c
                #opd_mod_reqs={omod.ILANE},
                steps=[
                    dm_step(op="store", src=[orig_ref()], src_rtypes=[rgt.VEC],
                            opd_mod_reqs={orig_ref() : {omod.ILANE}}),
                    ]))


        # example NEON:
        # fmov d1, v0.d[1]
        # str d1, [x5]
        registry.add_resolution(
            key=tfr_key(tfs=frozenset({tf.SCALAR_REDUCE}),
                        rtype=rgt.VEC, ddir=dmd.OUT),
            rsln = tr(
                unique_tag='lane_to_scalar',
                #opd_mod_reqs={omod.ILANE},
                steps=[dm_step(op="move", dest=temp_ref(tag='0'), dest_rtype=rgt.FP,
                               src=[orig_ref()], src_rtypes=[rgt.VEC],
                               opd_mod_reqs={orig_ref(): {omod.ILANE}}),
                       dm_step(op="store", src=[temp_ref(tag='0')], src_rtypes=[rgt.FP])]))
