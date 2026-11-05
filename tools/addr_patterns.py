#!/usr/bin/env python3
"""
Address arithmetic patterns in generated RVV kernels (docs/ADDRESSING_PLAN.md:
RVV findings): per region - before the k loop (pre), the loop, the block
after it (last), the epilogue's dispatch, its cases - the integer
instructions, and heuristics, rough by design (straight-line windows,
register names only): a copy then an operation on the copy (mv_then_op), li
then mul (li_mul), an expression computed again with its sources unchanged
(dup_expr), a pointer stepped forward then back (back_and_forth), pointer
steps between its accesses (serial_steps).

    python tools/addr_patterns.py ukrconfig/rvv/k3-x100/dgemm.yaml ...
"""
import re, sys, json, collections
ALU = re.compile(r"^\s*(add|addi|sub|slli|srli|sh[123]add|mul|li|mv|addw|subw)\s+([^#]*)")
MEM = re.compile(r"^\s*(vl\w*|vs\w*|fld|fsd|flw|fsw|ld|sd|lw|sw)\s+([^#]*)")
def regions(lines):
    """label regions: pre (before the k loop), loop, last, dispatch (tries), cases"""
    out, cur = collections.defaultdict(list), "pre"
    for l in lines:
        s = l.strip()
        if s.endswith(":"):
            name = s[:-1]
            if name.endswith("_loop"): cur = "loop"
            elif name.endswith("_last"): cur = "last"
            elif "_done" in name or "_try" in name or "_ok" in name: cur = "dispatch"
            elif "_case" in name: cur = "cases"
            continue
        out[cur].append(s)
    return out
def analyze(text):
    res = {"alu": collections.Counter(), "mv_then_op": 0, "li_mul": 0, "dup_expr": 0, "back_and_forth": 0, "serial_steps": 0}
    for name, body in regions(text.splitlines()).items():
        defs, exprs, last_add = {}, {}, {}
        prev = None
        mem_since = {}
        for i, s in enumerate(body):
            m = ALU.match(s)
            if m:
                op, args = m.group(1), [a.strip() for a in m.group(2).split(",")]
                res["alu"][name] += 1
                rd, srcs = args[0], args[1:]
                # a copy then an operation on the copy (add rd,rs,0 ; op rd,..rd..)
                if prev and prev[0] in ("add", "addi", "mv") and prev[1][0] == rd and (prev[0] == "mv" or prev[1][-1] == "0") and rd in srcs:
                    res["mv_then_op"] += 1
                if op == "mul" and prev and prev[0] == "li" and prev[1][0] in srcs:
                    res["li_mul"] += 1
                key = (op, tuple(srcs))
                if op not in ("li",) and key in exprs and exprs[key] != rd and all(defs.get(r, -1) < exprs.get(("pos",) + key, -1) for r in srcs if not r.lstrip("-").isdigit()):
                    res["dup_expr"] += 1
                if op in ("add", "addi") and rd in srcs and len(srcs) == 2:
                    step = srcs[1] if srcs[0] == rd else srcs[0]
                    if rd in mem_since and mem_since[rd]:
                        res["serial_steps"] += 1
                    last_add[rd] = step
                    mem_since[rd] = False
                if op == "sub" and rd in srcs and rd in last_add:
                    res["back_and_forth"] += 1
                exprs[key] = rd
                exprs[("pos",) + key] = i
                defs[rd] = i
                prev = (op, args)
                continue
            mm = MEM.match(s)
            if mm:
                for r in re.findall(r"\((\w+)\)", mm.group(2)):
                    mem_since[r] = True
            prev = None if not s.startswith(("#", ".")) else prev
    res["alu"] = dict(res["alu"])
    return res
if __name__ == "__main__":
    from ukrgen.injectors.blis.families import configuration, build_gemm
    from ukrgen.injectors.blis.cgen import asm_source
    total = collections.Counter()
    rows = []
    for path in sys.argv[1:]:
        c = configuration.from_files({("gemm", "FP64"): path})
        for fam in c.families:
            built, _ = build_gemm(c.isa, c.name, fam)
            for k in built:
                r = analyze(asm_source(k))
                rows.append((k.symbol, r))
                for key in ("mv_then_op", "li_mul", "dup_expr", "back_and_forth", "serial_steps"):
                    total[key] += r[key]
                for reg, n in r["alu"].items():
                    total["alu_" + reg] += n
    print(len(rows), "kernels:", dict(total))
    json.dump(rows, open("addr_patterns.json", "w"))
