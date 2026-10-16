"""
Addresses as data: symbolic offsets, an offset database and address registers.

The model does not compute addresses. It records where each access goes - a
component and an element offset along each of the component's indices - and
codegen turns the records into byte offsets, immediates and pointer increments,
which depend on immediate ranges only the chosen signatures know.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..components.tile import dimension_properties as dimp, dimension_type as dimt


@dataclass(frozen=True)
class sym:
    """
    A polynomial over named factors: VL (vector length in elements of the
    component's type) and run-time strides. 2*VL + 3*stride(C,n) is
    {("VL",): 2, ("stride(C,n)",): 3}.
    """
    terms : tuple[tuple[tuple[str, ...], int], ...] = ()

    @staticmethod
    def of(value) -> sym:
        return value if isinstance(value, sym) else sym.const(value)

    @staticmethod
    def _make(d: dict) -> sym:
        return sym(tuple(sorted((k, v) for k, v in d.items() if v)))

    @staticmethod
    def const(n: int) -> sym:
        return sym._make({(): n})

    @staticmethod
    def factor(name: str, n: int = 1) -> sym:
        return sym._make({(name,): n})

    @staticmethod
    def extent(d: dimp) -> sym:
        """
        Elements a dimension spans: size vector lengths, or size elements
        """
        return sym.factor("VL", d.size) if dimt.vla == d.dt else sym.const(d.size)

    def __add__(self, other) -> sym:
        d = dict(self.terms)
        for k, v in sym.of(other).terms:
            d[k] = d.get(k, 0) + v
        return sym._make(d)

    __radd__ = __add__

    def __neg__(self) -> sym:
        return sym._make({k: -v for k, v in self.terms})

    def __sub__(self, other) -> sym:
        return self + (-sym.of(other))

    def __mul__(self, other) -> sym:
        d: dict = {}
        for k1, v1 in self.terms:
            for k2, v2 in sym.of(other).terms:
                k = tuple(sorted(k1 + k2))
                d[k] = d.get(k, 0) + v1 * v2
        return sym._make(d)

    __rmul__ = __mul__

    def is_zero(self) -> bool:
        return not self.terms

    def __str__(self) -> str:
        if not self.terms:
            return "0"
        parts = []
        # the constant last: 2*VL + 3
        for factors, coeff in sorted(self.terms, key=lambda t: (not t[0], t[0])):
            if not factors:
                parts.append(str(coeff))
            else:
                parts.append("*".join(([str(coeff)] if 1 != coeff else []) + list(factors)))
        return " + ".join(parts).replace("+ -", "- ")


def layout_strides(component: str,
                   kinds: dict[str, str],
                   packing: list[str],
                   extents: dict[str, sym]) -> dict[str, sym]:
    """
    Stride of each index of a memory component, in elements

    :param component: component name, naming its run-time strides
    :param kinds: index -> "c" (contiguous), "p" (packed) or "s" (strided)
    :param packing: contiguous and packed indices, innermost first
    :param extents: elements the microtile spans along each index: what a
                    packed index is packed around
    :return: index -> stride. Contiguous is 1, packed the product of the
             extents inside it, strided a run-time factor stride(component,index)
    """
    strides: dict[str, sym] = {}
    inner = sym.const(1)
    for idx in packing:
        strides[idx] = inner
        inner = inner * extents[idx]
    for idx, kind in kinds.items():
        if "s" == kind:
            strides[idx] = sym.factor(f"stride({component},{idx})")
    return strides


@dataclass(frozen=True)
class offset_record:
    """
    Where an access goes: element offsets along the component's indices
    """
    component : str
    elements : tuple[tuple[str, sym], ...]

    def along(self, index: str) -> sym:
        return dict(self.elements).get(index, sym())

    def __str__(self):
        inner = ",".join(f"{i}:{e}" for i, e in self.elements)
        return f"{self.component}[{inner}]"


class offset_db:
    """
    Offsets registered by the model and resolved at codegen. Equal offsets get
    the same id.
    """

    def __init__(self):
        self.records : list[offset_record] = []
        self.ids : dict[offset_record, int] = {}

    def add(self, component: str, elements: dict[str, sym]) -> int:
        rec = offset_record(component=component,
                            elements=tuple(sorted((i, sym.of(e)) for i, e in elements.items()
                                                  if not sym.of(e).is_zero())))
        if rec not in self.ids:
            self.ids[rec] = len(self.records)
            self.records.append(rec)
        return self.ids[rec]

    def __getitem__(self, oid: int) -> offset_record:
        return self.records[oid]

    def shifted(self, oid: int, index: str, amount: sym) -> int:
        """
        The same offset moved along one index - the same access one loop
        iteration later
        """
        rec = self.records[oid]
        elements = dict(rec.elements)
        elements[index] = elements.get(index, sym()) + amount
        return self.add(rec.component, elements)

    def elements_offset(self, oid: int, strides: dict[str, sym]) -> sym:
        """
        Offset in elements from the component's base, given its strides
        """
        total = sym()
        for idx, e in self.records[oid].elements:
            total = total + e * strides[idx]
        return total


class addr_pattern:
    """
    Which of a component's address registers an access uses: a pure function
    of the access's position among the component's accesses, and of its phase
    (which STO and direction it belongs to). Being a function rather than a
    stateful rotation, a pattern cannot drift.

        rotate     0,1,2,0,1,2,...
        blocked:N  N accesses per register: blocked:2 gives 0,0,1,1,2,2,0,0,...
        phase      one register per phase, e.g. C's loads and C's stores, so
                   the stores need no rewinding
    """

    def __init__(self, kind: str, block: int = 1):
        self.kind = kind
        self.block = block

    @staticmethod
    def parse(spec: str) -> addr_pattern:
        name, _, arg = spec.partition(":")
        if "rotate" == name and not arg:
            return addr_pattern("rotate")
        if "phase" == name and not arg:
            return addr_pattern("phase")
        if "blocked" == name and arg.isdigit() and int(arg) > 0:
            return addr_pattern("blocked", int(arg))
        raise ValueError(f"not an address register pattern: {spec} "
                         f"(rotate, blocked:<n> or phase)")

    def select(self, access: int, phase: int, registers: int) -> int:
        """
        :param access: position of the access among the component's accesses
        :param phase: index of the access's phase
        :param registers: number of address registers
        """
        if "phase" == self.kind:
            return phase % registers
        return (access // self.block) % registers

    def __str__(self):
        return f"blocked:{self.block}" if "blocked" == self.kind else self.kind
