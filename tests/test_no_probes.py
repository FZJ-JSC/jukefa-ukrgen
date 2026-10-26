"""
ukrgen's objects have their attributes as explicit fields with defaults:
nothing in src/ asks hasattr, reads or writes an attribute by a literal
name through getattr or setattr (an attribute access in disguise, a default
standing in for a missing field), writes through __dict__, vars() or
globals(), or past a frozen dataclass with object.__setattr__. getattr and
setattr by a name computed at run time - a program's section, an
operation by an IR step's name - are dispatch and stay.
"""
import ast
import os
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "ukrgen")


def findings(tree, path):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                literal = len(node.args) > 1 and isinstance(node.args[1], ast.Constant)
                if f.id == "hasattr":
                    out.append(f"{path}:{node.lineno}: hasattr")
                elif f.id in ("getattr", "setattr", "delattr") and literal:
                    out.append(f"{path}:{node.lineno}: {f.id} of a literal name ({node.args[1].value})")
            elif isinstance(f, ast.Attribute) and f.attr == "__setattr__":
                out.append(f"{path}:{node.lineno}: __setattr__")
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Subscript):
                    v = t.value
                    if isinstance(v, ast.Attribute) and v.attr == "__dict__":
                        out.append(f"{path}:{node.lineno}: a write through __dict__")
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("vars", "globals"):
                        out.append(f"{path}:{node.lineno}: a write through {v.func.id}()")
    return out


class test_no_probes(unittest.TestCase):
    def test_src(self):
        found = []
        for root, _, files in os.walk(SRC):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    with open(path, encoding="utf-8") as fh:
                        found += findings(ast.parse(fh.read()), os.path.relpath(path, SRC))
        self.assertEqual([], found, "\n".join(found))


if __name__ == "__main__":
    unittest.main()
