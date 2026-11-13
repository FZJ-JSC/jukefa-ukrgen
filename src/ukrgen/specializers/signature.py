"""
Specializing LSC IR for the ISA, and emitting it, through operation signatures.

Every operation the model emits carries the signatures its instruction can
come from. Specializing (IR to IR) makes each operation fit one of them: an
access at an offset no addressing form takes, or offset by run-time strides,
gets an explicit address computation inserted before it. The result is still
LSC IR, for the irmod, MRU and scheduling stages.

Emitting (IR to assembly, codegen's part) picks for each operation the
signature that fits and calls asmgen with its modifiers and operands; asmgen
checks the call against its signatures again.

Neither knows which microkernel it works on: registers, data types, strides
and offsets all come from the program and the composition metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from asmgen.asmblocks.op.opset import opset_modifier
from asmgen.asmblocks.op.constraint import ArgumentDependencyError
from asmgen.callconv.fngen import fngen
from ..support.sig_group import sig_group
from ..support.domains import operand_values
from ..support.data_move import operand_side
from ..support.tiles import widening_ways
from asmgen.asmblocks.noarch import comparison
from asmgen.asmblocks.op import (
    register_type as rgt,
    operand_role as orl,
    operand_type as ot,
    opmem_modifier as memmod,
)
from asmgen.registers import reg_tracker, adt_size
from asmgen.asmblocks.op.constraint import ConstraintDoesNotApplyError

from ..models.lsc.addressing import offpoly
from ..models.lsc.ir import ir_program, ir_block, BASE_REGISTER, START_BLOCK
from ..components.tile import scalar_tile
from ..models.lsc.operations import (
    lsc_load, lsc_store, lsc_move, lsc_zero, lsc_transformation, lsc_addr_compute, lsc_loop,
    lsc_value_op)
from ..models.lsc.index import lsc_reg_index
from ..models.lsc.reg import lsc_reg_type
from ..models.lsc.offset_polynomial import offset_polynomial as offpoly


class specialization_error(Exception):
    """
    An operation fits none of its signatures as specialized
    """


def _sigs(groups) -> list:
    """
    The signatures in a signature group, or in a list of groups
    """
    if groups is None:
        return []
    if isinstance(groups, list):
        return [s for g in groups for s in _sigs(g)]
    if isinstance(groups, sig_group):
        return list(groups.sigs)
    # a signature itself
    return [groups]


def _masked(sig) -> bool:
    return any(orl.MASK == o.orole for o in sig.operands.values())


def _offset_forms(sig) -> str | None:
    """
    "plain" for a signature without an offset, "ioffset" for one taking an
    immediate offset, None for other addressing forms
    """
    # a structure load or store is addressed like a plain one
    mods = {m.name for m in sig.modifiers} - {"MASK", "STRUCT"}
    if not mods or ({"GSTRIDE"} == mods and "streg" in sig.operands) \
            or ({"VINDEX"} == mods and "vidxreg" in sig.operands):
        # a strided access or a gather is addressed plainly; its stride or
        # index vector is bound when emitted
        return "plain"
    if {"IOFFSET"} == mods and "ioffset" in sig.operands:
        return "ioffset"
    return None


def _accepts(sig, name: str, value) -> bool:
    """
    Whether a signature's operand takes a value: each of its constraints is
    asked, a ValueError meaning no; constraints that don't apply are skipped
    """
    shape = sig.operands.get(name)
    if shape is None:
        return False
    for constraint in shape.value_constraints:
        try:
            constraint(name, set(sig.modifiers), value, {})
        except (ConstraintDoesNotApplyError, ArgumentDependencyError):
            # doesn't apply, or depends on another operand: for when every
            # operand is known
            continue
        except ValueError:
            return False
    return True


def _all_true(ctx, rt=None):
    """
    The ISA's all-true governing predicate for masked signatures, set up by
    its isa_setup() - and reserved and aliased in the register tracker, when
    one is given. Only where predication is explicit (SVE, SME): with RVV's
    implicit vector length a mask is something else, v0. None where there is
    none.
    """
    setup = ctx.gen.isa_setup()
    if "EXPLICIT" != setup.predication().name:
        return None
    return setup.all_true_predicate(rt=rt, dt=None)


def _usable(ctx, sig) -> bool:
    """
    Unmasked signatures always; masked ones where the ISA sets up an all-true
    predicate to govern them, or where the mask is one the instruction clears
    (its signature's clobber_list) and the generator can set it all-true again
    before each use - AVX gathers and scatters
    """
    if not _masked(sig) or _all_true(ctx) is not None:
        return True
    masks = [n for n, o in sig.operands.items() if orl.MASK == o.orole]
    clobbered = set(sig.clobber_list or [])
    # re-set before each where the generator sets a mask all-true at all
    return set(masks) <= clobbered and bool(ctx.gen.set.forms(modifiers={opset_modifier.CONSTMASK}))


def _vl_form(sig) -> bool:
    """
    A load or store signature taking an offset in vector lengths: [x, #n, MUL VL]
    """
    return {m.name for m in sig.modifiers} - {"MASK"} == {"VOFFSET"} and "voffset" in sig.operands


def slice_placements(order: list, plan: dict, walk_of: dict) -> tuple[dict, dict]:
    """
    A loop over slices' moves, its walk plan's registers walking (no column
    pointers): each access of an iteration, from the registers' homes in the
    order emitted (the block's; preloading, the first copy's loads first), at
    its plan register - moved there first, or by the rest alone with the
    vector lengths an immediate where a signature takes them ([x, #n, MUL
    VL]) - and where the order leaves each register. Every copy (or the
    iteration) ends at the next home, so an access is placed alike wherever
    it's emitted
    :param order: the iteration's loads and stores in the order emitted
    :return: (placed, end): placed id(access) -> (plan key, the move before
             it or None, vector lengths an immediate or None); end plan key ->
             its register's offset from home after the order
    """
    current = {key: offpoly.const(0) for key in plan}
    placed = {}
    for b in order:
        w = b.properties.get("walk", 0)
        key = walk_of[w]
        target = plan[key]["walks"][w]
        rest = dict((target - current[key]).terms)
        if not rest:
            placed[id(b)] = (key, None, None)
            continue
        vectors = rest.get(("VL",))
        if vectors and any(_vl_form(sig) and _accepts(sig, "voffset", vectors) for sig in _sigs(b.sigs)):
            # the register moved by the rest alone (another column), the vector
            # lengths an immediate
            others = {f: c for f, c in rest.items() if ("VL",) != f}
            move = offpoly._make(others) if others else None
            if move is not None:
                current[key] = current[key] + move
            placed[id(b)] = (key, move, vectors)
            continue
        placed[id(b)] = (key, target - current[key], None)
        current[key] = target
    return placed, current


def slice_walkers(op, program, component_dts) -> list[dict]:
    """
    A loop over slices without a walk plan (a run-time count: a masked tile's
    rows): a walking pointer a walk - shared by walks of one component from
    the same element by the same step (a tile's load and store of C) - and a
    step register a step and element size
    :return: per walk, in order: its component and register (comp, reg), its
             start in elements, its step's terms, the step's key (a step
             register shared) and the start's (a walker shared)
    """
    out = []
    for walk in op.walks:
        anchor = walk.anchor
        wcomp, wreg = anchor.indices[0].component, anchor.indices[0].indices[0]
        elements = program.offsets.elements_offset(anchor.offset, program.strides.get(wcomp, {}))
        terms = dict(walk.step.terms)
        key = (tuple(sorted(terms.items())), adt_size(component_dts[wcomp]))
        out.append({"comp": wcomp, "reg": wreg, "elements": elements, "terms": terms, "key": key,
                    "start": (wcomp, str(elements), key)})
    return out


def slice_columns(op, plan: dict, loop_gregs) -> tuple:
    """
    A loop over slices' access columns: within the general registers allowed
    (--loop-gregs), a pointer per access column - an offset's part beside
    vector lengths; tiles a vector length apart share one, the rest an
    immediate - set before the loop, stepped once an iteration: no moves
    between tiles. The first column of a plan register is that register
    :return: (columns, pointers, column_of): columns (plan key, column text)
             -> (key, column); pointers the same keys -> the column (None:
             the plan register itself), empty without room; column_of a walk
             -> (key, column text, vector lengths an immediate or None)
    """
    columns, pointers, column_of = {}, {}, {}
    accesses = {}
    for b in op.block:
        if isinstance(b, (lsc_load, lsc_store)):
            accesses.setdefault(b.properties.get("walk", 0), []).append(b)
    for key, p in plan.items():
        for w, offset in p["walks"].items():
            vectors = dict(offset.terms).get(("VL",))
            # the vector lengths an immediate only where every access of the
            # walk takes them
            folds = vectors and all(any(_vl_form(sig) and _accepts(sig, "voffset", vectors)
                                        for sig in _sigs(b.sigs))
                                    for b in accesses.get(w, []))
            column = offpoly._make({f: c for f, c in dict(offset.terms).items()
                                if not (folds and ("VL",) == f)})
            column_of[w] = (key, str(column), dict(offset.terms).get(("VL",)) if folds else None)
            columns.setdefault((key, str(column)), (key, column))
    extra = len(columns) - len(plan)
    if loop_gregs is None or 2 + extra <= loop_gregs:
        for (key, name), (_, column) in columns.items():
            pointers[(key, name)] = None if not dict(column.terms) else column
    return columns, pointers, column_of


def _takes(sig, immediate: int, limit: int | None = None) -> bool:
    """
    Whether a load or store signature takes an access at this immediate offset
    - within limit bytes, either sign, where one is given (--max-imm-offset)
    """
    form = _offset_forms(sig)
    if "plain" == form:
        return 0 == immediate
    if "ioffset" == form:
        if limit is not None and abs(immediate) > limit:
            return False
        return _accepts(sig, "ioffset", immediate)
    return False


#: stride pointers kept per component and base where general registers are
#: many (AArch64, RISC-V: 31); columns beyond them share one walking pointer
#: stride pointers where a component asks for none of its own: none - the
#: pattern's registers walk to the columns (None: the ISA's old default,
#: MAX_STRIDE_POINTERS, FEW_ on x86)
STRIDE_POINTERS_DEFAULT = 0
MAX_STRIDE_POINTERS = 4
#: ... and where they are few (x86: 16)
FEW_STRIDE_POINTERS = 2


def _tail_runs(block) -> bool:
    """
    Whether a loop's tail runs - as the emitter counts it (loop_counts): a
    loop stepping one element (or one vector length) an iteration leaves
    none over, its tail not emitted; else the tail a counted loop over what's
    left, repeating (packm's, once a step left). A step of a fixed vector
    length's lanes isn't told here: taken to leave some
    """
    if block.loop_index is None or block.step is None:
        return False
    terms = {f: int(c) for f, c in dict(block.step.terms).items() if c}
    return terms not in ({(): 1}, {("VL",): 1})


class _sections:
    """A block's sections as given - the rest empty (what's after a section)"""

    def __init__(self, block, names):
        for name in ("prologue", "body", "epilogue", "tail", "subtail"):
            setattr(self, name, getattr(block, name) if name in names else [])


def _components_accessed(blocks) -> set:
    """
    The components blocks access through an address register - a loop's body
    too: those whose registers' positions matter after a block
    """
    out = set()

    def visit(ops):
        for op in ops or []:
            if isinstance(op, lsc_loop):
                visit(op.block)
            for p, idx in enumerate(op.indices):
                if p < len(op.reg_types or []) and lsc_reg_type.address == op.reg_types[p]:
                    out.add(idx.component)
    for block in blocks:
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            visit(getattr(block, section))
    return out


class signature_specializer:
    """
    Adapts one part's IR program to the ISA, in place: after it, every
    operation fits one of its signatures as it stands.

    - an access offset by run-time strides goes through a stride pointer: an
      address register computed once per section from the access's address
      register and the strides
    - an access at a constant offset no signature takes (NEON's ld1r has no
      immediate form) goes through a scratch address register set right before
      it - which an irmod can fuse into a post-increment form

    :raises specialization_error: for what is not specialized yet, e.g. the
                                  governing predicates of SVE and RVV
    """

    def walk_to(self, comp: str, reg: int, strided: dict, inserted: list, tile) -> None:
        """
        An access's address register walked to its offset at run-time strides
        - from whichever of the component's registers is the fewest strides
        away (registers taken in turn leapfrog: one add of a stride each) - not
        a stride pointer: along the loop's own index (k:s), or where the
        component has none (--COMP-stride-pointers 0)
        """
        target = self.positions[(comp, reg)] + offpoly._make(strided)
        def strides_away(r):
            # a stride, or a vector length of one (a strided access's next
            # vector: VL*stride(C,m), the vl_stride setup value) - an add each
            d = dict((target - self.positions[(comp, r)]).terms)
            if not all(self.walkable(comp, f) for f in d if f):
                return float("inf")
            return sum(abs(c) for f, c in d.items() if f)
        bases = [r for (c, r) in self.program.addr_setup if c == comp and (c, r) in self.positions]
        # another register costs its strides and the copy (or the step from it);
        # a tie the access's own: its steps fuse into post-increments (ldinc),
        # a copy doesn't
        source = min(bases or [reg], key=lambda r: (strides_away(r) + (0 if r == reg else 1), r != reg))
        move = target - self.positions[(comp, source)]
        if dict(move.terms) or source != reg:
            # (source first, then the register set: dest = src + delta)
            inserted.append(lsc_addr_compute(comp, source, reg, move, tile))
            walked = self.walked_by
            walked[(comp, reg)] = walked.get((comp, reg), offpoly.const(0)) + \
                (target - self.positions[(comp, reg)])
            self.walked_by = walked
            self.positions[(comp, reg)] = target
            # stride pointers computed from it were placed from where it was:
            # computed again, from here, on their next use
            self.pointers = {k for k in self.pointers if k[:2] != (comp, reg) or "walk" == k[2]}

    def indexed_lane(self, op, comp: str, strided: dict, usable: list) -> tuple | None:
        """
        A lane access's own stride and count where an index register takes
        them - the count a scale of the operation's own index forms (x86:
        1, 2, 4, 8) and the access a plain form the index extends; None where
        not (lane 0, lane 3, an ISA without the forms)
        """
        singles = [k[0] for k in strided if 1 == len(k)]
        index = op.properties.get("stride_index")
        named = f"stride({comp},{index})" if index is not None else None
        factor = named if named in singles else (singles[0] if 1 == len(strided) and 1 == len(singles) else None)
        if factor is None:
            return None
        count = strided[(factor,)]
        dt = self.ctx.component_dts[comp]
        operation = getattr(self.ctx.gen, op.step.op, None)      # IR pseudo-operations have none
        full = operation.get_signatures() if operation is not None else []
        # the index forms of the lane's own forms (vmovhpd's, an extract's -
        # not a whole vector's store): its modifiers and the scaled offset
        mods = lambda sig: {m.name for m in sig.modifiers}
        own = [mods(u) - {"IOFFSET"} for u in usable]
        scales = {s.structural_params.get("scale_factor") for s in full
                  if "SCALEOFFSET" in mods(s) and (mods(s) - {"SCALEOFFSET", "GOFFSET", "IOFFSET"}) in own
                  and ("adreg" not in s.operands or s.operands["adreg"].dt == dt)}
        return (factor, count) if count in scales else None

    def plan_jumps(self, ops) -> dict:
        """
        --ldinc-imm-offsets last: runs of consecutive accesses one way (loads,
        stores: their registers apart) to one column of a component that walks
        and post-increments - their offsets alike but for the constant (a
        column's rows) - each run's first access and how far its last row is
        :return: id(first access) -> elements to the last row
        """
        out, runs = {}, {}
        for op in ops:
            if not isinstance(op, (lsc_load, lsc_store)) or op.offset is None:
                continue
            comp = op.indices[0].component
            if 0 != self.stride_pointers(comp) or not any(
                    {"POSTINC"} == {m.name for m in s.modifiers} - {"MASK", "STRUCT"} for s in _sigs(op.sigs)):
                continue
            terms = dict(self.program.offsets.elements_offset(op.offset, self.program.strides.get(comp, {})).terms)
            const = terms.pop((), 0)
            key = (comp, isinstance(op, lsc_load))
            column = tuple(sorted(terms.items()))
            run = runs.get(key)
            if run is not None and run["column"] == column and const > run["last"]:
                run["last"] = const
                out[id(run["first"])] = const - run["base"]
                continue
            runs[key] = {"column": column, "first": op, "base": const, "last": const}
        return out

    def register_offset_form(self, op, comp: str) -> bool:
        """
        Whether the operation has a register offset form at the access's type
        (SVE's [x0, x1, lsl #3]) - the operation's own signatures: the access's
        solved forms are its plain and immediate ones
        """
        dt = self.ctx.component_dts[comp]
        operation = getattr(self.ctx.gen, op.step.op, None)      # IR pseudo-operations have none
        full = operation.get_signatures() if operation is not None else []
        return any({"GOFFSET"} == {m.name for m in s.modifiers} - {"MASK"}
                   and ("adreg" not in s.operands or s.operands["adreg"].dt == dt) for s in full)

    @staticmethod
    def walkable(comp: str, factors: tuple) -> bool:
        """
        A term an address register walks by, an add of a register each: one of
        the component's strides, or the vector length times one (a strided
        access's next vector - C's rows at a run-time stride)
        """
        if 1 == len(factors):
            return factors[0].startswith(f"stride({comp},")
        return 2 == len(factors) and "VL" == factors[0] and factors[1].startswith(f"stride({comp},")

    def stride_pointers(self, comp: str | None = None) -> int:
        """
        Stride pointers kept per component and base: the component's own
        (--COMP-stride-pointers), else fewer where the ISA has few general
        registers - x86's 16 hold A's and B's pointers, the loop's counter and
        the parameters too
        """
        if comp in self.program.stride_pointers:
            return self.program.stride_pointers[comp]
        # a storage alias of C (Cc, Cr - a storage case's C) takes C's own
        # setting where it has none: stride-pointers {C: 0} walks every case
        base = self.ctx.composition.storage_bases.get(comp)
        if base is not None and base in self.program.stride_pointers:
            return self.program.stride_pointers[base]
        if STRIDE_POINTERS_DEFAULT is not None:
            return STRIDE_POINTERS_DEFAULT
        if self._stride_pointers is None:
            # the general registers the tracker allocates, reserved ones included
            gregs = self.ctx.gen.get_reg_tracker().available_reg_count("greg")
            self._stride_pointers = MAX_STRIDE_POINTERS if gregs > 16 else FEW_STRIDE_POINTERS
        return self._stride_pointers

    def __init__(self, ctx, program: ir_program):
        #: how an access the register walks reaches an immediate offset (--ldinc-
        #: imm-offsets): all - by the immediate (ldr q's [x0, #16]); none - the
        #: register walks to it (where the access's forms post-increment)
        self.imm_offsets = "all"
        #: --ldinc-imm-offsets last: id(first access) -> elements to its last row
        self.jumps = {}
        #: --loop-gregs (the emit stage's too): a loop over slices' pointers
        self.loop_gregs = None
        # what's been placed and walked, the stride pointers made on first use
        self.placed = set()
        self.walked_by = {}
        #: the state the caller guarantees (--assume-state)
        self.assumed = {}
        self._stride_pointers = None
        #: adapting a case's last block: its last section's registers are read
        #: by nothing after it (the kernel returns; the next case starts afresh)
        self.final_block = False
        #: the components blocks after the one adapted access (their address
        #: registers): a block's last section moves no other's back
        self.accessed_later = None
        #: the loop index of the block being adapted (None: straight-line)
        self.loop_index = None
        self.ctx = ctx
        self.program = program
        self.positions: dict[tuple[str, int], offpoly] = {
            (comp, reg): program.offsets.elements_offset(oid, program.strides.get(comp, {}))
            for (comp, reg), oid in program.addr_setup.items()}
        self.next_reg: dict[str, int] = {}
        for comp, reg in self.positions:
            self.next_reg[comp] = max(self.next_reg.get(comp, 0), reg + 1)
        self.pointer_regs: dict[tuple, int] = {}
        self.pointers: set[tuple] = set()
        # walking pointers for lane-by-lane strided accesses: register, and
        # the stride multiple it is at in this section
        self.walk_regs: dict[tuple, int] = {}
        self.walking: dict[tuple, int] = {}
        self.scratch: dict[str, int] = {}

    def new_reg(self, comp: str, role: str = "address") -> int:
        """
        A general register of a component's, numbered here so that the IR names
        it before the emitter gives it a machine one, and recorded with what it
        holds - the frame the analysis has to see
        :param comp: the component whose address register it is
        :param role: what it holds - a stride pointer, a walker, a scratch
                     address, a column's pointer, a walker's start
        :return: its number under that component
        """
        # numbered per block (start_blocks resets the counter): a block's
        # registers reuse the numbers of the blocks before it, as the emitter's
        # aregs share them across the program
        reg = self.next_reg.get(comp, 0)
        self.next_reg[comp] = reg + 1
        self.program.address_registers[(comp, reg)] = role
        return reg

    def adapt_access(self, op) -> list:
        comp, reg = op.indices[0].component, op.indices[0].indices[0]
        assigned = reg
        db, strides = self.program.offsets, self.program.strides.get(comp, {})
        # its forms (forms(): the usable ones, whatever its address)
        if "usable" not in op.properties:
            self.forms(op)
        usable = op.properties["usable"]
        rel = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
        vl = rel.pop(("VL",), 0)
        inserted = []

        strided = {f: c for f, c in rel.items() if f}
        # a component strided along the loop's own index (k:s - a gemmsup's
        # unpacked A, B): its registers walk - every strided offset of it (a
        # general stride's columns too), the access's register moved there from
        # whichever of the component's registers is the fewest strides away:
        # forward a stride (registers taken in turn leapfrog: one add of its
        # register), or a row on (a general stride: rs - (n - R) cs) - not a
        # stride pointer per offset and register, which the walking bases
        # would leave behind
        def single(f):
            return 1 == len(f) and f[0].startswith(f"stride({comp},")
        # only where the loop's own index is strided at run time (k:s): a
        # component contiguous along it (packm's trans X - n:c, m:s) keeps its
        # stride pointers - independent chains, not one serial walk
        along = f"stride({comp},{self.loop_index})" if self.loop_index is not None else None
        walking = along is not None and any(f and along == f[0] for f, _ in strides.get(self.loop_index, offpoly.const(0)).terms) \
            and strided and all(single(f) for f in strided) and "lane" not in op.properties
        if walking:
            self.walk_to(comp, reg, strided, inserted, scalar_tile)
            rel = {f: c for f, c in rel.items() if not f}
            strided = {}
        if strided and "lane" in op.properties and 0 == self.stride_pointers(comp) \
                and all(self.walkable(comp, f) for f in strided):
            # lane by lane with no stride pointers: each lane's address walked
            # to like any other access's, from the register nearest it - the
            # pattern's registers (phase+rotate) rotating through the lanes,
            # no lane walker of their own (NEON's vn C, across vectors). Where
            # the ISA scales an index register (x86: 1, 2, 4, 8 - lane 1, 2,
            # 4 of a column), the register walks to the column only and the
            # lane is its stride through the index: no walk lane by lane, no
            # rewind to the next column
            lane = self.indexed_lane(op, comp, strided, usable)
            if lane is not None:
                rest = {f: c for f, c in strided.items() if f != (lane[0],)}
                if rest:
                    self.walk_to(comp, reg, rest, inserted, scalar_tile)
                op.properties["scaled_index"] = lane
            else:
                self.walk_to(comp, reg, strided, inserted, scalar_tile)
            rel = {f: c for f, c in rel.items() if not f}
            strided = {}
        if strided and any(c < 0 for c in strided.values()) \
                and all(self.walkable(comp, f) for f in strided) and "lane" not in op.properties:
            # the access behind its register - which walked past its column (a
            # column's second vector after the last column's first), or which
            # phase+rotate gave a later column first: walked there, from the
            # register nearest it; stride pointers only ever reach forward
            self.walk_to(comp, reg, strided, inserted, scalar_tile)
            rel = {f: c for f, c in rel.items() if not f}
            strided = {}
        if strided:
            for factors, count in strided.items():
                vl_times_stride = 2 == len(factors) and "VL" == factors[0] \
                    and factors[1].startswith("stride(")
                if not (vl_times_stride or (1 == len(factors) and factors[0].startswith("stride("))) \
                        or count < 0:
                    raise specialization_error(
                        f"{op.rsln} access to {db[op.offset]} is {offpoly._make(rel)} elements from "
                        f"its address register, which is not specialized yet")
            # lane by lane along a stride: the lane's own stride walks one
            # pointer per base and stride, stepping by the stride and
            # restarting from its base when the base changes or an access
            # goes back; the other factors (a column) give that base, as a
            # stride pointer. A pointer per lane would take a register each
            lane_factor = None
            if "lane" in op.properties:
                singles = [k[0] for k in strided if 1 == len(k)]
                index = op.properties.get("stride_index")
                named = f"stride({comp},{index})" if index is not None else None
                if named in singles:
                    lane_factor = named
                elif 1 == len(strided) and 1 == len(singles):
                    lane_factor = singles[0]
            lane_count = strided.pop((lane_factor,)) if lane_factor is not None else None
            # a stride times a count the ISA scales an index register by (x86:
            # 1, 2, 4, 8): the base pointer and the stride's register as
            # index - no pointer of its own (docs/REG_USE_OPTIMIZATION.md, 2c)
            if lane_factor is None and not vl and 1 == len(strided):
                (factors, count), = strided.items()
                # the ISA's own forms - the operation's signatures, chosen for
                # its resolution, hold none with a register offset
                dt = self.ctx.component_dts[comp]
                operation = getattr(self.ctx.gen, op.step.op, None)      # IR pseudo-operations have none
                full = operation.get_signatures() if operation is not None else []
                scales = {s.structural_params.get("scale_factor") for s in full
                          if "SCALEOFFSET" in {m.name for m in s.modifiers}
                          and ("adreg" not in s.operands or s.operands["adreg"].dt == dt)}
                # the access's own plain or immediate form, which the index
                # extends (a gather or scatter has none)
                plain = any(not ({m.name for m in s.modifiers} - {"IOFFSET", "MASK", "STRUCT"})
                            for s in usable)
                if 1 == len(factors) and count in scales and plain:
                    op.properties["scaled_index"] = (factors[0], count)
                    strided = {}
            if strided and 0 == self.stride_pointers(comp) and all(self.walkable(comp, f) for f in strided) \
                    and "lane" not in op.properties:
                # no stride pointers for this component (--COMP-stride-pointers
                # 0: its pattern's registers - phase+rotate's - in their place):
                # its register walks there - to the access exactly where its
                # forms post-increment by a register (NEON's ld1/st1): an
                # access at its register takes its walk's next step (ldinc),
                # one with an immediate (ldr q's) can't
                exact = rel.get((), 0) and any(
                    {"POSTINC"} == {m.name for m in s.modifiers} - {"MASK", "STRUCT"} and "increg" in s.operands
                    for s in _sigs(op.sigs))
                one = list(strided.items())
                # the whole offset from the register, as the emitter computes it:
                # one stride, nothing else (not a vector length - [x0, x_cs,
                # lsl #3] takes no immediate)
                whole = dict((self.program.offsets.elements_offset(op.offset, self.program.strides.get(comp, {}))
                              - self.positions[(comp, reg)]).terms)
                if self.ctx.gen.is_vla and 1 == len(one) and 1 == len(one[0][0]) and 1 == one[0][1] \
                        and {f: c for f, c in whole.items() if c} == {one[0][0]: 1} \
                        and any(not ({m.name for m in sg.modifiers} - {"MASK"}) for sg in _sigs(op.sigs)) \
                        and self.register_offset_form(op, comp):
                    # (a contiguous access, its plain form the register offset
                    # extends - not a scatter's vector index)
                    # SVE: the next column through the register offset form
                    # ([x0, x_cs, lsl #3]: the stride in elements the index) -
                    # the register stays, reaching two columns a step
                    op.properties["goffset"] = one[0][0][0]
                    rel = {}
                else:
                    self.walk_to(comp, reg, {**strided, (): rel[()]} if exact else strided, inserted, scalar_tile)
                    rel = {} if exact else {f: c for f, c in rel.items() if not f}
                strided = {}
            key = (comp, reg, tuple(sorted(strided.items())))
            columns = [k for k in self.pointer_regs if k[:2] == (comp, reg) and "walk" != k[2]]
            if strided and key not in self.pointer_regs and len(columns) >= self.stride_pointers(comp):
                # more columns than pointers kept for them (general registers
                # are few - RISC-V's C of 14 columns): one pointer walks
                # between the rest, moved by the difference, computed from
                # the base where this section hasn't placed it
                key = (comp, reg, "walk")
                if key not in self.pointer_regs:
                    self.pointer_regs[key] = self.new_reg(comp, "walking pointer")
                ptr = self.pointer_regs[key]
                target = self.positions[(comp, reg)] + offpoly._make(strided)
                if key in self.pointers:
                    move = target - self.positions[(comp, ptr)]
                    if dict(move.terms):
                        inserted.append(lsc_addr_compute(comp, ptr, ptr, move, scalar_tile))
                else:
                    inserted.append(lsc_addr_compute(comp, reg, ptr, offpoly._make(strided), scalar_tile))
                    self.pointers.add(key)
                self.positions[(comp, ptr)] = target
            else:
                if strided and key not in self.pointer_regs:
                    self.pointer_regs[key] = self.new_reg(comp, "pointer")
                ptr = self.pointer_regs[key] if strided else reg
            if strided and key not in self.pointers:
                delta = offpoly._make(strided)
                inserted.append(lsc_addr_compute(comp, reg, ptr, delta, scalar_tile))
                self.positions[(comp, ptr)] = self.positions[(comp, reg)] + delta
                self.pointers.add(key)
            base = reg
            reg = ptr
            if lane_factor is not None:
                wkey = (comp, base, lane_factor)
                if wkey not in self.walk_regs:
                    self.walk_regs[wkey] = self.new_reg(comp, "walker")
                walker = self.walk_regs[wkey]
                state = self.walking.get(wkey)
                # restarted where its base is another register, or the same one
                # moved since (a walking pointer's next row)
                if state is None or state[0] != ptr or lane_count < state[1] \
                        or state[2] != self.positions[(comp, ptr)]:
                    step = offpoly.factor(lane_factor, lane_count)
                    inserted.append(lsc_addr_compute(comp, ptr, walker, step, scalar_tile))
                    self.positions[(comp, walker)] = self.positions[(comp, ptr)] + step
                elif lane_count > state[1]:
                    step = offpoly.factor(lane_factor, lane_count - state[1])
                    inserted.append(lsc_addr_compute(comp, walker, walker, step, scalar_tile))
                    self.positions[(comp, walker)] = self.positions[(comp, walker)] + step
                self.walking[wkey] = (ptr, lane_count, self.positions[(comp, ptr)])
                reg = walker

        if reg != assigned:
            # the access goes through a column or walking pointer: what is
            # left is from where that pointer stands - its walks included
            now = dict((db.elements_offset(op.offset, strides) - self.positions[(comp, reg)]).terms)
            if not [f for f in now if f and ("VL",) != f]:
                vl = now.pop(("VL",), 0)
                rel = now
        const = rel.get((), 0)
        immediate = const * adt_size(self.ctx.component_dts[comp])

        # Offsets in vector lengths: [x, #n, MUL VL] where a signature takes n
        # and nothing else is added; otherwise the address register moves by
        # them first, along with any constant
        if vl:
            if any(_vl_form(s) and _accepts(s, "voffset", vl) for s in usable) and not const:
                op.indices[0] = lsc_reg_index(comp, [reg])
                return inserted + [op]
            if comp not in self.scratch:
                self.scratch[comp] = self.new_reg(comp, "scratch address")
            scratch = self.scratch[comp]
            target = self.positions[(comp, reg)] + offpoly.const(const) + offpoly.factor("VL", vl)
            vl_taken = lambda n: any(_vl_form(s) and _accepts(s, "voffset", n) for s in usable)
            # the scratch where this section placed it: what is left, if a
            # signature takes it - vector lengths, or a constant
            if (comp, scratch) in self.placed:
                rest = dict((target - self.positions[(comp, scratch)]).terms)
                rvl, rconst = rest.pop(("VL",), 0), rest.pop((), 0)
                if not rest and ((not rconst and (not rvl or vl_taken(rvl))) or
                                 (not rvl and any(_takes(s, rconst * adt_size(
                                     self.ctx.component_dts[comp]),
                                     self.max_imm_offset) for s in usable))):
                    op.indices[0] = lsc_reg_index(comp, [scratch])
                    return inserted + [op]
            # placed at the constant only where a signature takes the vector
            # lengths: the next vectors past it need nothing more
            delta = offpoly.const(const) if vl_taken(vl) else offpoly.const(const) + offpoly.factor("VL", vl)
            here = self.positions[(comp, reg)] + delta
            if (comp, scratch) in self.placed and \
                    not [f for f in dict((here - self.positions[(comp, scratch)]).terms) if f and ("VL",) != f]:
                # already placed this section: moved by the difference alone
                move = here - self.positions[(comp, scratch)]
                inserted.append(lsc_addr_compute(comp, scratch, scratch, move, scalar_tile))
            else:
                inserted.append(lsc_addr_compute(comp, reg, scratch, delta, scalar_tile))
            self.positions[(comp, scratch)] = here
            self.placed = self.placed | {(comp, scratch)}
            op.indices[0] = lsc_reg_index(comp, [scratch])
            # at its register exactly: a post-increment can be its (ldinc)
            op.properties["at_register"] = True
            return inserted + [op]

        # --ldinc-imm-offsets none: where this component walks (no stride pointers) and
        # the access's own forms post-increment (NEON's ld1/st1), its register
        # walks to it rather than reach it by an immediate - each row's step a
        # post-increment by the transfer (ldinc), the column's change an offset
        walk_imm = bool(immediate) and "none" == self.imm_offsets and 0 == self.stride_pointers(comp) \
            and any({"POSTINC"} == {m.name for m in s.modifiers} - {"MASK", "STRUCT"} for s in _sigs(op.sigs))
        if walk_imm or not any(_takes(s, immediate, self.max_imm_offset) for s in usable):
            if not any(_takes(s, 0) for s in usable):
                raise specialization_error(
                    f"no {op.step.op} signature for {db[op.offset]} takes a plain address")
            # the access's own register walks to it: later accesses resolved
            # from there (offsets until the limit, then a bump, as v1 did); the
            # section moves it back at its end
            inserted.append(lsc_addr_compute(comp, reg, reg, offpoly.const(const), scalar_tile))
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + offpoly.const(const)
            walked = self.walked_by
            walked[(comp, reg)] = walked.get((comp, reg), offpoly.const(0)) + offpoly.const(const)
            self.walked_by = walked
            immediate = 0
        op.indices[0] = lsc_reg_index(comp, [reg])
        # at its register exactly (no immediate): only such an access post-
        # increments (ld1/st1 take no offset; ldr q's immediate can't) - ldinc
        op.properties["at_register"] = 0 == immediate
        jump = self.jumps.get(id(op)) if 0 == immediate else None
        if jump:
            # --ldinc-imm-offsets last: the register on to the column's last row
            # right after its first (ldinc: ldr q0, [x0], #jump) - the rows
            # between by negative immediates, the last at the register, the
            # next column's walk from there (the remainder an offset)
            step = lsc_addr_compute(comp, reg, reg, offpoly.const(jump), scalar_tile)
            step.properties = {"jump": True}
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + offpoly.const(jump)
            walked = self.walked_by
            walked[(comp, reg)] = walked.get((comp, reg), offpoly.const(0)) + offpoly.const(jump)
            self.walked_by = walked
            return inserted + [op, step]
        return inserted + [op]

    def adapt_slices(self, op) -> list:
        """
        A loop over a tile's slices walks the address registers the model's
        plan gave its accesses - C's loads one, its stores another - not
        pointers of its own: each register starts at the first slice of the
        first walk on it in the block (its home), every walk on it an offset
        from there - another tile's first slice - and after the loop an
        address computation steps it back by its walk, home: code around the
        loop - an enclosing loop's advance, its last iteration's - finds it
        there whatever iteration it is. The plan is the emitter's too
        """
        if op.info.get("count"):
            if "slice_walks" in op.info:
                return [op]
            # a run-time count (a masked tile's rows): its walks' pointers
            # registers of the loop's own, set up before it and stepped in the
            # body - the emitter allocating and emitting them (slice_walks)
            walks = slice_walkers(op, self.program, self.ctx.component_dts)
            setups, op.block, regs = self.slice_walks(op, walks)
            for o in setups:
                o.properties["slice_setup"] = True
            op.info["slice_walks"] = regs
            op.refresh()
            return setups + [op]
        db = self.program.offsets
        order = []
        for b in op.block:
            if isinstance(b, (lsc_load, lsc_store)):
                w = b.properties.get("walk", 0)
                if w not in order:
                    order.append(w)
        order += [w for w in range(len(op.walks)) if w not in order]
        plan = {}
        for w in order:
            walk = op.walks[w]
            comp, reg = walk.anchor.indices[0].component, walk.anchor.indices[0].indices[0]
            start = db.elements_offset(walk.anchor.offset, self.program.strides.get(comp, {}))
            key = (comp, reg)
            if key not in plan:
                plan[key] = {"step": walk.step, "home": start, "walks": {}}
            elif str(plan[key]["step"]) != str(walk.step):
                raise specialization_error(
                    f"a loop over slices walks {comp}'s address register by {plan[key]['step']} "
                    f"and by {walk.step}")
            plan[key]["walks"][w] = start - plan[key]["home"]
        inserted, back = [], []
        for (comp, reg), p in plan.items():
            to_home = p["home"] - self.positions[(comp, reg)]
            if dict(to_home.terms):
                inserted.append(lsc_addr_compute(comp, reg, reg, to_home, scalar_tile))
                # a move like an access's: the section moves it back at its
                # end - a loop's next iteration, its tail, start where it did
                # (a streamed tile's: ZA's kappa 1 loads X's rows into tiles)
                walked = self.walked_by
                walked[(comp, reg)] = walked.get((comp, reg), offpoly.const(0)) + to_home
                self.walked_by = walked
            # every slice walked - a vector length of steps on - then its walk
            # stepped back: home
            walk = offpoly._make({tuple(sorted(("VL",) + f)): c for f, c in dict(p["step"].terms).items()})
            if dict(walk.terms):
                back.append(lsc_addr_compute(comp, reg, reg, offpoly.const(0) - walk, scalar_tile))
            self.positions[(comp, reg)] = p["home"]
        op.walk_plan = plan
        # its access columns planned here - a register of the loop's own for
        # each, the emitter allocating and emitting them
        columns, pointers, column_of = slice_columns(op, plan, self.loop_gregs) if plan else ({}, {}, {})
        op.info["slice_columns"] = (columns, pointers, column_of) if plan else None
        if plan and not op.info.get("preload") \
                and "slice_registers" not in op.info and "slice_moves" not in op.info:
            if pointers:
                # a register of the loop's own per access column, set up
                # before it: the emitter allocates and emits, nothing chosen
                # at emission. Their setup after the frame's - the slice index
                # among the registers its operands allow (w12-w15), taken
                # first - so the setups carry slice_setup (slice_frames)
                setups, op.block, regs = self.slice_registers(op, plan, pointers, column_of)
                for o in setups:
                    o.properties["slice_setup"] = True
                inserted += setups
                op.info["slice_registers"] = regs
            else:
                # no pointer to be had: the iteration's moves in the IR
                op.block = self.slice_moves(op, plan)
                op.info["slice_moves"] = True
        # it moves them: the scheduler keeps what addresses through them after
        # it, after it
        op.refresh()
        return inserted + [op] + back

    def slice_walks(self, op, walks: list) -> tuple[list, list, list]:
        """
        A loop over slices of a count known at run time with its walks'
        pointers: each walk a register of the loop's own - the walks from the
        same element by the same step one - set up before it from the element
        its access starts at, the accesses at it, and one step a walker in the
        body by the walk's step (times the copies of an unrolled one). Registers
        of the IR's: the emitter allocates and emits them
        (docs/ADDRESSING_PLAN.md 6.6, walkers and columns)
        :return: (the setup operations before the loop, the block, the
                 walkers' registers - theirs to free after it)
        """
        scale = op.subtiling.unroll if op.info.get("unrolled") else 1
        walkers, regs, setups = {}, [], []
        for w in walks:
            if w["start"] in walkers:
                continue
            reg = self.new_reg(w["comp"], "walker start")
            walkers[w["start"]] = reg
            regs.append((w["comp"], reg))
            delta = w["elements"] - self.positions[(w["comp"], w["reg"])]
            # a walker at its access's own element too: the copy, that its
            # register exists and holds what the access starts at
            setups.append(lsc_addr_compute(w["comp"], w["reg"], reg, delta, scalar_tile))
            self.positions[(w["comp"], reg)] = w["elements"]
        out = []
        for b in op.block:
            if isinstance(b, (lsc_load, lsc_store)):
                w = walks[int(b.properties.get("walk", 0))]
                b.indices[0] = lsc_reg_index(w["comp"], [walkers[w["start"]]])
            out.append(b)
        stepped = set()
        for i, w in enumerate(walks):
            if w["start"] in stepped:
                continue
            stepped.add(w["start"])
            step = offpoly._make({f: c * scale for f, c in dict(op.walks[i].step.terms).items()})
            if any(dict(step.terms).values()):
                reg = walkers[w["start"]]
                out.append(lsc_addr_compute(w["comp"], reg, reg, step, scalar_tile))
        return setups, out, regs

    def slice_registers(self, op, plan: dict, pointers: dict,
                        column_of: dict) -> tuple[list, list, list]:
        """
        A loop over slices with a register of its own per access column: each
        access at its column's register - the home column's the register the
        loop walks anyway - every other column's set up before the loop from
        that register, and all of them stepped on in the body by an iteration.
        Registers of the IR's: the emitter allocates and emits them, nothing
        chosen at emission (docs/ADDRESSING_PLAN.md 6.6, walkers and columns)
        :return: (the setup operations before the loop, the block, the
                 columns' registers - theirs to free after it)
        """
        columns = {}
        setups = []
        for (key, name), column in pointers.items():
            if column is None or not any(dict(column.terms).values()):
                continue                # the home column: the register itself
            reg = self.new_reg(key[0], "column pointer")
            columns[(key, name)] = reg
            setups.append(lsc_addr_compute(key[0], key[1], reg, column, scalar_tile))
        out = []
        for b in op.block:
            if isinstance(b, (lsc_load, lsc_store)):
                key, name, vectors = column_of[b.properties.get("walk", 0)]
                if (key, name) in columns:
                    b.indices[0] = lsc_reg_index(key[0], [columns[(key, name)]])
                if vectors is not None:
                    b.add_property("voffset", vectors)
            out.append(b)
        for (comp, reg), p in plan.items():
            step = offpoly._make({f: c * op.subtiling.unroll for f, c in dict(p["step"].terms).items()})
            if not any(dict(step.terms).values()):
                continue
            moved = [reg] + [r for (key, _), r in columns.items() if key == (comp, reg)]
            out += [lsc_addr_compute(comp, r, r, step, scalar_tile) for r in moved]
        return setups, out, sorted((key[0], reg) for (key, _), reg in columns.items())

    def slice_moves(self, op, plan: dict) -> list:
        """
        A loop over slices' block with the moves of one iteration in it: each
        access at its plan register, moved there before it - the vector
        lengths a signature takes as an immediate recorded with the access
        (voffset) - and after the last, every register's step on to the next
        iteration's home. Address computations of the IR's: the speller spells
        them into their instructions, the scheduler places them among the
        accesses (docs/ADDRESSING_PLAN.md 6.6, an iteration's address moves)
        :return: the block, the moves among its operations
        """
        walk_of = {w: key for key, p in plan.items() for w in p["walks"]}
        accesses = [b for b in op.block if isinstance(b, (lsc_load, lsc_store))]
        placed, end = slice_placements(accesses, plan, walk_of)
        out = []
        for b in op.block:
            if isinstance(b, (lsc_load, lsc_store)):
                key, move, vectors = placed[id(b)]
                if move is not None and any(dict(move.terms).values()):
                    out.append(lsc_addr_compute(key[0], key[1], key[1], move, scalar_tile))
                if vectors is not None:
                    b.add_property("voffset", vectors)
            out.append(b)
        for (comp, reg), p in plan.items():
            # an iteration takes unroll slices: the step on by them all, less
            # where the last access left the register
            step = offpoly._make({f: c * op.subtiling.unroll for f, c in dict(p["step"].terms).items()})
            net = step - end[(comp, reg)]
            if any(dict(net.terms).values()):
                out.append(lsc_addr_compute(comp, reg, reg, net, scalar_tile))
        return out

    def forms(self, op) -> None:
        """
        What an operation's signatures allow whatever its address - the forms
        the ISA takes (a tail's masked ones without an all-true predicate);
        an access's kept with it (properties["usable"], copies of it too) for
        placing its address (adapt). ADDRESSING_PLAN 6.2: the forms of every
        operation first, the addresses after - a loop's copies made between
        """
        if isinstance(op, lsc_loop):
            if "slices" != op.info.get("kind"):
                for walk in op.walks:
                    self.forms(walk.anchor)
            return
        if isinstance(op, lsc_store) and "shuffle" == op.rsln:
            raise specialization_error(
                f"{op.indices[1]}: a shuffle store is a row of a transpose in registers, "
                f"which shufflenet makes of blocks of as many rows as a vector has lanes - "
                f"these rows aren't; alone it would store the row contiguously")
        if isinstance(op, (lsc_load, lsc_store)):
            sigs = _sigs(op.sigs)
            # a last vector's access (tailmask) under the mask the emitter sets
            # up from tail(<index>): its masked forms usable without an all-true
            # predicate (RVV's v0.t)
            tail = op.properties.get("tail") is not None
            usable = [s for s in sigs if tail or _usable(self.ctx, s)]
            if sigs and not usable:
                raise specialization_error(
                    f"every {op.step.op} signature for {self.program.offsets[op.offset]} needs a "
                    f"governing predicate the ISA doesn't set up")
            op.properties["usable"] = usable
            return
        if isinstance(op, lsc_transformation):
            sigs = _sigs(op.resolution.compute_sg)
            if sigs and not any(_usable(self.ctx, s) for s in sigs):
                raise specialization_error(
                    f"every {op.op} signature needs a governing predicate the ISA "
                    f"doesn't set up")
        if isinstance(op, lsc_move):
            sigs = _sigs(op.sigs)
            if sigs and not any(_usable(self.ctx, s) for s in sigs):
                raise specialization_error(
                    "every move signature needs a governing predicate the ISA doesn't "
                    "set up")
            if not sigs:
                raise specialization_error(f"the ISA has no move for {op.rsln}")

    def adapt(self, op) -> list:
        if isinstance(op, lsc_loop) and "slices" == op.info.get("kind"):
            return self.adapt_slices(op)
        if isinstance(op, lsc_loop):
            # each walk's anchor addressed like any access, its address
            # computations before the loop
            inserted = []
            for walk in op.walks:
                done = self.adapt_access(walk.anchor)
                walk.anchor = done[-1]
                inserted += done[:-1]
            op.refresh()
            if op.info.get("walker"):
                # its copies' walker (flow/stages/loops.py): set up here, after
                # the anchor's walk - from where the register is now to the
                # anchor's element (a fill from the last element backwards from
                # a vector length of steps on, one back)
                inserted.append(self.walker_start(op))
            return inserted + [op]
        if isinstance(op, (lsc_load, lsc_store)):
            return self.adapt_access(op)
        return [op]

    def walker_start(self, loop):
        """
        An element loop's walker set up: an address step from the component's
        register to the anchor's element, as far as where the register is
        """
        from ..flow.stages.loops import WALKER
        anchor = loop.walks[0].anchor
        comp, reg = anchor.indices[0].component, anchor.indices[0].indices[0]
        elements = self.program.offsets.elements_offset(anchor.offset, self.program.strides.get(comp, {}))
        delta = elements - self.positions[(comp, reg)]
        if loop.subtiling.order < 0:
            terms = dict(loop.walks[0].step.terms)
            delta = delta + offpoly._make({tuple(sorted(("VL",) + f)): c for f, c in terms.items()}) \
                - loop.walks[0].step
        return lsc_addr_compute(comp, reg, WALKER, delta, scalar_tile)

    def rebase(self, block: ir_block, rebased: dict) -> list:
        """
        After a preloading prologue: each register of a preloaded component
        moved to its first access in the body, so the loop's offsets start
        at 0 - where none of its accesses there goes negative (x86 takes no
        negative offset) and the move is constant or in vector lengths
        """
        shift = block.preload_shift or {}
        if not any(shift.values()):
            return []
        db, firsts, lows = self.program.offsets, {}, {}
        for op in block.body:
            if not isinstance(op, (lsc_load, lsc_store)):
                continue
            comp, reg = op.indices[0].component, op.indices[0].indices[0]
            if not shift.get(comp) or (comp, reg) not in self.positions:
                continue
            rel = db.elements_offset(op.offset, self.program.strides.get(comp, {})) - self.positions[(comp, reg)]
            firsts.setdefault((comp, reg), rel)
            lows.setdefault((comp, reg), []).append(rel)
        out = []
        for (comp, reg), delta in firsts.items():
            terms = dict(delta.terms)
            if any(f and ("VL",) != f for f in terms) or not any(terms.values()):
                continue
            # none of the register's accesses below it after the move
            if any(dict((r - delta).terms).get((), 0) < 0 or dict((r - delta).terms).get(("VL",), 0) < 0
                   for r in lows[(comp, reg)]):
                continue
            out.append(lsc_addr_compute(comp, reg, reg, delta, scalar_tile))
            self.positions[(comp, reg)] = self.positions[(comp, reg)] + delta
            rebased[(comp, reg)] = delta
        return out

    def loop_advances(self, block: ir_block) -> dict:
        """
        A loop's advance to its next iteration, per address register the model
        set up: what the emitter otherwise appends as text after the body
        """
        if block.loop_index is None or not block.advance:
            return {}
        db, out = self.program.offsets, {}
        for comp, oid in block.advance.items():
            step = db.elements_offset(oid, self.program.strides.get(comp, {}))
            for (c, reg) in list(self.positions):
                if c == comp and (c, reg) in self.program.addr_setup:
                    out[(c, reg)] = step
        return out

    def adapt_block(self, block: ir_block):
        self.loop_index = block.loop_index
        rebased = {}
        filled = [s for s in ("prologue", "body", "epilogue", "tail", "subtail") if getattr(block, s)]
        for section in ("prologue", "body", "epilogue", "tail", "subtail"):
            ops = []
            # --ldinc-imm-offsets last: each column's first access jumps its
            # register to the column's last row (plan_jumps)
            self.jumps = self.plan_jumps(getattr(block, section)) if "last" == self.imm_offsets else {}
            for op in getattr(block, section):
                ops += self.adapt(op)
            # registers walked in this section back where it found them: the
            # next section (or iteration) starts from the same positions - and
            # in a loop's body and last iteration, merged with the advance to
            # the next iteration: one add a register, placed by the schedulers
            walked = self.walked_by
            advances = self.loop_advances(block) if section in ("body", "epilogue") else {}
            # a case's last section: moving its registers back is dead - the
            # kernel returns after it (phase+rotate's walks, C's walked columns) -
            # unless it repeats: a loop's tail runs once a step left (packm's
            # 2-wide transposed panel walked its x1 to row 1 for good)
            repeats = "tail" == section and _tail_runs(block)
            if self.final_block and filled and section == filled[-1] and not advances and not repeats:
                for key, moved in walked.items():
                    self.positions[key] = self.positions[key] - moved
                walked = {}
            # a section run once (not a loop's body, nor a tail that repeats):
            # a component nothing after it accesses - the block's later
            # sections, the blocks after - has its registers neither moved
            # back nor advanced: dead (the k loop's last iteration: A's and
            # B's, the epilogue walking C)
            once = not (block.loop_index is not None and "body" == section) and not repeats
            after = None
            if self.accessed_later is not None:
                rest = ("prologue", "body", "epilogue", "tail", "subtail")
                later_here = [s for s in rest[rest.index(section) + 1:]
                              if s not in ("tail", "subtail") or _tail_runs(block)]
                after = self.accessed_later | _components_accessed(
                    [_sections(block, later_here)])
            if once and after is not None:
                walked, advances = dict(walked), dict(advances)
                for key in [k for k in list(walked) + list(advances) if k[0] not in after]:
                    if key in walked:
                        self.positions[key] = self.positions[key] - walked.pop(key)
                    advances.pop(key, None)
            for key in list(walked) + [k for k in advances if k not in walked]:
                comp, reg = key
                moved = walked.get(key, offpoly.const(0))
                step = advances.get(key)
                # strides walked (k:s - a gemmsup's A, B): one move, the advance
                # less the walk - two would each add the stride's register as
                # often as it counts (8 strides back, 8 on: 16 adds for none);
                # addrmerge merges constants and vector lengths, not strides
                strided = any(f and f != ("VL",) for x in (moved, step) if x is not None
                              for f in dict(x.terms))
                if strided and step is not None:
                    net = step - moved
                    op = lsc_addr_compute(comp, reg, reg, net, scalar_tile)
                    op.properties = dict(op.properties or {}, advance=step)
                    ops.append(op)
                    self.positions[key] = self.positions[key] - moved
                    continue
                if any(dict(moved.terms).values()):
                    ops.append(lsc_addr_compute(comp, reg, reg, offpoly.const(0) - moved, scalar_tile))
                if step is not None and any(dict(step.terms).values()):
                    op = lsc_addr_compute(comp, reg, reg, step, scalar_tile)
                    op.properties = dict(op.properties or {}, advance=step)
                    ops.append(op)
                self.positions[key] = self.positions[key] - moved
            if advances:
                block.advance_in_ir = True
            self.walked_by = {}
            if "prologue" == section:
                # the loop's offsets from 0: registers moved past the preload
                ops += self.rebase(block, rebased)
            if "epilogue" == section:
                # and back after the last iteration: the tail starts where it
                # does when the loop (and its prologue) didn't run
                # - a component nothing after it accesses (a tail that runs, the
                # blocks after) left where it is: its registers dead
                for (comp, reg), delta in rebased.items():
                    if after is None or comp in after:
                        ops.append(lsc_addr_compute(comp, reg, reg, offpoly.const(0) - delta, scalar_tile))
                    self.positions[(comp, reg)] = self.positions[(comp, reg)] - delta
            setattr(block, section, ops)
            # stride pointers are computed per section, in the same registers;
            # a scratch address placed in one section isn't relied on in the next
            self.pointers = set()
            self.walking = {}
            self.placed = set()

    def element_types(self, dt):
        """
        Where the element type is processor state (RVV's vtype): an lsc_state
        before each transformation needing another than the one before - a
        widening one the narrow type, arithmetic on a group the group's type
        and grouping - each section beginning and ending with the setup's
        (dt's, ungrouped), whatever order the sections run in. A
        transformation whose signatures need different ones left to the
        emitter (vtype_dynamic), as it was
        """
        from ..models.lsc.operations import lsc_state
        from ..irmod.lsc.base import blocks_and_sections
        setup = (adt_size(dt), 1)
        def need(op, sig):
            sizes = [adt_size(o.dt) for o in sig.operands.values() if rgt.VEC == o.rtype and o.dt is not None]
            if not sizes:
                return None
            ways = op.properties.get("group", 1)
            return (min(sizes), 1) if widening_ways(sig) > 1 else (max(sizes), ways)
        def switch(want, sig, dtype=None):
            wdt = dtype or next(o.dt for o in sig.operands.values()
                                if rgt.VEC == o.rtype and o.dt is not None and adt_size(o.dt) == want[0])
            # named as the setup's state names it (asmgen: e32), a group's
            # grouping after it (e64,m2)
            name = f"e{8 * want[0]}" + (f",m{want[1]}" if want[1] > 1 else "")
            return lsc_state({"vtype": name}, wdt)
        for block, section in blocks_and_sections(self.program):
            ops, out, current = list(getattr(block, section) or []), [], setup
            for op in ops:
                if isinstance(op, lsc_transformation):
                    sigs = _sigs(op.resolution.compute_sg) if op.resolution is not None else []
                    wants = {w for w in (need(op, s) for s in sigs) if w is not None}
                    if len(wants) > 1:
                        op.add_property("vtype_dynamic", True)
                        current = None              # the emitter's from here
                    elif wants:
                        want = next(iter(wants))
                        if want != current:
                            out.append(switch(want, next(s for s in sigs if need(op, s) == want)))
                            current = want
                out.append(op)
            if current is not None and current != setup:
                out.append(switch(setup, None, dt))
            setattr(block, section, out)

    def specialize(self) -> ir_program:
        """
        The forms, then the addresses (the flow runs them as two stages:
        isa_specialize, addresses - a loop's copies made between)
        """
        self.specialize_forms()
        return self.place()

    def specialize_forms(self) -> None:
        """
        Every operation's forms (forms: whatever its address)
        """
        for block in list(self.program.blocks) + [b for case in self.program.cases for b in case.blocks]:
            for section in ("prologue", "body", "epilogue", "tail", "subtail"):
                for op in getattr(block, section) or []:
                    self.forms(op)

    def start_blocks(self) -> None:
        """
        Each component's address registers started in the IR: before the first
        block that accesses it - the program's, a case's own where it starts
        there - a setup block moving each register from the component's base
        parameter (BASE_REGISTER) to where it starts (addr_setup), the copy and
        the move then the speller's to spell and merge, the scheduler's to
        place (docs/ADDRESSING_PLAN.md: setup in the IR, address starts)
        """
        setup = {c for c, _ in self.program.addr_setup}
        offsets, strides = self.program.offsets, self.program.strides

        def starts(blocks, started):
            out = []
            for block in blocks:
                new = sorted((_components_accessed([block]) & setup) - started)
                ops = [lsc_addr_compute(comp, BASE_REGISTER, reg,
                                        offsets.elements_offset(oid, strides.get(comp, {})), scalar_tile)
                       for (comp, reg), oid in sorted(self.program.addr_setup.items()) if comp in new]
                if block.loop_index is not None:
                    # its counts: the iterations and what's left of its count
                    # parameter - the emitter deciding them (loop_counts)
                    ops.append(lsc_value_op("counts", writes=[f"iter({block.name})", f"left({block.name})"],
                                            reads=[block.loop_index], step=block.step, loop=block.name))
                if ops:
                    start = ir_block(name=f"{START_BLOCK}{block.name}")
                    start.body = ops
                    out.append(start)
                    started = started | set(new)
                out.append(block)
            return out, started
        self.program.blocks, started = starts(list(self.program.blocks), set())
        for case in self.program.cases:
            case.blocks, _ = starts(list(case.blocks), started)

    def place(self) -> ir_program:
        """
        The addresses, block by block - positions, walks, moves, immediates,
        offsets - then the processor state each access's forms need
        """
        self.start_blocks()
        case_blocks = [b for case in self.program.cases for b in case.blocks]
        for j, block in enumerate(self.program.blocks):
            self.accessed_later = _components_accessed(list(self.program.blocks[j + 1:]) + case_blocks)
            self.adapt_block(block)
        start = dict(self.positions)
        for case in self.program.cases:
            self.positions = dict(start)
            for i, block in enumerate(case.blocks):
                # the case's last block: nothing reads its registers after it
                self.final_block = len(case.blocks) - 1 == i
                self.accessed_later = _components_accessed(case.blocks[i + 1:])
                self.adapt_block(block)
            self.final_block = False
        self.accessed_later = None
        # the state the ISA's setup leaves (for the narrowest element type, as
        # the emitter sets it up), lsc_states setting more: each access's
        # signatures those whose requirements hold where it is - decided here,
        # with the forms, before scheduling
        # (imported here: the state module reaches the irmods, tailmask this module)
        from ..models.lsc.state import check_state
        dt = min(self.ctx.component_dts.values(), key=adt_size)
        if self.ctx.gen.isa_setup().element_type_is_state():
            self.element_types(dt)
        isa = self.ctx.gen.isa_setup()
        state, engine = isa.state(dt), isa.engine()
        if engine is not None:
            # the engine on before every path and off after them, as state the
            # emitter writes through the ISA's signatures (set's ENGINE): the
            # state before it the setup's without its own switch
            from ..models.lsc.operations import lsc_state
            on, off = engine
            if all(self.assumed.get(k) == v for k, v in on.items()):
                # the caller's: the engine on around the kernel, no switch
                self.program.engine_assumed = True
            elif not any(isinstance(op, lsc_state) and op.values == on for op in self.program.entry):
                # first: smstart zeroes the predicates - a tail's mask after it
                self.program.entry = [lsc_state(dict(on), dt)] + list(self.program.entry)
                self.program.exit = list(self.program.exit) + [lsc_state(dict(off), dt)]
            state = {**state, **off}
        problems = check_state(self.program, {**state, **self.assumed})
        if problems:
            raise specialization_error("processor state: " + "; ".join(problems))
        return self.program
