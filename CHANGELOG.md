# Changelog

All notable changes to UltraFold are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-06-06

**Python 3 port.** UltraFold now runs on Python 3; the v1.x line stays Python 2.7, frozen at the
`v1.0.0` tag for citation. Validated to reproduce the v1.1.1 reference within float-repr precision:
`merged.ct` is byte-identical, and `merged.dp` / `shannon` are numerically identical to ~5e-12 (py3
simply prints more float digits) — verified on both engines against the v1.1.1 goldens.

### Changed
- **Ported all modules to Python 3** — `print()` functions, `range` / `list(map(...))`, `hashlib`
  byte-encoding, subprocess text/bytes handling, `open('r')`. The silent `np.array(map(...))`
  corruption hazard (0-d object array) is resolved (now `np.array(list(map(...)))`).
- **PVclient drawing is OFF by default and the flag is fixed.** Use `--pvclient` to enable;
  `--noPVclient` is retained as a deprecated alias. v1.x had this inverted (drawing on by default,
  `--noPVclient` to disable). **CLI behavior change.**
- Program self-identification updated to UltraFold (SuperFold lineage credit retained).

### Removed
- The unused `batchSubmit.py` module (parallel dispatch is handled in-pipeline; lineage attribution
  remains in CITATION.cff and the README).

### Added
- **Regression test harness + CI (#11).** Pure-Python unit tests (RNAtools `CT`/`dotPlot`, the
  missing-data sanitizer) plus end-to-end golden-output tests that run the real pipeline on a
  fixed ESR1 slice and byte-compare the merged `.dp`/`.ct`/`shannon` against committed references
  per engine, including a `--np 4` vs `--np 1` determinism check. GitHub Actions runs the unit
  tests under Python 3; the end-to-end tests skip where the folding tools aren't installed. (The
  harness was first added on the v1.x line and the goldens were re-captured under Python 3 for
  v2.0.0.) See [`tests/README.md`](tests/README.md).

### Changed
- **Port-prep code hygiene (#13).** Behavior-preserving cleanup ahead of the Python 3 port — each
  change verified **byte-identical** against the v1.1.1 golden outputs on both engines (incl. the
  region `.ps`):
  - Deleted the dead, shadowed `.bps`-reading `mainAssemble` (the live `.dp` one is unchanged) — −69 lines.
  - Reconciled the duplicate, divergent `CT` class in `PyCircleCompareSF.py` to import the single
    `RNAtools.CT` (the pipeline already passed `RNAtools.CT` objects to `makeCircle`) — −340 lines.
  - Removed the unused `batchSubmit` import and the duplicate `os`/`shlex`/`subprocess` imports.
  - Removed the dead startup writes (`temp_seq_file.seq`, `profile_data.bpp2seq`) and the dead
    `args.drawPVclient` assignment.
  - Fixed `readSeq()`'s `return processed` (undefined name) → `return seq`.
  *No change to released behavior, so no version bump.*

## [1.1.1] — 2026-06-05

Correctness & robustness fixes over v1.1.0 (no new features). **v1.0.0 remains the frozen citable
reference.**

### Fixed
- **Missing-data sentinels no longer corrupt the EternaFold restraint (#4).** ShapeMapper's `-999`
  no-data sentinel (and any negative / NaN reactivity) was written verbatim into the `.bpp2seq`
  evidence column, so EternaFold folded against a garbage potential at masked positions. These are
  now mapped to `-1.0` (EternaFold's `UNKNOWN_POTENTIAL`, treated as "no evidence"). The bundled
  ESR1 example has 139 such positions. ⚠️ Changes EternaFold-engine output at masked nucleotides.
- **`runCheck` validates the right toolchain for the chosen engine (#3).** It previously aborted
  unless RNAstructure's `Fold`/`partition`/`ProbabilityPlot` were present — even on the EternaFold
  path that never uses them. It now checks `contrafold` + `dot2ct` for `--engine eternafold` and
  `Fold`/`partition`/`ProbabilityPlot` for `--engine rnastructure`. `DATAPATH` is still required by
  both (EternaFold's `dot2ct` also loads the data tables). Runs out-of-the-box on EternaFold-only.
- **Partition 3′ coverage gap closed (#5).** The EternaFold partition window loop could stop up to
  `stepSize-1` nt short of the 3′ end, leaving terminal nucleotides with no pairing probability /
  Shannon entropy. A 3′-anchored final window is now appended when needed.
- **Long-range base pairs no longer crushed in the merged dot plot (#5).** `concatonateDP`'s
  coverage helper returned a hardcoded `500` for any pair spanning ≥600 nt, dividing its
  probability by 500. It now uses the real window-coverage count (with a divide-by-zero guard).
  Affects the EternaFold engine (RNAstructure already bounds spans via `-md`). ⚠️ Changes
  EternaFold-engine long-range pair probabilities.
- **Sparse low-SHAPE regions no longer abort the run.** A region with no base pairs made the
  circle-plot sensitivity/PPV divide by zero (`PyCircleCompareSF.makeCircle`) and crash the whole
  pipeline; the per-region circle plot is now guarded so the run completes (the region `.ct` is
  still written).

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

[2.0.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v2.0.0
[1.1.1]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.1.1
[1.1.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.1.0
[1.0.1]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.1
[1.0.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.0
