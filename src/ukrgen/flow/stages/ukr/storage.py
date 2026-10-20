"""
C's storages as branches of one kernel's epilogue: the composition expanded
"""

import copy

from .ukr import component_description, case_description, branch_description, block_description

#: each storage's C layout
LAYOUTS = {"row": ["n:c", "m:s"], "col": ["m:c", "n:s"], "any": ["m:s", "n:s"]}
#: the alias component a storage reaches C through (the default's is C)
ALIASES = {"row": "Cr", "col": "Cc", "any": "Cg"}
#: the index a storage has contiguous: its condition, C's stride along it one element
UNIT = {"row": "n", "col": "m"}


def _renamed(obj, old: str, new: str):
    """
    A deep copy of an STO with every reference to old naming new instead
    """
    obj = copy.deepcopy(obj)
    seen = set()
    def walk(o):
        if id(o) in seen or isinstance(o, (str, int, float, bool, type(None))):
            return
        seen.add(id(o))
        if isinstance(o, (list, tuple)):
            for x in o:
                walk(x)
            return
        if isinstance(o, dict):
            for x in o.values():
                walk(x)
            return
        attrs = getattr(o, "__dict__", None)
        if attrs is None:
            return
        for key, value in list(attrs.items()):
            if "name" == key and value == old and _is_ref(o):
                object.__setattr__(o, key, new)
            elif isinstance(value, tuple) and value and all(isinstance(v, str) for v in value):
                object.__setattr__(o, key, tuple(new if v == old else v for v in value))
            elif isinstance(value, tuple) and value and all(isinstance(v, tuple) for v in value):
                object.__setattr__(o, key, tuple(tuple(new if x == old else x for x in v) for v in value))
            else:
                walk(value)
    walk(obj)
    return obj


def _is_ref(o) -> bool:
    """
    A reference to a component in a requirement tree: a name and its indices
    """
    attrs = getattr(o, "__dict__", None) or {}
    return isinstance(attrs.get("name"), str) and "indices" in attrs


def _touches(sto, comp: str) -> bool:
    """
    Whether an STO reads or writes a component - in its requirement or as
    what it stores
    """
    found = []
    seen = set()
    def walk(o):
        if id(o) in seen or isinstance(o, (str, int, float, bool, type(None))):
            return
        seen.add(id(o))
        if isinstance(o, (list, tuple)):
            for x in o:
                if x == comp:
                    found.append(True)
                walk(x)
            return
        if _is_ref(o) and o.__dict__["name"] == comp:
            found.append(True)
        for value in (getattr(o, "__dict__", None) or {}).values():
            walk(value)
    for key, value in sto.__dict__.items():
        if "name" != key:
            walk(value)
    return bool(found)


def storage_branches(base, storages: list[str]):
    """
    The composition with C's storages as branches: the last storage the
    default (C itself, unconditioned), each other an alias component of C
    whose epilogue STOs are copies of C's, its cases first - conditioned on
    C's stride along its contiguous index being one element
    """
    storages = list(storages)
    for s in storages:
        if s not in LAYOUTS:
            raise ValueError(f"--C-storage: {s} not one of {sorted(LAYOUTS)}")
    default, others = storages[-1], storages[:-1]
    if any(s == "any" for s in others):
        raise ValueError("--C-storage: 'any' takes every C - only as the last (default) storage")
    aliases = {ALIASES[s]: s for s in others}
    suffix = {s: s[0] for s in others}
    epilogue = [s for s in base.get_sto_descriptions() if "mm" != s.name and _touches(s, "C")]
    branch = base.get_branch()

    class expanded(base):
        storage_aliases = aliases
        storage_default = default

        @classmethod
        def get_components(cls):
            comps = list(base.get_components())
            for alias in aliases:
                comps.append(component_description(name=alias, storage=next(
                    c.storage for c in comps if "C" == c.name), dt_reference="C"))
            return comps

        @classmethod
        def get_sto_descriptions(cls):
            stos = list(base.get_sto_descriptions())
            for alias, s in aliases.items():
                for sto in epilogue:
                    clone = _renamed(sto, "C", alias)
                    object.__setattr__(clone, "name", f"{sto.name}.{suffix[s]}")
                    stos.append(clone)
            return stos

        @classmethod
        def get_branch(cls):
            if branch is None:
                return None
            cases = []
            for alias, s in aliases.items():
                renamed = {sto.name: f"{sto.name}.{suffix[s]}" for sto in epilogue}
                for case in branch.cases:
                    when = {f"stride(C,{UNIT[s]})": 1}
                    when.update(case.when)
                    blocks = tuple(block_description(**dict(b.__dict__, stos=tuple(
                        renamed.get(n, n) for n in b.stos))) for b in case.blocks)
                    cases.append(case_description(when=when, blocks=blocks))
            cases.extend(branch.cases)
            return branch_description(cases=tuple(cases))

        @classmethod
        def get_blocks(cls):
            out = []
            for b in base.get_blocks():
                out.append(cls.get_branch() if isinstance(b, branch_description) else b)
            return out

    expanded.__name__ = f"{base.__name__}_storages"
    return expanded
