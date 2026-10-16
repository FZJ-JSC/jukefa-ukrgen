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
from asmgen.asmblocks.op import register_type as rgt

from ..components.tile import (
    tile,
    dimension_properties as dimp,
    dimension_type as dimt,
)
from ..matching.math import ast_node, for_each_operand
from .dm_solver import resolved_operation_chain
from .op import infer_hw_tile

ONE = dimp(dt=dimt.fixed, size=1, sdt=dimt.fixed, sd_size=1)


def index_extents(gen: asmgen,
                  impl: resolved_operation_chain) -> dict[str, dimp]:
    """
    How far one execution of an implementation reaches along each requirement
    index it binds to a hardware index

    :param gen: generator the implementation is for
    :param impl: implementation of a requirement
    :return: requirement index -> extent; unbound indices are left out (extent 1)
    :raises ValueError: if the operations of a chain disagree about an extent
    """
    extents: dict[str, dimp] = {}

    for res, step in zip(impl.resolved_chain, impl.math_chain):
        sig = res.compute_sg.representative

        for ref in for_each_operand(step.hw_ast, lambda x: x):
            shape = sig.operands[ref.name]
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

                known = extents.setdefault(req_idx, extent)
                if known != extent:
                    raise ValueError(f"operations disagree about the extent of {req_idx}: "
                                     f"{known} and {extent}")
    return extents


def operand_tiles(gen: asmgen,
                  impl: resolved_operation_chain,
                  req: ast_node) -> dict[str, tile]:
    """
    Tile of each requirement operand: the block one execution of the
    implementation covers, projected onto the operand's indices

    :param gen: generator the implementation is for
    :param impl: implementation of req
    :param req: the requirement
    :return: operand name -> tile, with the operand's first index along dima
    """
    extents = index_extents(gen, impl)
    tiles: dict[str, tile] = {}
    for leaf in for_each_operand(req, lambda x: x):
        dims = [extents.get(idx, ONE) if idx is not None else ONE for idx in leaf.indices]
        dims += [ONE] * (2 - len(dims))
        tiles[leaf.name] = tile(dima=dims[0], dimb=dims[1])
    return tiles
