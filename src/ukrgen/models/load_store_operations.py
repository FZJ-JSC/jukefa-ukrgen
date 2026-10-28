# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

from dataclasses import dataclass
import string
from typing import Callable
from enum import Enum,auto
from ..components.tile import tile,scalar_tile
from ..components.operation import dimension_type

from .lsc.offset import lsc_offset
from .lsc.index import lsc_reg_index 
from .lsc.reg import lsc_reg_type


# TODO: fractional offsets
class fraction:
    def __init__(self, nom : int, div : int = 1):
        self.nom = nom
        self.div = div

class lsc_operation:
    #: what some operations carry, set where they do - the others have these
    resolution = None           # a transformation's data movement
    block = None                # a loop's block
    sigs = None                 # the signatures a load, store or move may take
    increment = None            # an address register's advance after the access
    mods : tuple = ()           # a load's, store's or transformation's modifiers
    rtypes = None               # its operands' register types
    walk_plan = None            # how a loop walks its components

    def __init__(self,
                 tiles : list[tile],
                 indices: list[lsc_reg_index],
                 reads: list[int],
                 writes: list[int],
                 reg_types : list[lsc_reg_type]):
        for t in tiles:
            if not isinstance(t, tile):
                raise ValueError("non-tile in list of tiles")
        self.tiles = tiles
        for idx in indices:
            if not isinstance(idx,lsc_reg_index):
               raise ValueError(f"invalid index: {idx}")
        self.indices = indices
        self.reads = reads
        self.writes = writes
        #: processor state read and written beyond the signatures' (an
        #: operation setting it, lsc_state, its own)
        self.extra_reads_state: set[str] = set()
        self.extra_writes_state: set[str] = set()
        self._state_memo = None
        self.reg_types = reg_types

        self.properties : dict[str,int|str] = dict()

    def state_sigs(self) -> list:
        """the signatures whose processor state the operation has - none here"""
        return []

    @property
    def reads_state(self) -> frozenset:
        """the processor state the operation reads (asmgen's signatures say)"""
        return _state_of(self)[0]

    @property
    def writes_state(self) -> frozenset:
        """the processor state the operation writes"""
        return _state_of(self)[1]

    def add_property(self, name : str, value : int|str):
        self.properties[name] = value


def can_reorder(first : lsc_operation, second : lsc_operation) -> bool:
    """
    Checks if two lsc ops have data accesses that require them to be in
    order [first,second] and returns False if the order is required and
    True if the order is not required
    """

    # RAW
    if any([(first.indices[widx] == second.indices[ridx]) \
            and (first.reg_types[widx] == second.reg_types[ridx])\
            for widx in first.writes \
            for ridx in second.reads]):
        return False
    # WAR
    if any([(first.indices[ridx] == second.indices[widx]) \
            and (first.reg_types[ridx] == second.reg_types[widx])\
            for ridx in first.reads \
            for widx in second.writes]):
        return False

    # RAR is not a data hazard
    # WAW is probably also not a hazard - there should be a RAW or WAR somewhere
    # between two ops or the code is malformed

    return True


class ldst_modifier(Enum):
    bcast1 = auto()
    lane = auto()
    postinc = auto()

def _flat(groups) -> list:
    """the signatures in a signature group, a list of them, or one"""
    from ..support.sig_group import sig_group
    if groups is None:
        return []
    if isinstance(groups, (list, tuple)):
        return [s for g in groups for s in _flat(g)]
    if isinstance(groups, sig_group):
        return list(groups.sigs)
    return [groups]


def _state_of(op) -> tuple[frozenset, frozenset]:
    """
    The processor state an operation reads and writes: its signatures'
    (asmgen's state_requires, state_writes - any it may take) and its own -
    memoized on the signatures it holds, again where they change
    """
    sigs = op.state_sigs()
    key = tuple(id(s) for s in sigs)
    if op._state_memo is None or op._state_memo[0] != key:
        reads = frozenset(n for s in sigs for n in s.state_requires)
        writes = frozenset(n for s in sigs for n in s.state_writes)
        op._state_memo = (key, reads, writes)
    return (op._state_memo[1] | frozenset(op.extra_reads_state),
            op._state_memo[2] | frozenset(op.extra_writes_state))


