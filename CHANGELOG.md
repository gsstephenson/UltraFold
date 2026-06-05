# Changelog

All notable changes to UltraFold are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-06-05

Adds an optional RNAstructure folding/partition engine alongside EternaFold (a new feature, hence
the minor bump). **v1.0.0 remains the frozen citable reference** and v1.0.1 is unaffected.

### Added
- **`--engine {eternafold,rnastructure}` (default `eternafold`).** A second, optional
  folding/partition backend that shells out to RNAstructure's `Fold` / `partition` /
  `ProbabilityPlot`. Unlike the EternaFold path, RNAstructure natively applies the SHAPE/DMS
  restraint (`-sh` / `-dmsnt`), the maximum pairing distance (`-md`), **and hard constraints**
  (`-C`) — so the user `--ssRegion` / `--pkRegion` pairs **and** the 99%-confident partition pairs
  are actually enforced, restoring SuperFold's constrain-and-refold method that EternaFold
  structurally cannot express (its `--constraints` and `--evidence` are mutually exclusive). Useful
  as an orthogonal cross-validation track and for DMS-specific / pseudoknot-capable folding. The
  default EternaFold behavior is unchanged. Verified end-to-end on ESR1 (constraints provably
  obeyed; structures differ from EternaFold). See issues #8, #6, #7.

### Fixed
- **Single-window `mainAssemble` no longer trims off real data.** The live `mainAssemble` had lost
  upstream's single-window guard, so any RNA shorter than one partition window (~<1400 nt at
  defaults) had its 3' ~300 nt silently trimmed from the merged dot plot and Shannon entropy.
  Restored the `len(targetDP)==1` early return (found by adversarial review).

### Changed
- **Output directories are wiped before each run.** `fold_*` / `partition_*` are recreated clean
  (`_freshDir`) so stale `.ct` / `.dp` files from a prior run with different parameters can no
  longer pollute the consensus/assembly (found by adversarial review).

See the [v2 plan](docs/v2_plan.md) and tracked [issues](docs/issues/) for the remaining work.

## [1.0.1] — 2026-06-05

Correctness + performance hotfixes over v1.0.0 (no new features). **v1.0.0 remains the frozen
citable reference** (git tag `v1.0.0`).

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

[1.1.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.1.0
[1.0.1]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.1
[1.0.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.0
