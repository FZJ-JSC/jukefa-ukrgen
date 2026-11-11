"""
The LSC model: load-store-compute codegen as one place.

The tiled STOs and their implementations as loads, stores and computations
(`operations`), the IR they build into (`ir`, `builder`), the address
polynomials they carry (`offset_polynomial`, `addressing`), and the passes
that work on the IR: liveness, renaming, the register allocation's two
passes and the state of the machine a kernel runs on.
"""