class lsc_load(lsc_operation):
    """
    A load of a component's data register through one of its address
    registers.
    Built by the LSC model, a load or store also carries where its
    instruction comes from - the data movement resolution it is a step of,
    that step and the signatures that can execute it - and its address as a
    record in the model's offset database (off and stride stay unset). The
    register it moves may belong to another owner than the address: the
    scratch register a broadcast is loaded into first.
    """
    def __init__(self,
                 component : str,
                 res_idx : int,
                 addr_idx : int,
                 off : lsc_offset,
                 stride : lsc_offset,
                 t : tile,
                 mods : set[ldst_modifier],
                 *,
                 data : lsc_reg_index | None = None,
                 rsln : str | None = None,
                 step = None,
                 sigs = None,
                 offset : int | None = None,
                 rtypes : list | None = None):
        self.rsln = rsln
        self.step = step
        self.sigs = sigs
        self.offset = offset
        self.rtypes = rtypes
        self.off = off
        self.stride = stride
        self.mods = mods

        tiles = [scalar_tile, t]
        indices = [lsc_reg_index(component, [addr_idx]),
                   data or lsc_reg_index(component, [res_idx])]
        # read address
        reads = [0]
        # write resource
        writes = [1]

        reg_types = [lsc_reg_type.address, lsc_reg_type.data]

        super().__init__(tiles=tiles, indices=indices,
                         reads=reads, writes=writes,
                         reg_types=reg_types)

    def state_sigs(self) -> list:
        return _flat(self.sigs)

    @property
    def res_idx(self):
        return self.indices[1]

    @property
    def addr_idx(self):
        return self.indices[0]

    @property
    def t(self):
        return self.tiles[1]

    def __str__(self):
        offsetstr = f" + {self.off}"
        resstr = f"RES:{self.res_idx}"
        opstr = "LOAD"
        if ldst_modifier.bcast1 in self.mods:
            opstr = "BCAST"
        if ldst_modifier.lane in self.mods:
            resstr += f"[lane:{self.properties['lane']}]"
        if ldst_modifier.postinc in self.mods:
            offsetstr = f"; ADDR:{self.addr_idx} <- ADDR:{self.addr_idx} + {self.off}"
        return f"{resstr} <- {opstr} ADDR:{self.addr_idx}{offsetstr}"

class lsc_store(lsc_operation):
    """
    A store of a component's data register through one of its address
    registers.
    Built by the LSC model, a load or store also carries where its
    instruction comes from - the data movement resolution it is a step of,
    that step and the signatures that can execute it - and its address as a
    record in the model's offset database (off and stride stay unset). The
    register it moves may belong to another owner than the address: the
    scratch register a broadcast is loaded into first.
    """
    def __init__(self,
                 component : str,
                 res_idx : int,
                 addr_idx : int,
                 off : lsc_offset,
                 stride : lsc_offset,
                 t : tile,
                 mods : set[ldst_modifier],
                 *,
                 data : lsc_reg_index | None = None,
                 rsln : str | None = None,
                 step = None,
                 sigs = None,
                 offset : int | None = None,
                 rtypes : list | None = None):
        self.rsln = rsln
        self.step = step
        self.sigs = sigs
        self.offset = offset
        self.rtypes = rtypes
        self.off = off
        self.stride = stride
        self.mods = mods

        tiles = [scalar_tile, t]
        indices = [lsc_reg_index(component, [addr_idx]),
                   data or lsc_reg_index(component, [res_idx])]
        # read resource
        reads = [0,1]
        # we write memory, not the address register
        writes = []

        reg_types = [lsc_reg_type.address, lsc_reg_type.data]

        super().__init__(tiles=tiles, indices=indices,
                         reads=reads, writes=writes,
                         reg_types=reg_types)
    def state_sigs(self) -> list:
        return _flat(self.sigs)

    @property
    def res_idx(self):
        return self.indices[1]

    @property
    def addr_idx(self):
        return self.indices[0]

    @property
    def t(self):
        return self.tiles[1]

    def __str__(self):
        offsetstr = f" + {self.off}"
        poststr = ""
        resstr = f"RES:{self.res_idx}"
        if ldst_modifier.lane in self.mods:
            resstr += f"[lane:{self.properties['lane']}]"
        if ldst_modifier.postinc in self.mods:
            offsetstr = ""
            poststr = f"; ADDR:{self.addr_idx} <- ADDR:{self.addr_idx} + {self.off}"
        return f"ADDR:{self.addr_idx}{offsetstr} <- STORE {resstr}{poststr}"

class lsc_zero(lsc_operation):
    def __init__(self, component : str, res_idx : int, t : tile, *, rtypes : list | None = None):
        self.rtypes = rtypes

        tiles = [t]
        indices = [lsc_reg_index(component, [res_idx])]
        reads = []
        # write resource
        writes = [0]

        reg_types = [lsc_reg_type.data]

        super().__init__(tiles=tiles, indices=indices,
                         reads=reads, writes=writes,
                         reg_types=reg_types)

    @property
    def res_idx(self):
        return self.indices[0]

    @property
    def t(self):
        return self.tiles[0]

    def __str__(self):
        return f"RES:{self.res_idx} <- 0"

