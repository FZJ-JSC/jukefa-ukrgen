import sys
from specializers import test_signature as t
from stages.test_sto import gemm as gemm_params
from ukrgen.flow.stage_engine import stage_engine

def gemm(isa, **extra):
    regs = {"A-data-regs": "4", "B-data-regs": "4", "C-data-regs": "8"}
    regs.update({"alpha-data-regs": "1", "beta-data-regs": "1"})
    if isa.startswith("rvv"):
        regs["rvv-LMUL"] = "1"
    regs.update(extra)
    for _ in range(4):
        try:
            return t.mm(**gemm_params(isa=isa, **regs))
        except ValueError as e:
            name = str(e).split("Parameter ")[-1].split(" is required")[0]
            if "data-regs" not in name:
                raise
            regs[name] = "1"
    raise RuntimeError("parameters")
