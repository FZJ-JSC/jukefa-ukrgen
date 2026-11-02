# The old mechanism

ukrgen's first pipeline - its lsc emitter and specializer, the codegen,
irmod, variant, mru, schedule and specialize stages, the BLIS patcher, the
address-parameter model - as it was when the family pipeline replaced it,
each module at its old path under `legacy/src`, its tests under
`legacy/tests`. Kept to read, not to run:

- it can't be imported: it uses `asmgen.asmblocks.operations`, which asmgen
  moved to `asmblocks/op`, and names (`comparison`) its modules no longer
  get; `schedulers/register_instruction_dependency_scheduler.py` doesn't
  parse;
- its tests can't load, or test the old address resolver's API
  (`test_addr_resolver`).

Moved by asmgen 0.6's rework (`docs/V06_REWORK.md` in asmgen, phase 8): the
live pipeline - `injectors/blis/families.py`, `clitools` - imports none of
it.

The signature emitter's address resolution has a test of its own, as the old
resolver had `test_addr_resolver`: `tests/specializers/test_addresses.py`.

## Moved here later

- `src/ukrgen/generators/mm.py`: the old mm generator, its two-level loop
  orders (`MmNnKk`: uppercase a dimension's coarse level - registers -,
  lowercase its factor - lanes) and the `mm_op` / `tile` types. The flow
  tiles with `generators/tiling.py`, which took over the two-level orders.
- `src/ukrgen/models/load_store_cpu.py` and
  `src/ukrgen/schedulers/minreguse_scheduler.py`: the model and scheduler
  built on them; nothing in the flow used either.
- Their tests: `tests/generators/test_mm.py`, `test_mm_pack.py`,
  `tests/models/test_load_store_cpu.py`.
