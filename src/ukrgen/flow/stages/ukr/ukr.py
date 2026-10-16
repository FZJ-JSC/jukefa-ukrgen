"""
Microkernels described as compositions of tile operations (STOs).

A composition declares three things: the components the kernel works on, the
STOs acting on them, and the blocks those STOs are grouped into. Everything the
later stages need beyond that - operand roles, scalars, accumulators, and where
each operand's data comes from and goes to - is derived from these declarations
rather than written down per kernel. The previous version declared much of it by
hand (sup tile names, dimension lambdas, diagonal bands for scalars); those were
answers to questions the requirement AST now answers itself.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

from ....matching.math import (
    ast_node,
    expression_node,
    operand_ref,
    operation,
    for_each_operand,
    get_operand_io,
    recurse_indices,
    reduction_dims,
)


# ---------------------------------------------------------------------------
# components
# ---------------------------------------------------------------------------

class storage_class(Enum):
    """
    Where a component lives outside the STOs that use it.

    MEMORY:   passed to the kernel through memory (A, B, C, alpha, ...)
    REGISTER: exists only inside the kernel (the gemm accumulator AB)
    """
    MEMORY = auto()
    REGISTER = auto()


class component_init(Enum):
    """
    What the first read of a component sees.

    LOAD: its value in memory
    ZERO: zero - an accumulator that starts from nothing
    """
    LOAD = auto()
    ZERO = auto()


@dataclass(frozen=True, kw_only=True)
class component_description:
    """
    One component of a microkernel.

    :param name: component name, as used in the requirement ASTs
    :param storage: where the component lives
    :param init: what its first read sees; defaults to LOAD for memory
                 components and ZERO for register-only ones
    :param dt_reference: name of the component whose data type this one takes.
                         Such components get no data type parameter of their own
                         (gemm's alpha and beta take C's).
    :param parameterized: whether the component gets register-count and preload
                          parameters
    """
    name: str
    storage: storage_class
    init: component_init | None = None
    dt_reference: str | None = None
    parameterized: bool = True

    @property
    def initial(self) -> component_init:
        """
        What the first read of this component sees
        """
        if self.init is not None:
            return self.init
        if storage_class.REGISTER == self.storage:
            return component_init.ZERO
        return component_init.LOAD


# ---------------------------------------------------------------------------
# STOs
# ---------------------------------------------------------------------------

class sto_kind(Enum):
    """
    COMPUTE: has a requirement AST; needs math matching and data movement
    STORE:   writes components to memory; data movement only
    """
    COMPUTE = auto()
    STORE = auto()


def _leaves(ast: ast_node) -> list[operand_ref]:
    return list(for_each_operand(ast, lambda x: x))


@dataclass(frozen=True, kw_only=True)
class sto_description:
    """
    One set of tile operations.

    :param name: STO name; also names its command line choice (--<name>-to)
    :param kind: compute or store
    :param generator: tiling generator producing the STO (compute only)
    :param req: requirement AST (compute only)
    :param store_components: components written to memory (store only)
    :param store_into: (stored component, memory component) pairs for a store
                       writing one component's value into another's memory:
                       gemm's AB into C when alpha is 1 and beta 0. Components
                       not listed are stored into their own memory.
    """
    name: str
    kind: sto_kind
    generator: str | None = None
    req: ast_node | None = None
    store_components: tuple[str, ...] = ()
    store_into: tuple[tuple[str, str], ...] = ()

    def memory_of(self, component: str) -> str:
        """
        The memory component a store writes a component into
        """
        return dict(self.store_into).get(component, component)

    def __post_init__(self):
        if sto_kind.COMPUTE == self.kind:
            if self.req is None or self.generator is None:
                raise ValueError(f"compute STO {self.name} needs a requirement and a generator")
            if not isinstance(self.req, expression_node) or operation.MOVE != self.req.op:
                raise ValueError(f"requirement of {self.name} must be a MOVE into its result")
            if self.store_components:
                raise ValueError(f"compute STO {self.name} cannot store components")
        else:
            if not self.store_components:
                raise ValueError(f"store STO {self.name} has nothing to store")
            if self.req is not None or self.generator is not None:
                raise ValueError(f"store STO {self.name} takes no requirement or generator")

    @property
    def operands(self) -> tuple[str, ...]:
        """
        Operands of the STO, in order of first appearance
        """
        if sto_kind.STORE == self.kind:
            return self.store_components

        seen: list[str] = []
        for leaf in _leaves(self.req):
            if leaf.name not in seen:
                seen.append(leaf.name)
        return tuple(seen)

    @property
    def operand_indices(self) -> dict[str, tuple[str | None, ...]]:
        """
        Index tuple of each operand. Empty for a store STO: what it stores takes
        its shape from the STO that produced it.
        """
        if sto_kind.STORE == self.kind:
            return {}

        indices: dict[str, tuple[str | None, ...]] = {}
        for leaf in _leaves(self.req):
            known = indices.setdefault(leaf.name, leaf.indices)
            if known != leaf.indices:
                raise ValueError(f"{self.name}: operand {leaf.name} appears as both "
                                 f"{known} and {leaf.indices}")
        return indices

    def live_indices(self, operand: str) -> tuple[str, ...]:
        """
        Indices an operand actually varies along
        """
        return tuple(i for i in self.operand_indices.get(operand, ()) if i is not None)

    @property
    def indices(self) -> tuple[str, ...]:
        """
        Every index of the STO's iteration space, including reduction indices
        """
        if sto_kind.STORE == self.kind:
            return ()
        found = list(recurse_indices(self.req))
        for red in sorted(reduction_dims(self.req)):
            if red not in found:
                found.append(red)
        return tuple(found)

    @property
    def reduction_indices(self) -> frozenset[str]:
        """
        Indices summed over. Instances along these accumulate into the same output
        rather than producing distinct ones.
        """
        if sto_kind.STORE == self.kind:
            return frozenset()
        return frozenset(reduction_dims(self.req))

    def io(self, operand: str) -> tuple[bool, bool]:
        """
        (read, written) for an operand. A store STO reads the register copy of what
        it stores and writes it to memory.
        """
        if sto_kind.STORE == self.kind:
            return (operand in self.store_components, operand in self.store_components)
        return get_operand_io(self.req, operand)

    @property
    def scalars(self) -> frozenset[str]:
        """
        Operands that vary along no index. These replace the diagonal-band tiles the
        mm generator used to fake a scalar with.
        """
        return frozenset(op for op in self.operands
                         if sto_kind.COMPUTE == self.kind and not self.live_indices(op))


@dataclass(frozen=True, kw_only=True)
class block_description:
    """
    STOs executed together.

    :param stos: names of the STOs, in order
    :param loop_index: index the block loops over; None for straight-line code
    :param preload: whether operands streamed by the loop are loaded ahead
    :param tail: whether the loop needs remainder handling
    """
    stos: tuple[str, ...]
    loop_index: str | None = None
    preload: bool = False
    tail: bool = False

    @property
    def is_loop(self) -> bool:
        """
        Whether the block is a loop
        """
        return self.loop_index is not None


@dataclass(frozen=True, kw_only=True)
class case_description:
    """
    One way a branch continues

    :param when: scalar component -> value it must equal; empty for the default
    :param blocks: blocks the case runs, in order
    """
    when: dict = field(default_factory=dict)
    blocks: tuple[block_description, ...] = ()

    @property
    def label(self) -> str:
        if not self.when:
            return "otherwise"
        return " and ".join(f"{c}=={v:g}" for c, v in self.when.items())


@dataclass(frozen=True, kw_only=True)
class branch_description:
    """
    The kernel continuing one of several ways, on run-time values of scalar
    components - gemm's epilogue for beta 0, alpha 1 and so on. Cases are tried
    in order and the first whose conditions all hold runs; the last is the
    default. A branch ends the kernel: every case runs to the end, so no two
    cases have to agree on what they leave in registers.
    """
    cases: tuple[case_description, ...]


# ---------------------------------------------------------------------------
# data flow between STOs
# ---------------------------------------------------------------------------

class read_access(Enum):
    """
    How an STO obtains an operand it reads.

    LOAD:     loaded from memory once, before first use
    STREAM:   loaded from memory on every iteration of the enclosing loop
    ZERO:     starts as zero; nothing is loaded
    RESIDENT: already in registers, left there by an earlier STO
    """
    LOAD = auto()
    STREAM = auto()
    ZERO = auto()
    RESIDENT = auto()


class write_access(Enum):
    """
    Where an STO puts an operand it writes.

    REGISTER:      stays in registers for later STOs
    MEMORY:        stored to memory once
    MEMORY_STREAM: stored to memory on every iteration of the enclosing loop
    """
    REGISTER = auto()
    MEMORY = auto()
    MEMORY_STREAM = auto()


@dataclass(frozen=True)
class operand_access:
    """
    How one STO reads and writes one operand. None means it does not.
    """
    read: read_access | None
    write: write_access | None

    def __str__(self):
        r = self.read.name if self.read else "-"
        w = self.write.name if self.write else "-"
        return f"{r}>{w}"


# ---------------------------------------------------------------------------
# compositions
# ---------------------------------------------------------------------------

class ukr_composition(ABC):
    """
    A microkernel as a composition of STOs. Subclasses declare components, STOs and
    blocks; everything else is derived.
    """

    @classmethod
    @abstractmethod
    def get_components(cls) -> list[component_description]:
        """
        All components the microkernel uses
        """

    @classmethod
    @abstractmethod
    def get_sto_descriptions(cls) -> list[sto_description]:
        """
        All STOs of the microkernel
        """

    @classmethod
    @abstractmethod
    def get_blocks(cls) -> list[block_description]:
        """
        The blocks the STOs are grouped into, in execution order
        """

    # --- lookups -----------------------------------------------------------

    @classmethod
    def get_component(cls, name: str) -> component_description:
        """
        Component by name
        """
        for comp in cls.get_components():
            if comp.name == name:
                return comp
        raise KeyError(f"{cls.__name__} has no component {name}")

    @classmethod
    def get_sto(cls, name: str) -> sto_description:
        """
        STO by name
        """
        for sto in cls.get_sto_descriptions():
            if sto.name == name:
                return sto
        raise KeyError(f"{cls.__name__} has no STO {name}")

    @classmethod
    def get_parameterized_components(cls) -> list[str]:
        """
        Components that get register-count and preload parameters
        """
        return [c.name for c in cls.get_components() if c.parameterized]

    @classmethod
    def get_typed_components(cls) -> list[str]:
        """
        Components with a data type of their own (not taken from another component)
        """
        return [c.name for c in cls.get_components() if c.dt_reference is None]

    @classmethod
    def dt_source(cls, name: str) -> str:
        """
        The component whose data type a component takes, following references
        """
        seen = [name]
        comp = cls.get_component(name)
        while comp.dt_reference is not None:
            if comp.dt_reference in seen:
                raise ValueError(f"data type references form a cycle: {seen}")
            seen.append(comp.dt_reference)
            comp = cls.get_component(comp.dt_reference)
        return comp.name

    @classmethod
    def get_branch(cls) -> branch_description | None:
        """
        The branch ending the kernel, if any
        """
        blocks = cls.get_blocks()
        return blocks[-1] if blocks and isinstance(blocks[-1], branch_description) else None

    @classmethod
    def paths(cls) -> list[tuple[case_description | None, list[block_description]]]:
        """
        Every way through the kernel: the blocks before the branch, then one
        case's. A kernel without a branch has one path, with no case.
        """
        prefix = [b for b in cls.get_blocks() if isinstance(b, block_description)]
        branch = cls.get_branch()
        if branch is None:
            return [(None, prefix)]
        return [(case, prefix + list(case.blocks)) for case in branch.cases]

    @classmethod
    def all_blocks(cls) -> list[block_description]:
        """
        Every block of every path, once each
        """
        found: list[block_description] = []
        for _, blocks in cls.paths():
            for block in blocks:
                if not any(block is b for b in found):
                    found.append(block)
        return found

    @classmethod
    def sto_order(cls) -> list[str]:
        """
        Every STO once, in the order the kernel first runs it
        """
        order = []
        for block in cls.all_blocks():
            for name in block.stos:
                if name not in order:
                    order.append(name)
        return order

    @classmethod
    def block_of(cls, sto_name: str) -> block_description:
        """
        The block an STO belongs to
        """
        for block in cls.all_blocks():
            if sto_name in block.stos:
                return block
        raise KeyError(f"STO {sto_name} is in no block")

    # --- derived properties -----------------------------------------------

    @classmethod
    def accumulators(cls, sto_name: str) -> frozenset[str]:
        """
        Operands an STO in a loop both reads and writes without varying along the
        loop index: they accumulate across iterations in registers
        """
        sto = cls.get_sto(sto_name)
        block = cls.block_of(sto_name)
        if sto_kind.STORE == sto.kind or not block.is_loop:
            return frozenset()
        return frozenset(op for op in sto.operands
                         if all(sto.io(op))
                         and block.loop_index not in sto.live_indices(op))

    @classmethod
    def dataflow(cls, path: list[block_description] | None = None) \
            -> dict[tuple[str, str], operand_access]:
        """
        How every STO obtains and disposes of every operand - along one path,
        or over all of them. An STO shared by several cases must access its
        operands the same way in each: it has one implementation.

        :raises ValueError: if a shared STO's accesses differ between cases
        """
        if path is not None:
            return cls._flow_of(path)
        merged: dict[tuple[str, str], operand_access] = {}
        for case, blocks in cls.paths():
            for key, access in cls._flow_of(blocks).items():
                known = merged.setdefault(key, access)
                if known != access:
                    raise ValueError(
                        f"STO {key[0]} accesses {key[1]} as {known} in one case and as "
                        f"{access} in another ({case.label if case else ''}): it has one "
                        f"implementation, so give each case its own STO")
        return merged

    @classmethod
    def _flow_of(cls, path: list[block_description]) -> dict[tuple[str, str], operand_access]:
        """
        How every STO obtains and disposes of every operand.

        Walks the blocks in order, tracking which components currently have their
        value in registers. A component read for the first time is loaded from
        memory - once, or on every iteration if it varies along the loop index - or
        starts as zero; afterwards it is resident. Values streamed through a loop
        are not resident after it: only the last iteration's slice was ever held.

        :return: (STO name, operand) -> access
        """
        flow: dict[tuple[str, str], operand_access] = {}
        live: set[str] = set()
        shape: dict[str, tuple[str, ...]] = {}

        for block in path:
            streamed: set[str] = set()

            for sto_name in block.stos:
                sto = cls.get_sto(sto_name)

                for op in sto.operands:
                    comp = cls.get_component(op)
                    reads, writes = sto.io(op)

                    if sto_kind.COMPUTE == sto.kind:
                        shape[op] = sto.live_indices(op)
                    varies = block.is_loop and block.loop_index in shape.get(op, ())

                    read = None
                    if reads:
                        if op in live:
                            read = read_access.RESIDENT
                        elif component_init.ZERO == comp.initial:
                            read = read_access.ZERO
                        elif varies:
                            read = read_access.STREAM
                        else:
                            read = read_access.LOAD

                    write = None
                    if sto_kind.STORE == sto.kind:
                        write = write_access.MEMORY_STREAM if varies else write_access.MEMORY
                    elif writes:
                        write = write_access.REGISTER

                    flow[(sto_name, op)] = operand_access(read, write)

                    if read in (read_access.LOAD, read_access.ZERO) or \
                            write_access.REGISTER == write:
                        live.add(op)
                    if read_access.STREAM == read:
                        streamed.add(op)

            live -= streamed

        return flow

    @classmethod
    def validate(cls):
        """
        Check that the declarations are consistent

        :raises ValueError: describing the first inconsistency found
        """
        names = [c.name for c in cls.get_components()]
        if len(set(names)) != len(names):
            raise ValueError(f"{cls.__name__}: duplicate component names {names}")

        for comp in cls.get_components():
            if comp.dt_reference is not None and comp.dt_reference not in names:
                raise ValueError(f"{comp.name} takes its data type from unknown "
                                 f"component {comp.dt_reference}")
            cls.dt_source(comp.name)

        stos = [s.name for s in cls.get_sto_descriptions()]
        if len(set(stos)) != len(stos):
            raise ValueError(f"{cls.__name__}: duplicate STO names {stos}")

        blocks = cls.get_blocks()
        for pos, block in enumerate(blocks):
            if isinstance(block, branch_description) and pos != len(blocks) - 1:
                raise ValueError(f"{cls.__name__}: a branch must end the kernel")
        branch = cls.get_branch()
        if branch is not None:
            if not branch.cases or branch.cases[-1].when:
                raise ValueError(f"{cls.__name__}: the last case of a branch must be the "
                                 f"default, with no conditions")
            for case in branch.cases[:-1]:
                if not case.when:
                    raise ValueError(f"{cls.__name__}: only the last case may be the default")
                for comp in case.when:
                    if comp not in names:
                        raise ValueError(f"case {case.label} tests undeclared component {comp}")

        placed = set()
        for case, path in cls.paths():
            in_path = [name for block in path for name in block.stos]
            if len(set(in_path)) != len(in_path):
                raise ValueError(f"{cls.__name__}: an STO runs twice along one path "
                                 f"({case.label if case else 'the kernel'}): {in_path}")
            placed |= set(in_path)
        if placed != set(stos):
            raise ValueError(f"{cls.__name__}: every STO must be in a block "
                             f"(declared {sorted(stos)}, placed {sorted(placed)})")

        for sto in cls.get_sto_descriptions():
            for op in sto.operands:
                if op not in names:
                    raise ValueError(f"STO {sto.name} uses undeclared component {op}")

        for block in cls.all_blocks():
            if block.is_loop and not any(block.loop_index in cls.get_sto(s).indices
                                         for s in block.stos):
                raise ValueError(f"block {block.stos} loops over {block.loop_index}, "
                                 f"which none of its STOs uses")

        for sto in cls.get_sto_descriptions():
            for value, memory in sto.store_into:
                if value not in sto.store_components or memory not in names or \
                        storage_class.MEMORY != cls.get_component(memory).storage:
                    raise ValueError(f"STO {sto.name} stores {value} into {memory}, which "
                                     f"must be one of its components and in memory")

        # a store needs a value to store, along every path it is on
        flow = cls.dataflow()
        for sto in cls.get_sto_descriptions():
            if sto_kind.STORE != sto.kind:
                continue
            for op in sto.store_components:
                if read_access.RESIDENT != flow[(sto.name, op)].read:
                    raise ValueError(f"STO {sto.name} stores {op}, which no earlier STO "
                                     f"leaves in registers")


def scalar(name: str) -> operand_ref:
    """
    Requirement operand varying along no index.

    Written with two None indices rather than none so it also matches the current
    positional matcher; anything checking for scalars looks for "no live index",
    so both forms work.
    """
    return operand_ref(name=name, indices=(None, None))
