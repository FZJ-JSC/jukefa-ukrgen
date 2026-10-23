# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING

from asmgen.asmblocks.noarch import asmgen
from asmgen.registers import asm_data_type as adt

from .stage_param import stage_param

if TYPE_CHECKING:
    # TODO: Fix/rewrite model/specializer/generator
    #       For now the TYPE_CHECKING enables import from already-reworked stages
    from asmgen.registers import reg_tracker
    from ..models.load_store_cpu import load_store_cpu
    from ..models.load_store_operations import lsc_operation
    from ..models.offset_mapper import offset_mapper
    from ..specializers.asm import lsc_specializer, op_support
    from ..generators.mm import mm_op
    from ..support.op import op_support_builder
    from .stages.ukr.ukr import ukr_composition
    from .stages.solve import chosen_to
    from .stages.sto import sto_tiling

class ukr_context:
    """
    Contains data, parameters and structures involved in the generation
    of a compute kernel as well as it's state through the different 
    flow stages
    """
    def __init__(self):
        self.gen             : asmgen = None
        self.composition     : type[ukr_composition] = None
        self.osb             : op_support_builder = None
        # one dict per part of the microtile: STO name -> chosen implementation
        self.to_parts        : list[dict[str,chosen_to]] = list()
        # memory component -> index it is contiguous along (None: neither)
        self.component_layouts : dict[str,str|None] = dict()
        # memory component -> index -> "c" (contiguous), "p" (packed) or "s" (strided)
        self.component_strides : dict[str,dict[str,str]] = dict()
        # memory component -> its contiguous and packed indices, innermost first
        self.component_packing : dict[str,list[str]] = dict()
        self.to_candidates   : dict[str,dict] = dict()
        self.rt              : reg_tracker = None
        self.params          : dict[str,stage_param] = dict()

        self.model           : load_store_cpu = None
        self.specializer     : lsc_specializer = None
        self.op_support_list : list[op_support] = list()
        self.component_dts   : dict[str,adt] = dict()
        self.sup             : op_support = None
        self.mappers         : dict[str,offset_mapper] = dict()
        self.strides         : dict[str,tuple[int|None,int|None]] = dict()
        self.mru_map         : dict[str,tuple[list[str],list[str]]] = dict()
        self.sched_map       : dict[str,tuple[list[str],bool]] = dict()
        self.specialization_order : list[str] = list()

        # one dict per part of the microtile: STO name -> its tiling
        self.stos            : list[dict[str,sto_tiling]] = list()
        self.dims            : dict[str,int] = dict()
        # one LSC IR program per part, and its emitted assembly
        self.programs        : list = list()
        self.emitted         : list = list()
        # per part: loop STO -> implementation for the loop's remainder below
        # one operation, and its tiling
        self.subtail_parts   : list[dict] = list()
        self.subtail_stos    : list[dict] = list()
        self.order           : tuple[str,...] = tuple()
        self.irs             : dict[str,list[lsc_operation]] = dict()
        self.asmblocks       : dict[str,str] = dict()
        #: hooks run around stages (flow.hooks), parsed by the setup stage
        self.hooks           : list = list()

