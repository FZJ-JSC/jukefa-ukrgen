"""
The example configurations in ukrconfig/: every one loads - its family files
agree on the ISA, its families parse - and every preset it names exists
"""

import glob
import os
import unittest

from ukrgen.flow import presets
from ukrgen.injectors.blis.families import configuration

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "ukrconfig")


def configs():
    return sorted(os.path.dirname(p) for p in glob.glob(os.path.join(ROOT, "*", "*", "dgemm.yaml"))
                  if "legacy" not in p)


class test_ukrconfig(unittest.TestCase):

    def test_every_config_loads(self):
        found = [os.path.relpath(d, ROOT) for d in configs()]
        self.assertEqual(["avx2/fma_bc_blocks", "avx512/fma_bc_blocks", "avx512/fma_bc_vindex",
                          "neon/fma_bc_lanes", "neon/fma_lane", "rvv/fma_vf", "rvv/fma_vf_m2",
                          "rvv/k1", "rvv/k3-a100",
                          "sme/fopa_bc_vindex", "smesve/fopa_fma_split", "sve/fma_bc_vindex",
                          "sve/fma_blocklane"], found)
        for d in configs():
            files = {(kind, dt): os.path.join(d, f"{ch}{kind}.yaml")
                     for kind in ("gemm", "packm") for ch, dt in (("s", "FP32"), ("d", "FP64"))}
            cfg = configuration.from_files(files)
            kinds = {(f.kind, f.dtypes[0]) for f in cfg.families}
            self.assertEqual(set(files), kinds, d)
            for fam in cfg.families:
                for preset in [fam.params.get("tileop-preset")] + [pp.get("tileop-preset") for pp, _ in fam.parts]:
                    if preset:
                        presets.load(preset)
            defaults = {dt for f in cfg.families if "gemm" == f.kind for dt in f.default}
            self.assertEqual({"FP32", "FP64"}, defaults, d)


if __name__ == "__main__":
    unittest.main()
