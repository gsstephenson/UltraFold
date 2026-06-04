# UltraFold

> Windowed RNA secondary-structure modeling for large RNAs from SHAPE/DMS chemical-probing data — a faster, refined evolution of SuperFold.

![status: v1.0.0](https://img.shields.io/badge/version-1.0.0-blue)
![python: 2.7](https://img.shields.io/badge/python-2.7-yellow)
![license: GPL v3](https://img.shields.io/badge/license-GPLv3-green)

UltraFold predicts the secondary structure of **large RNAs** by breaking the
folding problem into overlapping windows that can be folded in parallel on a
multi-core workstation. It is directed by per-nucleotide **SHAPE** or **DMS**
reactivities (from [ShapeMapper 2](https://github.com/Weeks-UNC/shapemapper2)),
combines partition-function base-pairing probabilities across windows into a
consensus model, computes **Shannon entropy** to highlight well- vs.
poorly-determined regions, and renders arc and circle structure plots.

---

## ⚠️ Version 1.0.0 — read this first

**v1.0.0 is Python 2.7 code.** It is published *faithfully*, as the exact
reference implementation used to generate published results, so that it can be
**cited and reproduced** without ambiguity. No algorithmic changes have been
made during packaging.

This release is, however, deliberately structured for future work. Python 3
porting, dependency modernization, GPU acceleration, and packaging are all
planned — see **[ROADMAP.md](ROADMAP.md)**.

If you are citing the method used in a paper, cite **v1.0.0** (see
[CITATION.cff](CITATION.cff)).

---

## Lineage & attribution

UltraFold was engineered by **George Stephenson**, building on the following
prior work from the **Weeks Lab (UNC–Chapel Hill)** and others:

- **SuperFold** — Greggory M. Rice (UNC, 2014) — windowed folding approach;
  also original author of `RNAtools.py` and `PyCircleCompareSF.py`
  · <https://github.com/Weeks-UNC/Superfold>
- **PVclient / arc-ribbon drawing** — Steven Busan (UNC, 2014) — bundled as
  `pvclient.py` and the arc-diagram plotting code
- **ShapeMapper 2.2** — DMS compatibility by David Mitchell III (2023)
- **EternaFold / CONTRAFold** — used as an alternative folding engine

Because these are licensed under the **GNU GPL v3**, UltraFold is also released
under **GPLv3** (see [LICENSE](LICENSE)). Original copyright headers are
preserved in the source files.

---

## Requirements

### Python
- **Python 2.7**
- Python packages: see [requirements.txt](requirements.txt) (`numpy`, `pandas`,
  `matplotlib`; `httplib2` only if you use PVclient drawing).

### External command-line tools (must be on your `PATH`)
UltraFold orchestrates external folding engines via subprocess calls:

| Tool | Provides | Source |
|------|----------|--------|
| `Fold`, `partition`, `ProbabilityPlot`, `dot2ct` | RNAstructure folding/partition suite | [RNAstructure](https://rna.urmc.rochester.edu/RNAstructure.html) |
| `contrafold` / `eternafold` | EternaFold folding engine (optional path) | [EternaFold](https://github.com/eternagame/EternaFold) |

> **Note (hardcoded path):** v1.0.0 references EternaFold parameters at
> `/opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1`. If you
> installed EternaFold elsewhere, either symlink it to that path or edit the
> path in `src/ultrafold/Ultrafold.py`. Making this configurable is a
> [roadmap](ROADMAP.md) item for v2.

See [docs/external_tools.md](docs/external_tools.md) for details.

---

## Usage

```bash
cd src/ultrafold
python Ultrafold.py <input.map> --DMS [options]
```

`<input.map>` is a ShapeMapper-derived file (nucleotide #, normalized profile,
stderr, sequence). See [docs/file_formats.md](docs/file_formats.md).

Common options (run `python Ultrafold.py -h` for the full list):

| Option | Default | Description |
|--------|---------|-------------|
| `--DMS` | off | Input is DMS probing data (ShapeMapper 2.2 `--dms`) |
| `--np N` | 2 | Number of processors |
| `--maxPairingDist N` | 600 | Maximum base-pairing distance |
| `--partitionWindowSize N` | 1200 | Partition window length |
| `--partitionStepSize N` | 100 | Partition window spacing |
| `--foldWindowSize N` | 3000 | Fold window length |
| `--foldStepSize N` | 300 | Fold window spacing |
| `--trimInterior N` | 300 | nt trimmed to reduce window-end effects |
| `--SHAPEslope` / `--SHAPEintercept` | 1.8 / -0.6 | SHAPE pseudo-free-energy params |
| `--noPVclient` | — | Skip PVclient structure drawing |

### Example
A small example input (first 3000 nt of ESR1) is provided:

```bash
cd src/ultrafold
python Ultrafold.py ../../examples/ESR1/E_DMS_fwd_ESR1_first_3000.map --DMS
```

See [examples/ESR1/README.md](examples/ESR1/README.md).

---

## Repository layout

```
UltraFold/
├── src/ultrafold/        # the v1.0.0 reference implementation (Python 2.7)
│   ├── Ultrafold.py          # main pipeline / entry point
│   ├── RNAtools.py           # CT / dot-plot / SHAPE I/O
│   ├── batchSubmit.py        # parallel job dispatch
│   ├── drawArcRibbons_simple.py  # arc-diagram plotting
│   ├── PyCircleCompareSF.py  # circle-plot comparison
│   └── pvclient.py           # PVclient structure drawing (optional)
├── tools/                # standalone helper utilities (Python 3-clean)
├── examples/ESR1/        # small runnable example
├── docs/                 # file formats, external tools, original dev notes
├── CHANGELOG.md
├── CITATION.cff
├── ROADMAP.md            # the v2+ plan (Py3, deps, GPU)
├── CONTRIBUTING.md
├── requirements.txt
└── LICENSE               # GPLv3
```

---

## Citing UltraFold

See [CITATION.cff](CITATION.cff). Please cite **v1.0.0** for results produced
with this reference implementation.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE). Derived from
GPLv3-licensed SuperFold / ShapeMapper; original author attributions are
retained in the source headers.
