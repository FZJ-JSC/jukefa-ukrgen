"""
Tile operation presets: every STO's tile operation from one name
(--tileop-preset gemm_fma_bc, or a YAML file of the same form).

A preset has a variant per index the vectors run along - the placeholders
that differ with it ($K, $T, $V, $S, ...) - and alternatives: placeholders
with options in order ($CL: C loaded directly, else strided, ...). Each
STO's template expands into its alternatives; the first the ISA offers for
the layouts at hand is the STO's. The first variant whose every STO finds
one is taken - C's contiguous index first, unless --tileop-vectorize names
the index
"""

from __future__ import annotations

import itertools
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = re.compile(r"\$([A-Z]+)")


def names() -> list[str]:
    """
    The presets shipped
    """
    return sorted(f[:-5] for f in os.listdir(HERE) if f.endswith(".yaml"))


def load(name_or_path: str) -> dict:
    """
    A preset by its shorthand, else from a YAML file
    """
    path = os.path.join(HERE, f"{name_or_path}.yaml")
    if not os.path.exists(path):
        path = name_or_path
    if not os.path.exists(path):
        raise ValueError(f"no tile operation preset {name_or_path!r}: one of {', '.join(names())}, "
                         f"or a YAML file")
    with open(path) as f:
        preset = yaml.safe_load(f)
    for key in ("variants", "tileops"):
        if key not in preset:
            raise ValueError(f"tile operation preset {name_or_path}: no {key}")
    return preset


def expand(template: str, variant: dict, alternatives: dict) -> list[str]:
    """
    A template's tile operations in order: the variant's placeholders
    filled in, every combination of the alternatives' options
    """
    used = [n for n in dict.fromkeys(PLACEHOLDER.findall(template)) if n in alternatives]
    out = []
    for combo in itertools.product(*[[str(o) for o in alternatives[n]] for n in used]):
        values = {k: str(v) for k, v in variant.items()}
        values.update(dict(zip(used, combo)))
        out.append(PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), template))
    return out


def select(preset: dict, candidates: dict, given: set, vectorize: str | None = None,
           contiguous: str | None = None, forced: dict | None = None,
           layouts: dict | None = None) -> dict[str, str]:
    """
    Each STO's tile operation: the first variant whose every STO - of the
    ukr's, and not given explicitly - has an alternative the ISA offers
    (candidates: STO -> its tile operations), the first such alternative.
    forced: alternatives fixed to one of their options (--tileop-alternatives
    YS=shuffle: a trans case's store method) - a choice to tune, not the
    first the ISA offers
    """
    preset = dict(preset)
    if forced:
        alternatives = dict(preset.get("alternatives") or {})
        for name, value in forced.items():
            if name not in alternatives:
                raise ValueError(f"no alternative {name} to fix: the preset's are "
                                 f"{', '.join(alternatives) or 'none'}")
            alternatives[name] = [value]
        preset["alternatives"] = alternatives
    variants = list(preset["variants"].items())
    if vectorize is not None:
        variants = [(n, v) for n, v in variants if n == vectorize]
        if not variants:
            raise ValueError(f"the preset has no variant vectorizing {vectorize}: "
                             f"{', '.join(preset['variants'])}")
    elif contiguous is not None and not isinstance(contiguous, dict):
        variants.sort(key=lambda nv: nv[0] != contiguous)
    missing = []
    for name, variant in variants:
        # vectors across C's contiguous index reach C across vectors: not
        # directly - the alternatives after direct
        base_alternatives = dict(preset.get("alternatives") or {})
        def without_direct(alts):
            return {k: [o for o in v if "direct" != str(o)] or v for k, v in alts.items()}
        alternatives = base_alternatives
        if contiguous is not None and not isinstance(contiguous, dict) and name != contiguous:
            alternatives = without_direct(base_alternatives)
        # alternatives of a component's access (components: {XL: X, YS: Y}):
        # direct only where its memory is contiguous along the variant's vectors
        for alt, comp in (preset.get("components") or {}).items():
            index = (layouts or {}).get(comp)
            if alt in alternatives and index is not None and index != name:
                alternatives = dict(alternatives, **without_direct({alt: alternatives[alt]}))
        chosen, lacking = {}, None
        for sto, templates in preset["tileops"].items():
            if isinstance(contiguous, dict):
                # C's storages as branches: the C this STO reaches decides - a
                # copy's alias (store_ab.r: Cr), else C; the loop's mm reaches
                # none (store_ab names only AB, which it stores into C)
                reached = contiguous.get("__by_suffix__", {}).get(sto.split(".", 1)[1]) \
                    if "." in sto else ("C" if "mm" != sto else None)
                across = reached is not None and contiguous.get(reached) not in (None, name)
                alternatives = without_direct(base_alternatives) if across else base_alternatives
            if sto not in candidates or sto in given:
                continue
            options = [o for t in ([templates] if isinstance(templates, str) else templates)
                       for o in expand(t, variant, alternatives)]
            pick = next((o for o in options if o in candidates[sto]), None)
            if pick is None:
                lacking = (sto, options)
                break
            chosen[sto] = pick
        if lacking is None:
            return chosen
        missing.append(f"vectors along {name}: --{lacking[0]}-tileop has none of "
                       f"{lacking[1][:3]}{' ...' if len(lacking[1]) > 3 else ''}")
    raise ValueError("no variant of the preset fits this ISA and these layouts:\n  " +
                     "\n  ".join(missing))
