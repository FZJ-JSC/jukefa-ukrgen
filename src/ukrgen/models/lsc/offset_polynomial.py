"""
Offset polynomials: an offset as the IR holds it, over named factors.

2*VL + 3*stride(C,n) is {("VL",): 2, ("stride(C,n)",): 3}: a named factor is
the vector length in elements or a run-time stride, a constant the empty one.
Neither an ISA's layout nor a value's own - the model's offsets, the IR's
strides and the emitter's immediates all mean this one polynomial.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...components.tile import dimension_properties as dimp, dimension_type as dimt


@dataclass(frozen=True)
class offset_polynomial:
    """
    A polynomial over named factors: VL (vector length in elements of the
    component's type) and run-time strides. 2*VL + 3*stride(C,n) is
    {("VL",): 2, ("stride(C,n)",): 3}.
    """
    terms : tuple[tuple[tuple[str, ...], int], ...] = ()

    @staticmethod
    def of(value) -> offset_polynomial:
        return value if isinstance(value, offset_polynomial) else offset_polynomial.const(value)

    @staticmethod
    def _make(d: dict) -> offset_polynomial:
        return offset_polynomial(tuple(sorted((k, v) for k, v in d.items() if v)))

    @staticmethod
    def const(n: int) -> offset_polynomial:
        return offset_polynomial._make({(): n})

    @staticmethod
    def factor(name: str, n: int = 1) -> offset_polynomial:
        return offset_polynomial._make({(name,): n})

    @staticmethod
    def extent(d: dimp) -> offset_polynomial:
        """
        Elements a dimension spans: size vector lengths, or size elements
        """
        return offset_polynomial.factor("VL", d.size) if dimt.vla == d.dt else offset_polynomial.const(d.size)

    def __add__(self, other) -> offset_polynomial:
        d = dict(self.terms)
        for k, v in offset_polynomial.of(other).terms:
            d[k] = d.get(k, 0) + v
        return offset_polynomial._make(d)

    __radd__ = __add__

    def __neg__(self) -> offset_polynomial:
        return offset_polynomial._make({k: -v for k, v in self.terms})

    def __sub__(self, other) -> offset_polynomial:
        return self + (-offset_polynomial.of(other))

    def __mul__(self, other) -> offset_polynomial:
        d: dict = {}
        for k1, v1 in self.terms:
            for k2, v2 in offset_polynomial.of(other).terms:
                k = tuple(sorted(k1 + k2))
                d[k] = d.get(k, 0) + v1 * v2
        return offset_polynomial._make(d)

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