class lsc_addr_add(lsc_operation):
    def __init__(self, component : str, addr_idx : int, off : lsc_offset, t : tile):
        if not isinstance(off, lsc_offset):
            raise ValueError(f"offset {off} is not an lsc_offset")
        self.off = off

        # t is used for calculating address, isn't the tile the address resides in
        tiles = [scalar_tile, t]
        indices = [lsc_reg_index(component, [addr_idx])]
        # read addr
        reads = [0]
        # write addr
        writes = [0]
        
        reg_types = [lsc_reg_type.address]


        super().__init__(tiles=tiles, indices=indices,
                         reads=reads, writes=writes,
                         reg_types=reg_types)

    @property
    def addr_idx(self):
        return self.indices[0]

    @property
    def t(self):
        return self.tiles[1]

    def __str__(self):
        ar_str = f"ADDR:{self.addr_idx}"
        return f"{ar_str} <- {ar_str} + {self.off}"

class lsc_addr_compute(lsc_operation):
    """
    An address register set from another plus an offset in elements of the
    component: dest = src + delta. delta may contain run-time strides
    (stride(C,n)) and is resolved to bytes when emitted. Inserted when
    specializing for the ISA: column pointers for strided accesses, and scratch
    addresses for accesses at offsets no signature takes.
    """
    def __init__(self, component : str, src_idx : int, dest_idx : int, delta, t : tile):
        self.delta = delta
        super().__init__(tiles=[scalar_tile, scalar_tile],
                         indices=[lsc_reg_index(component, [src_idx]),
                                  lsc_reg_index(component, [dest_idx])],
                         reads=[0], writes=[1],
                         reg_types=[lsc_reg_type.address, lsc_reg_type.address])

    def __str__(self):
        return f"{self.indices[1]} <- {self.indices[0]} + {self.delta}"


class lsc_add_val_off(lsc_operation):
    def __init__(self, valname : str, off : lsc_offset):
        if not isinstance(off, lsc_offset):
            raise ValueError(f"offset {off} is not an lsc_offset")
        self.off = off
        self.valname = valname

        # t is used for calculating address, isn't the tile the address resides in
        tiles = [scalar_tile]
        indices = []
        # read addr
        reads = [0]
        # write addr
        writes = [0]
        
        reg_types = [lsc_reg_type.value]


        super().__init__(tiles=tiles, indices=indices,
                         reads=reads, writes=writes,
                         reg_types=reg_types)

    def __str__(self):
        return f"{self.valname} <- {self.valname} + {self.off}"

class lsc_debugmsg(lsc_operation):
    def __init__(self, msg : str):
        super(lsc_debugmsg, self).__init__(tiles=[], indices=[], reads=[], writes=[], reg_types=[])
        self.msg = msg
    def __str__(self):
        return self.msg


class lsc_move(lsc_operation):
    """
    A register-to-register step of a data movement: broadcasting a scalar
    loaded into a scratch register, moving a lane. Carries the resolution it
    belongs to, the step and the signatures that can execute it.
    """
    def __init__(self, src : lsc_reg_index, dest : lsc_reg_index,
                 tiles : list[tile], *, rsln : str | None = None, step = None,
                 sigs = None, rtypes : list | None = None):
        self.rsln = rsln
        self.step = step
        self.sigs = sigs
        self.rtypes = rtypes
        super().__init__(tiles=tiles, indices=[src, dest], reads=[0], writes=[1],
                         reg_types=[lsc_reg_type.data, lsc_reg_type.data])

    def state_sigs(self) -> list:
        return _flat(self.sigs)

    def __str__(self):
        return f"{self.indices[1]} <- MOVE {self.indices[0]}"


class lsc_permute(lsc_move):
    """
    Two registers' elements permuted into a third - asmgen's opmove PERMUTE,
    its signature saying how (pattern, bits, segment): a round of an
    in-register transpose. A move to the scheduler (a vector permute).
    """
    def __init__(self, a : lsc_reg_index, b : lsc_reg_index, dest : lsc_reg_index,
                 tiles : list[tile], *, sig, rtypes : list):
        lsc_operation.__init__(self, tiles=tiles, indices=[a, b, dest], reads=[0, 1], writes=[2],
                               reg_types=[lsc_reg_type.data] * 3)
        self.rsln = None
        self.step = None
        self.sigs = [sig]
        self.rtypes = rtypes

    def __str__(self):
        return f"{self.indices[2]} <- PERMUTE {self.indices[0]}, {self.indices[1]}"


class tr_modifier(Enum):
    np = auto()
    
