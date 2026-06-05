# Regression harness + CI (golden ESR1 outputs)

<!-- labels: infra, high, testing -->
<!-- milestone: v2.x -->

## Summary
There are zero automated tests and no CI for ~1,400 lines of scientific numerics. Build a
golden-output smoke test on the bundled ESR1 example and run it in GitHub Actions. This is the
safety net the ROADMAP's "validate byte-for-byte against v1.0.0" goal depends on.

## ⚠️ Critical sequencing
Capture the goldens **after** the coverage/`inf` fixes (Issue 05) and ideally after Issues 01/04.
Capturing them against current v1.0.0 would **canonize corrupt output** (the `inf`/magic-500 bugs,
the sequence-only partition) as the reference, and "byte-for-byte fidelity" would then faithfully
reproduce bugs.

## Proposed work
- End-to-end ESR1 run producing `merged_*.dp`, `merged_*.ct`, `shannon_*.txt` (skip web-dependent
  PVclient; use `--noPVclient`).
- Store goldens (or hashes + tolerance) under `tests/golden/`.
- A `pytest`/script comparator with documented numeric tolerance for the dot-plot/Shannon values.
- GitHub Actions workflow: lint + smoke test on push/PR (matrix py2.7 for v1.x, py3 for the port).

## Acceptance criteria
- [ ] `make test` (or `pytest`) runs the ESR1 smoke test and compares to goldens.
- [ ] CI is green on `main`.
- [ ] Goldens captured *after* Issue 05 (documented which commit produced them).
- [ ] Tolerance policy documented in `CONTRIBUTING.md`.

## References
ROADMAP v1.x ("tiny end-to-end smoke test") + v2.0 (byte-for-byte validation); v2 plan sequencing note.
