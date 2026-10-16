"""
Operands whose value is already in, or stays in, a register
"""

from asmgen.asmblocks.op import register_type as rgt

from ..data_move import (
    resolution_registry,
    transformation_resolution,
    tfr_key,
    dm_direction as dmd,
    dm_location as dml,
)
from ...matching.math import transformation as tf


class resident_provider:
    """
    Registers the resolution of an operand that needs no data movement: an
    accumulator kept in registers across a loop, a value an earlier STO left in
    registers, a temporary passed between the operations of a chain. It has no
    steps; the operation reads or writes the register directly, in the register
    type the operation uses.
    """

    TAG = "resident"

    def register_resolutions(self, registry: resolution_registry):
        for rtype in (rgt.VEC, rgt.TILE, rgt.FP, rgt.GP, rgt.MASK):
            for ddir in (dmd.IN, dmd.OUT):
                for tfs in (frozenset({tf.NONE}), frozenset()):
                    registry.add_resolution(
                        tfr_key(tfs=tfs, rtype=rtype, ddir=ddir, loc=dml.REGISTER),
                        transformation_resolution(unique_tag=self.TAG, steps=[]))
