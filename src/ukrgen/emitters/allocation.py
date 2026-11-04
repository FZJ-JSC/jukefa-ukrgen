"""
The emitter's data registers through one object (docs/REGISTER_ALLOCATION.md
step 1)
"""

from asmgen.asmblocks.op import register_type as rgt

from ..specializers.signature import specialization_error


class register_allocator:
    """
    Every data register - vectors, FP scalars, tiles - taken and freed through
    one object: a value's register (take, free), registers of no value's own
    (reserve, unreserve: index vectors, masks, slices' register sets, the
    parameters' scalars), a value bound to one of those (bind). Its state the
    emitter's current one (a case starts from a copy, the tracker switches):
    the next step gives it its own, the allocation computed before emitting
    """

    def __init__(self, emitter):
        self.e = emitter

    def take(self, idx, rtype):
        """
        The physical register for a virtual one. Vectors fill the vector file
        from the bottom, scalars from the top: on ISAs where scalar FP registers
        are the low parts of vector registers the two must not meet.
        """
        e = self.e
        key = (idx.component, idx.indices[0], rtype)
        group = e.program.groups.get(idx.component)
        parts = group[2] if group is not None and len(group) > 2 else None
        if key not in e.phys and parts is not None and rgt.VEC == rtype:
            # a group's parts each a group of its own (structfuse): a part's
            # registers consecutive wherever there's room, its rows wherever
            # its first is; a register in none ungrouped
            part = next(((s, n) for s, n in parts.items() if s <= idx.indices[0] < s + n), None)
            if part is not None:
                first, size = part
                used = e.rt.get_used_regs("vreg")
                start = next((s for s in range(0, e.gen.max_vregs() - size + 1)
                              if not any(s + p in used for p in range(size))), None)
                if start is None:
                    raise specialization_error(f"no {size} consecutive vector registers left for "
                                               f"{idx.component}{first}")
                for p in range(size):
                    e.rt.reserve_specific_reg("vreg", start + p)
                    member = (idx.component, first + p, rtype)
                    e.phys[member] = e.gen.vreg(start + p)
                    e.numbers[member] = ("vreg", start + p)
        elif key not in e.phys and group is not None and rgt.VEC == rtype:
            # a group of registers: all of them at once, consecutive and
            # starting at a multiple of their number (RVV's groups need that,
            # SVE's structure loads and stores take consecutive ones)
            ways = group[0]
            first = idx.indices[0] - idx.indices[0] % ways
            used = e.rt.get_used_regs("vreg")
            start = next((s for s in range(0, e.gen.max_vregs() - ways + 1, ways)
                          if not any(s + p in used for p in range(ways))), None)
            if start is None:
                raise specialization_error(f"no {ways} consecutive vector registers left for "
                                           f"{idx.component}{first}")
            for p in range(ways):
                e.rt.reserve_specific_reg("vreg", start + p)
                member = (idx.component, first + p, rtype)
                e.phys[member] = e.gen.vreg(start + p)
                e.numbers[member] = ("vreg", start + p)
        if key not in e.phys:
            dt = e.dts.get(idx.value())
            tag = "vreg"
            if rgt.VEC == rtype:
                bound = e.bounds.get(key)
                if bound is None:
                    if not e.rt.available("vreg"):
                        raise specialization_error(
                            f"{key[0]}: no vector register left - the accumulators, the data "
                            f"registers and a loop's unrolled copies (unroll_loops' factor and "
                            f"registers) take them all; scheduling (--mru) renames tiles "
                            f"streamed through straight-line code into the registers free, "
                            f"fewer register sets or data registers fit")
                    number = e.rt.reserve_any_reg("vreg")
                else:
                    used = e.rt.get_used_regs("vreg")
                    free = [i for i in bound if i not in used]
                    if not free:
                        raise specialization_error(
                            f"none of the vector registers {bound} left for {key[0]}{key[1]}")
                    number = free[0]
                    e.rt.reserve_specific_reg("vreg", number)
                e.phys[key] = e.gen.vreg(number)
            elif rgt.FP == rtype and "freg" in e.rt.shared:
                # the tracker knows which vector registers FP registers are
                number = e.rt.reserve_any_reg("freg")
                tag = "freg"
                e.phys[key] = e.gen.freg(number, dt)
            elif rgt.FP == rtype and "freg" in e.rt.registered_types:
                # a file of its own (RVV)
                number = e.rt.reserve_any_reg("freg")
                tag = "freg"
                e.phys[key] = e.gen.freg(number, dt)
            elif rgt.FP == rtype:
                # older trackers: from the top of the vector file, clear of vectors
                used = e.rt.get_used_regs("vreg")
                number = max(i for i in range(e.gen.max_vregs()) if i not in used)
                e.rt.reserve_specific_reg("vreg", number)
                tag = "vreg"
                e.phys[key] = e.gen.freg(number, dt)
            elif rgt.TILE == rtype:
                # a tile (SME ZA): from its own file
                # the element type's tiles, or fewer where max-tiles says so
                tiles = e.gen.max_tregs(dt)
                cap = e.ctx.params.get("max-tiles")
                cap = int(cap.value or 0) if cap is not None else 0
                from ..flow.stages.isaparam import register_cap
                tregs = register_cap(e.ctx.params, "treg")
                cap = min(cap, tregs) if cap and tregs else (cap or tregs)
                tiles = min(tiles, cap) if cap > 0 else tiles
                # the tracker's type of dt's tiles (asmgen's treg_tag: SME's by
                # element size, sharing ZA's storage) - added where the
                # generator declares none; max-tiles caps the tiles held
                tag = e.gen.treg_tag(dt)
                if tag not in e.rt.registered_types:
                    e.rt.add_type(tag, tiles)
                held = sum(1 for (t, n) in e.numbers.values() if t == tag)
                if not e.rt.available(tag) or held >= tiles:
                    raise specialization_error(
                        f"{key[0]}: no tile left - {dt.name} has {e.gen.max_tregs(dt)} tiles"
                        f"{f', max-tiles {cap}' if cap > 0 else ''}, "
                        f"all taken; fusing the loops over slices (fuse_slices, forward_slices) "
                        f"keeps tiles out of use, or a smaller microtile needs fewer")
                number = e.rt.reserve_any_reg(tag)
                e.phys[key] = e.gen.treg(number, dt)
            else:
                raise specialization_error(f"{rtype.name} registers are not specialized yet")
            e.numbers[key] = (tag, number)
        return e.phys[key]


    def free(self, key):
        """
        A virtual register's value is dead: its physical register is free again
        (a group's registers stay: a lone member must not be handed out)
        """
        e = self.e
        if key[0] in e.program.groups:
            return
        if key in e.phys:
            tag, number = e.numbers.pop(key)
            e.rt.unuse_reg(tag, number)
            del e.phys[key]


    def reserve(self, tag: str, number: int | None = None) -> int:
        """A register of no value's own: any free one, or the one asked"""
        if number is None:
            return self.e.rt.reserve_any_reg(tag)
        self.e.rt.reserve_specific_reg(tag, number)
        return number

    def unreserve(self, tag: str, number: int) -> None:
        """A register of no value's own free again"""
        self.e.rt.unuse_reg(tag, number)

    def bind(self, key, reg) -> None:
        """A value held in a register reserved for it (a slice loop's set)"""
        self.e.phys[key] = reg
