"""
Which asmgen generator implements each --isa choice
"""

import importlib

from asmgen.asmblocks.noarch import asmgen

asmgen_modules = {
    'avx128' : 'avx',
    'avx256' : 'avx',
    'avx512' : 'avx',
    'rvv'    : 'rvv',
    'rvv071' : 'rvv071',
    'neon'   : 'neon',
    'sve'    : 'sve',
    'sme'    : 'sme',
}

asmgen_map = {
    'avx128' : 'fma128',
    'avx256' : 'fma256',
    'avx512' : 'avx512',
    'rvv'    : 'rvv',
    'rvv071' : 'rvv071',
    'neon'   : 'neon',
    'sve'    : 'sve',
    'sme'    : 'sme',
}


def make_generator(isa: str) -> asmgen:
    """
    Instantiate the asmgen generator for an ISA

    :param isa: one of the keys of asmgen_map
    :return: the generator, set to emit standalone assembly
    """
    module = importlib.import_module(f"asmgen.asmblocks.{asmgen_modules[isa]}")
    gen = getattr(module, asmgen_map[isa])()
    gen.set_output_inline(yesno=False)
    return gen
