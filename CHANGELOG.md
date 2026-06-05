# Changelog

All notable changes to UltraFold are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [1.0.1] — 2026-06-05

Correctness + performance hotfixes. **v1.0.0 remains the frozen citable reference** (git tag
`v1.0.0`); this release is for new work only.

### Fixed
- **Partition step now uses the reactivity data (`--evidence`).** The `contrafold` partition
  command omitted `--evidence`, so the per-window base-pairing posteriors were computed
  **sequence-only** — meaning the merged dot plot, the 99%-confident constraint pairs, and the
  entire Shannon-entropy / low-SHAPE-low-Shannon region analysis ignored the SHAPE/DMS input.
  Adding `--evidence` makes these outputs probing-directed as intended.
  ⚠️ **This changes scientific output relative to v1.0.0** (the partition/entropy results were
  previously not reactivity-directed). Re-run analyses produced with v1.0.0 if they relied on the
  dot plot, Shannon entropy, or region calls. See issue #1.

### Changed
- **Per-window fold/partition jobs now run in parallel and honor `--np`.** They were dispatched
  serially (`batchSubmit` was imported but never used), so large RNAs ran as hundreds of serial,
  single-threaded folds. Window jobs are independent, so this is a near-linear wall-clock speedup
  with **byte-identical results** (deterministic DP, per-window-unique filenames). See issue #2.

See the [v2 plan](docs/v2_plan.md) and tracked [issues](docs/issues/) for the remaining work.

## [1.0.0] — 2024-11-13

Initial public release: the **faithful, citable Python 2.7 reference
implementation** of UltraFold.

### Included
- Windowed RNA secondary-structure modeling directed by SHAPE/DMS reactivities.
- Partition-function consensus base-pairing across overlapping windows.
- Shannon-entropy analysis and low-SHAPE/low-Shannon region detection.
- Arc-diagram and circle-comparison plotting.
- Optional PVclient structure drawing.
- EternaFold/CONTRAFold alternative folding engine support.

### Notes
- This release packages the existing source **with no algorithmic changes**, to
  preserve reproducibility of published results. The code dates to 2024-11-13.
- Derived from SuperFold (G. M. Rice) and ShapeMapper 2.2 (DMS support by
  D. Mitchell III); released under GPLv3 accordingly.

See [ROADMAP.md](ROADMAP.md) for planned Python 3, dependency, and GPU work.

[1.0.1]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.1
[1.0.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.0
