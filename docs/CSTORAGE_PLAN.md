# C storage dispatch inside the kernel - plan and progress

ukrgen v1 reached row-major, column-major and general C each with its own
kernel, a C wrapper picking one by C's strides. v2 does it in one kernel:
C's storage is another dimension of the epilogue's case dispatch - the k
loop shared, an epilogue per storage and alpha/beta case (3 storages x 6
cases = 18 blocks is fine: many code paths are where a generator shines).

## Design

- `--C-storage S...` (gemm; families' `c-storage`): the storages, the last
  the default - its epilogue runs for any C the others don't take, its C
  the component `C` with `--C-layout`. Each other storage is an alias
  component of C - `Cr` (row: `[n:c, m:s]`), `Cc` (col: `[m:c, n:s]`) -
  with C's data type, its own data and address registers, sharing C's base
  pointer and the stride it keeps.
- The composition expanded (`stages/ukr/storage.py`): alias components;
  every epilogue STO touching C copied per alias, C renamed in it
  (`store.r`, `betascale.r`, ...); the branch the product of storages and
  alpha/beta cases, a storage's cases first, conditioned on C's unit
  stride: row `stride(C,n) == 1`, col `stride(C,m) == 1` (elements).
- Every stage sees the expanded composition: each copy's tile operations
  are solved for its alias's layout (presets: the copy takes its STO's
  entry, C renamed), the builder and the specializer address each alias by
  its layout.
- The signature: an alias's parameters are C's - `base(Cr)` is
  `base(C)`, `stride(Cr,m)` is `stride(C,m)` - no parameters added.
- The dispatch: a stride condition compares C's stride parameter with one
  element's bytes in a general register - before alpha/beta's.
- blisgen: a family's `c-storage` builds one kernel with its branches; the
  wrapper's temporary tile: `SETUP_CT_ANY` with an `any` storage, `_AMBI`
  with row and col.

## Steps

| # | Step | Status |
|---|------|--------|
| 1 | Composition expanded: alias components, STO copies, cases x storages; `--C-storage`; alias layouts | done |
| 2 | Solve and presets per copy (C renamed) | done: copies take their STO's entry, C renamed; `direct` decided per STO by the C it reaches |
| 3 | Signature: alias parameters onto C's | done: the emitter maps an alias's parameters onto C's registers; the emitted parameters C's only |
| 4 | Dispatch on stride conditions (integer compare) | done: `mov`, subtract one element's bytes, `jzero` - no asmgen addition |
| 5 | Kernels run: row/any, row/col, col/any - every C storage through the harness, AVX-512, SVE, RVV | done: AVX-512 row/any and row/col natively; SVE (256, 512) and RVV (128, 256) row/any under qemu - every C storage exact |
| 6 | blisgen: `c-storage` as branches in one kernel; wrapper macros; example configurations | done: `c-storage` sets `--C-storage` and C's layout (the last storage's); the wrapper `SETUP_CT_ANY` / `_AMBI`; example configurations |
| 7 | Measured against v1 (8x3v AVX-512: row-, column-major, general C) | |
