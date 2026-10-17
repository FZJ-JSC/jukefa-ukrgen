"""
Tiles of requirement operands, inferred from the chosen implementation.

One execution of an implementation covers a block of the requirement's
iteration space: along an index bound to a hardware index (i -> m), as far as
that hardware index reaches - a vector's worth of elements, a tile's rows -
and along every other index a single element. An operand's tile is that block
projected onto the operand's own indices. This replaces the hand-written
per-operand tiles of the op_support structure and the vecdir that oriented
them: the orientation is the index binding.
"""

from __future__ import annotations

from asmgen.asmblocks.noarch import asmgen
from asmgen.asmblocks.op import register_type as rgt, operand_modifier as omod
from asmgen.registers import adt_size

from ..components.tile import (
    tile,
    dimension_properties as dimp,
    dimension_type as dimt,
)
from ..matching.math import ast_node, for_each_operand, transformation as tf
from .dm_solver import resolved_operation_chain
from .data_move import dm_direction as dmd
from .op import infer_hw_tile

ONE = dimp(dt=dimt.fixed, size=1, sdt=dimt.fixed, sd_size=1)


def widening_ways(sig) -> int:
    """
    How many registers a widening signature's wide operands take per register
    of its narrow ones (1 where it doesn't widen): its widening_method says so
    """
    method = sig.structural_params.get("widening_method")
    if method is None or "NONE" == method.name:
        return 1
    sizes = [adt_size(o.dt) for o in sig.operands.values()
             if getattr(o, "dt", None) is not None and o.rtype in (rgt.VEC, rgt.TILE)]
    return max(sizes) // min(sizes) if sizes else 1


def kernel_groups(impls) -> dict[int, int]:
    """
    Where a kernel widens, every vector register of the wide type is a group -
    in every chain, the plain ones on the same registers (gemm's alpha and
    beta, C) alike: wide element size -> registers per group
    """
    groups: dict[int, int] = {}
    for impl in impls:
        for res in impl.resolved_chain:
            sig = res.compute_sg.representative
            if widening_ways(sig) < 2:
                continue
            sizes = [adt_size(o.dt) for o in sig.operands.values()
                     if rgt.VEC == o.rtype and getattr(o, "dt", None) is not None]
            for size in sizes:
                if size > min(sizes):
                    groups[size] = size // min(sizes)
    return groups


def index_extents(gen: asmgen,
                  impl: resolved_operation_chain,
                  groups: dict[int, int] | None = None) -> dict[str, dimp]:
    """
    How far one execution of an implementation reaches along each requirement
    index it binds to a hardware index

    :param gen: generator the implementation is for
    :param impl: implementation of a requirement
    :return: requirement index -> extent; unbound indices are left out (extent 1)
    :raises ValueError: if the operations of a chain disagree about an extent
    """
    extents: dict[str, dimp] = {}

    # where the kernel widens, its wide registers are groups (the chain's own
    # widening, if the caller doesn't know the kernel's)
    groups = kernel_groups([impl]) if groups is None else groups
    for res, step in zip(impl.resolved_chain, impl.math_chain):
        sig = res.compute_sg.representative

        for ref in for_each_operand(step.hw_ast, lambda x: x):
            shape = sig.operands[ref.name]
            # a scalar-reduced operand is one element wherever its index sits
            # (RVV's vfmacc.vf takes it in an FP register): it says nothing
            # about how far the operation reaches
            if tf.SCALAR_REDUCE in step.transformations.get(ref.name, set()) or \
                    shape.rtype not in (rgt.VEC, rgt.TILE):
                continue
            physical = infer_hw_tile(gen, shape, shape.dt)
            live = [(axis, idx) for axis, idx in enumerate(ref.indices) if idx is not None]

            for axis, hw_idx in live:
                req_idx = step.index_mapping.get(hw_idx)
                if req_idx is None:
                    continue
                # a vector has one dimension wherever its index sits in the
                # AST; a tile's axes are its rows and columns
                if rgt.TILE == shape.rtype:
                    extent = physical.dima if 0 == axis else physical.dimb
                else:
                    extent = physical.dima

                if rgt.VEC == shape.rtype and adt_size(shape.dt) in groups \
                        and dimt.fixed == extent.dt:
                    # a widening chain: its wide registers are groups, as many
                    # as a narrow register's elements take. Fixed-width extents
                    # count elements; vector-length agnostic ones count vectors
                    # of each operand's own type, where a group of wide vectors
                    # already is one narrow vector
                    factor = groups[adt_size(shape.dt)]
                    extent = dimp(dt=extent.dt, size=extent.size * factor,
                                  sdt=extent.sdt, sd_size=extent.sd_size * factor)
                known = extents.setdefault(req_idx, extent)
                if known != extent:
                    raise ValueError(f"operations disagree about the extent of {req_idx}: "
                                     f"{known} and {extent}")
    return extents


