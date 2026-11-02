"""
A component's storages as branches of one kernel's epilogue (C's in gemm;
any component's): the composition expanded - one component after another
"""

import dataclasses

from .ukr import component_description, case_description, branch_description, block_description

def storage_layout(storage: str, indices) -> list[str]:
    """
    A storage's layout of a two-index component (i, j): row j contiguous,
    col i, any both strided
    """
    i, j = indices[0], indices[1]
    return {"row": [f"{j}:c", f"{i}:s"], "col": [f"{i}:c", f"{j}:s"], "any": [f"{i}:s", f"{j}:s"]}[storage]


def unit_index(storage: str, indices) -> str:
    """The index a storage has contiguous: its condition, the stride along it one element"""
    return indices[1] if "row" == storage else indices[0]


#: each storage's alias letter: a component's alias for it is the component's
#: name and the letter (C's: Cr, Cc, Cg)
SUFFIX = {"row": "r", "col": "c", "any": "g"}
#: C's (its indices m, n) - the names the rest of the flow has known them by
LAYOUTS = {s: storage_layout(s, ("m", "n")) for s in SUFFIX}
ALIASES = {s: f"C{x}" for s, x in SUFFIX.items()}
UNIT = {s: unit_index(s, ("m", "n")) for s in ("row", "col")}


def _fields(o) -> dict:
    """
    A description's fields by name - a dataclass's; nothing for anything
    else (enums, functions, classes it refers to are values, not parts)
    """
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}
    return {}


def _renamed(obj, old: str, new: str):
    """
    An STO with every reference to old naming new instead - a reference's
    name, names in tuples of names (or of tuples of them) - rebuilt with
    dataclasses.replace: the frozen descriptions themselves untouched
    """
    def rename(o):
        if type(o) in (list, tuple):
            return type(o)(rename(x) for x in o)
        if isinstance(o, dict):
            return {k: rename(v) for k, v in o.items()}
        fields = _fields(o)
        if not fields:
            return o
        changes = {}
        for key, value in fields.items():
            if "name" == key and value == old and _is_ref(o):
                value = new
            elif isinstance(value, tuple) and value and all(isinstance(v, str) for v in value):
                value = tuple(new if v == old else v for v in value)
            elif isinstance(value, tuple) and value and all(isinstance(v, tuple) for v in value):
                value = tuple(tuple(new if x == old else x for x in v) for v in value)
            else:
                value = rename(value)
            changes[key] = value
        init = {f.name for f in dataclasses.fields(o) if f.init}
        return dataclasses.replace(o, **{k: v for k, v in changes.items() if k in init})
    return rename(obj)


def _is_ref(o) -> bool:
    """
    A reference to a component in a requirement tree: a name and its indices
    """
    fields = _fields(o)
    return isinstance(fields.get("name"), str) and "indices" in fields


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
        fields = _fields(o)
        if _is_ref(o) and fields["name"] == comp:
            found.append(True)
        for value in fields.values():
            walk(value)
    for key, value in _fields(sto).items():
        if "name" != key:
            walk(value)
    return bool(found)


def storage_branches(base, storages: list[str], comp: str = "C"):
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
    from ..layout import component_indices
    indices = component_indices(base)[comp]
    aliases = {f"{comp}{SUFFIX[s]}": s for s in others}
    # C's copies keep their names (store.r); another component's name its own
    suffix = {s: (SUFFIX[s] if "C" == comp else f"{comp}{SUFFIX[s]}") for s in others}
    branch = base.get_branch()
    # the STOs of the branch's cases touching the component - the epilogue's
    in_cases = {n for case in (branch.cases if branch is not None else ()) for b in case.blocks for n in b.stos}
    epilogue = [s for s in base.get_sto_descriptions() if s.name in in_cases and _touches(s, comp)]

    class expanded(base):
        storage_aliases = {**base.storage_aliases, **aliases}
        storage_bases = {**base.storage_bases, **{a: comp for a in aliases}}
        storage_default = default

        @classmethod
        def get_components(cls):
            comps = list(base.get_components())
            for alias in aliases:
                comps.append(component_description(name=alias, storage=next(
                    c.storage for c in comps if comp == c.name), dt_reference=comp))
            return comps

        @classmethod
        def get_sto_descriptions(cls):
            stos = list(base.get_sto_descriptions())
            for alias, s in aliases.items():
                for sto in epilogue:
                    clone = _renamed(sto, comp, alias)
                    clone = dataclasses.replace(clone, name=f"{sto.name}.{suffix[s]}")
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
                    when = {f"stride({comp},{unit_index(s, indices)})": 1}
                    when.update(case.when)
                    blocks = tuple(dataclasses.replace(b, stos=tuple(
                        renamed.get(n, n) for n in b.stos)) for b in case.blocks)
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
