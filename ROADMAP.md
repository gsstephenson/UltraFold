# UltraFold Roadmap

UltraFold v1.0.0 is the **faithful, citable Python 2.7 reference
implementation**. This document records the planned evolution so that the v1
codebase stays a stable scientific anchor while future work happens in
clearly-versioned, separately-validated releases.

## Guiding principle

> **v1.0.0 is never silently changed.** It is the version of record for
> published results. All modernization lands as new minor/major versions with
> validation against v1.0.0 output on reference datasets.

## Planned work

### v1.x — packaging & docs (no behavior change)
- [ ] Pin exact, known-good Python 2.7 dependency versions in `requirements.txt`.
- [ ] Expand `docs/` (algorithm overview, parameter guidance, file-format specs).
- [ ] Add a tiny end-to-end smoke test with bundled reference output.
- [ ] Capture the exact external-tool versions used (RNAstructure, EternaFold).

### v2.0 — Python 3 port (behavior-preserving)
- [ ] Port `Ultrafold.py`, `RNAtools.py`, `PyCircleCompareSF.py`, `pvclient.py`
      to Python 3. **Special attention to integer division** (`/` vs `//`) and
      other Python 2/3 numeric/string differences that can silently alter
      scientific results.
- [ ] Validate v2 output byte-for-byte (or within documented tolerance) against
      v1.0.0 on reference datasets before release.
- [ ] Replace the hardcoded `/opt/EternaFold/...` parameter path with a CLI
      flag / environment variable / config file.
- [ ] Modernize dependencies (current `numpy`/`pandas`/`matplotlib`).

### v2.x — engineering quality
- [ ] PEP 8 / formatter (black) once the code is Python 3.
- [ ] Convert the flat module set into a properly importable package with
      console entry points (`pip install .` → `ultrafold` command).
- [ ] CI (lint + smoke test) via GitHub Actions.
- [ ] Type hints on public functions.

### v3.0 — performance
- [ ] GPU acceleration of the folding/partition windowing.
- [ ] Profiling and parallelism improvements beyond the current
      `multiprocessing` batch dispatch.

## How the repo is designed to support this

- `src/ultrafold/` isolates the reference implementation from tooling.
- `tools/` holds auxiliary scripts that already work under Python 3.
- `examples/` gives a small, fast dataset for regression-checking ports.
- `CHANGELOG.md` + `CITATION.cff` make each version individually citable.