def operand_tiles(gen: asmgen,
                  impl: resolved_operation_chain,
                  req: ast_node,
                  groups: dict[int, int] | None = None) -> dict[str, tile]:
    """
    Tile of each requirement operand: the block one execution of the
    implementation covers, projected onto the operand's indices

    :param gen: generator the implementation is for
    :param impl: implementation of req
    :param req: the requirement
    :return: operand name -> tile, with the operand's first index along dima
    """
    extents = index_extents(gen, impl, groups)
    tiles: dict[str, tile] = {}
    for leaf in for_each_operand(req, lambda x: x):
        dims = [extents.get(idx, ONE) if idx is not None else ONE for idx in leaf.indices]
        dims += [ONE] * (2 - len(dims))
        tiles[leaf.name] = tile(dima=dims[0], dimb=dims[1])
    return tiles


def lane_axes(gen: asmgen,
              impl: resolved_operation_chain,
              req: ast_node,
              layouts: dict[str, str | None] | None = None) -> dict[str, tuple[str, int]]:
    """
    Operands an implementation uses one element at a time out of a register
    holding several: an FMA by element (NEON fmla v0.2d, v1.2d, v2.d[1]) on
    elements of B loaded lane by lane (use_lane) - one load where the lanes are
    contiguous, after the lanefuse irmod. Consecutive elements along the
    operand's index share a register, one per lane.

    The lanes run along the index the operand was loaded along - the one it is
    contiguous along in memory, or its last index if the layout is unknown.
    On SVE an FMA by element picks the element per 128-bit block: its
    operand is loaded one block replicated into every block (bc_block, ld1rq),
    a lane per element of the block.

    :return: operand -> (index the lanes run along, lanes per register)
    """
    layouts = layouts or {}
    leaves = {leaf.name: [i for i in leaf.indices if i is not None]
              for leaf in for_each_operand(req, lambda x: x)}
    found: dict[str, tuple[str, int]] = {}
    for res, step in zip(impl.resolved_chain, impl.math_chain):
        sig = res.compute_sg.representative
        for hw_name, math_name in step.name_mapping.items():
            shape = sig.operands.get(hw_name)
            strat = res.operand_strategies.get((hw_name, dmd.IN))
            if shape is None or strat is None or not leaves.get(math_name):
                continue
            tag = strat.rsln.unique_tag
            if "use_lane" == tag and omod.ILANE in shape.modifiers and not gen.is_vla:
                count = gen.simd_size // adt_size(shape.dt)
            elif "bc_block" == tag and omod.BLOCKLANE in shape.modifiers:
                # one lane per element of a block, every block alike
                count = sig.structural_params.get(f"{hw_name}_blocksize")
                if not count:
                    continue
            else:
                continue
            axis = layouts.get(math_name)
            if axis not in leaves[math_name]:
                axis = leaves[math_name][-1]
            found[math_name] = (axis, count)
    return found


def register_tiles(tiles: dict[str, tile], lanes: dict[str, tuple[str, int]],
                   req: ast_node) -> dict[str, tile]:
    """
    Register tiles: the operand tiles, widened along the lane axis for operands
    used one element at a time
    """
    indices = {leaf.name: leaf.indices for leaf in for_each_operand(req, lambda x: x)}
    regs = dict(tiles)
    for name, (axis, count) in lanes.items():
        dims = [tiles[name].dima, tiles[name].dimb]
        dims[list(indices[name]).index(axis)] = dimp(dt=dimt.fixed, size=count,
                                                     sdt=dimt.fixed, sd_size=count)
        regs[name] = tile(dima=dims[0], dimb=dims[1])
    return regs
