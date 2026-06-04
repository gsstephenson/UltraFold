# Changelog

All notable changes to UltraFold are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

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

[1.0.0]: https://github.com/gsstephenson/UltraFold/releases/tag/v1.0.0