class lsc_transformation(lsc_operation):
    """
    An arithmetic operation on data registers.

    Built by the LSC model it also carries the solved operation it executes
    (resolution: its compute signature group and how each operand gets its
    data), the hardware operand behind each register position, and reads and
    writes from the requirement rather than the gemm-shaped defaults.
    """
    def __init__(self, op : str,
                 res_indices : list[lsc_reg_index],
                 tiles : list[tile],
                 reads : list[int] = [0,1,2],
                 writes : list[int] = [2],
                 *,
                 resolution = None,
                 hw_operands : list[str] | None = None,
                 rtypes : list | None = None):
        self.resolution = resolution
        self.hw_operands = hw_operands
        self.rtypes = rtypes

        #TODO: This is needed because registers might get replaced (for example by the
        #      minreguse_scheduler) and we need component assignments to actual data.
        #      In other I/O ops we can just use component of addr_idx. Possibly come up
        #      with a better system?
        self.data_components = [idx.component for idx in res_indices]

        opsplit = op.split(":")
        opstr = opsplit[0]
        self.op = opstr
        self.mods = []
        if 1 < len(opsplit):
            modlist = opsplit[1].split(",")        
            self.mods = [tr_modifier[m] for m in modlist]
        reg_types = [lsc_reg_type.data for i in range(len(res_indices))]
        super(lsc_transformation, self).__init__(tiles=tiles, indices=res_indices,
                                                 reads=reads, writes=writes,
                                                 reg_types=reg_types)


    def state_sigs(self) -> list:
        return _flat(self.resolution.compute_sg) if self.resolution is not None else []

    @property
    def modifiers(self):
        return self.mods

    def __str__(self):
        regstrs = [f"RES:{idx}" for idx in self.indices]

        modstr = [str(m).replace('tr_modifier.','') for m in self.mods]
        if modstr:
            modstr = ":"+f"{{{','.join(modstr)}}}"
        else:
            modstr = ""
        out = f"{regstrs[-1]} <- {self.op}{modstr}("
        out += ", ".join(regstrs)
        out += ")"
        return out



@dataclass
class loop_walk:
    """
    A pointer a loop walks: from the address of anchor - an access of the
    first element, which the stages before emission address like any - by
    step elements along the walk's index each iteration (the subtiling's
    order: forwards, or from the last element backwards)
    """
    anchor : lsc_operation
    step : object


class lsc_loop(lsc_operation):
    """
    A loop as an instruction: its block - operations, loops among them - run
    for each subtile its subtiling counts (a vla count: as many times as a
    vector has elements at run time; a fixed one: unrolled), the walks'
    pointers moved after each. To the scheduler it reads and writes what its
    block does, and its walks' address registers.

    info: what the loop does as data - component, index, element stride,
        direction - for irmods turning it into a vector access where the ISA
        has one
    """

    def __init__(self, *, block, subtiling, walks, info=None):
        super().__init__(tiles=[], indices=[], reads=[], writes=[], reg_types=[])
        self.block = block
        self.subtiling = subtiling
        self.walks = walks
        self.info = info or {}
        self.refresh()

    def refresh(self):
        """
        The registers the loop reads and writes, from its walks and block
        """
        self.indices, self.rtypes, self.reads, self.writes = [], [], [], []
        self.reg_types = []
        for w in self.walks:
            self.indices.append(w.anchor.indices[0])
            self.rtypes.append(None)
            self.reg_types.append(w.anchor.reg_types[0])
            self.reads.append(len(self.indices) - 1)
        for op in self.block:
            types = op.rtypes or [None] * len(op.indices)
            kinds = op.reg_types or []
            for p, idx in enumerate(op.indices):
                self.indices.append(idx)
                self.rtypes.append(types[p] if p < len(types) else None)
                self.reg_types.append(kinds[p] if p < len(kinds) else lsc_reg_type.data)
                if p in op.reads:
                    self.reads.append(len(self.indices) - 1)
                if p in op.writes:
                    self.writes.append(len(self.indices) - 1)
        # the address registers it walks (its walk plan): moved by it - read
        # and written
        for comp, reg in (self.walk_plan or {}):
            self.indices.append(lsc_reg_index(comp, [reg]))
            self.rtypes.append(None)
            self.reg_types.append(lsc_reg_type.address)
            self.reads.append(len(self.indices) - 1)
            self.writes.append(len(self.indices) - 1)


class lsc_state(lsc_operation):
    """
    Sets processor state: values, name -> value - "vlen": "tail(m)" (the
    count a kernel parameter holds), "max" - as asmgen's signatures'
    state_writes name them; emitted through the generator's signature
    writing them. It writes each state it sets: the schedulers keep every
    operation reading one on its side of it
    """
    def __init__(self, values: dict[str, str], dt=None):
        super().__init__(tiles=[], indices=[], reads=[], writes=[], reg_types=[])
        self.values = dict(values)
        #: the element type a vector length is set for (RVV's vtype)
        self.dt = dt
        self.extra_writes_state = set(values)

    def __str__(self) -> str:
        return "state(" + ", ".join(f"{k}={v}" for k, v in self.values.items()) + ")"

    def __repr__(self) -> str:
        return self.__str__()
