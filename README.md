# UltraFold

> Windowed RNA secondary-structure modeling for large RNAs from SHAPE/DMS chemical-probing data — a faster, refined evolution of SuperFold.

![version: 2.0.0](https://img.shields.io/badge/version-2.0.0-blue)
![python: 3](https://img.shields.io/badge/python-3-blue)
![license: GPL v3](https://img.shields.io/badge/license-GPLv3-green)

UltraFold predicts the secondary structure of **large RNAs** by breaking the
folding problem into overlapping windows that can be folded in parallel on a
multi-core workstation. It is directed by per-nucleotide **SHAPE** or **DMS**
reactivities (from [ShapeMapper 2](https://github.com/Weeks-UNC/shapemapper2)),
combines partition-function base-pairing probabilities across windows into a
consensus model, computes **Shannon entropy** to highlight well- vs.
poorly-determined regions, and renders arc and circle structure plots.

---

## ⚠️ Versions — read this first

- **v2.0.0 (current) — Python 3.** The Python 3 port of the windowed-consensus
  pipeline. It reproduces the v1.1.1 numerics within float-repr precision
  (validated against golden reference outputs on both engines) and offers an
  optional RNAstructure engine alongside EternaFold.
- **v1.x — Python 2.7.** The original reference line. **v1.0.0 is the frozen,
  citable reference** used to generate published results, kept faithful and
  unchanged. **If you are citing the method in a paper, cite v1.0.0** (see
  [CITATION.cff](CITATION.cff)); the `v1.0.0` git tag is immutable.

See [CHANGELOG.md](CHANGELOG.md) for the per-version history and [ROADMAP.md](ROADMAP.md)
for what's planned.

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
- **EternaFold / CONTRAFold** and **RNAstructure** — the folding/partition engines

Because these are licensed under the **GNU GPL v3**, UltraFold is also released
under **GPLv3** (see [LICENSE](LICENSE)). Original copyright headers are
preserved in the source files.

---

## How it works

For an input reactivity profile, UltraFold:

1. **Partitions** the RNA in overlapping windows and computes per-window
   base-pairing probabilities, which are trimmed and merged into one whole-RNA
   **dot plot** (`merged_*.dp`).
2. Extracts the **~99%-confident pairs** and computes per-nucleotide **Shannon
   entropy** (`shannon_*.txt`).
3. **Folds** the RNA in overlapping windows and merges them by overlap-consensus
   into a single structure (`merged_*.ct`).
4. Identifies **low-SHAPE / low-Shannon** ("well-determined") regions and exports
   per-region structures plus arc and circle/Shannon figures.

### Two engines (`--engine`)

| `--engine` | Restraint model | Notes |
|---|---|---|
| `eternafold` *(default)* | SHAPE/DMS as **learned evidence** (EternaFold via `contrafold`) | Best probing-directed accuracy; uses EternaFold's evidence model rather than a slope/intercept pseudo-energy. |
| `rnastructure` | SHAPE/DMS **pseudo-free-energy** (RNAstructure `Fold`/`partition`) | Natively honors hard constraints (`-C`), max-pairing-distance (`-md`), DMS-specific handling (`-dmsnt`), and pseudoknot-capable folding. Useful as an orthogonal cross-check and when you need those capabilities. |

> Several CLI knobs (`--SHAPEslope`/`--SHAPEintercept`, `--maxPairingDist`,
> DMS-specific handling) currently apply to the **`rnastructure`** engine; the
> `eternafold` engine folds with EternaFold's learned evidence model, so those
> particular knobs do not affect its output (tracked as a roadmap item).

---

## Requirements

### Python
- **Python 3** (≥3.6). (The v1.x line is Python 2.7 — see the v1.x tags.)
- Packages: `pip install -r requirements.txt` (`numpy`, `pandas`, `matplotlib`;
  `httplib2` only if you enable `--pvclient` drawing). v2.0.0 is validated
  against `numpy==1.16.6 / pandas==0.24.2 / matplotlib==2.2.3`.

### External command-line tools (must be on your `PATH`)
UltraFold orchestrates external folding engines via subprocess calls. The set you
need depends on `--engine`:

| Engine | Tools required on `PATH` | Also needs |
|---|---|---|
| `eternafold` *(default)* | `contrafold`, `dot2ct` | `DATAPATH` (used by `dot2ct`) |
| `rnastructure` | `Fold`, `partition`, `ProbabilityPlot` | `DATAPATH` (RNAstructure data tables) |

Set `DATAPATH` to your RNAstructure `data_tables` directory:

```bash
export DATAPATH=/path/to/RNAstructure/data_tables
```

Sources: [RNAstructure](https://rna.urmc.rochester.edu/RNAstructure.html) ·
[EternaFold](https://github.com/eternagame/EternaFold). See
[docs/external_tools.md](docs/external_tools.md) for details.

> **Note (hardcoded EternaFold params path):** UltraFold references the EternaFold
> parameter file at `/opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1`.
> If you installed EternaFold elsewhere, symlink it there or edit the path in
> `src/ultrafold/Ultrafold.py`. Making this configurable is a planned roadmap item.

---

## Quickstart

```bash
# 1) Python 3 environment with the validated dependency set
conda create -n ultrafold-py3 python=3.7
conda activate ultrafold-py3
pip install -r requirements.txt

# 2) external tools on PATH + DATAPATH (see Requirements)
export DATAPATH=/path/to/RNAstructure/data_tables

# 3) run the bundled ESR1 example (default EternaFold engine)
cd src/ultrafold
python Ultrafold.py ../../examples/ESR1/E_DMS_fwd_ESR1_first_3000.map --DMS --np 4
```

Outputs land in `results/` (`merged_*.dp`, `merged_*.ct`, `shannon_*.txt`, the
arc/Shannon figures, and `regions/`). PVclient drawing is **off by default**;
pass `--pvclient` to enable it. See [examples/ESR1/README.md](examples/ESR1/README.md).

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
| `--engine {eternafold,rnastructure}` | `eternafold` | Folding/partition engine (see above) |
| `--DMS` | off | Input is DMS probing data (ShapeMapper 2.2 `--dms`) |
| `--np N` | 2 | Number of parallel worker processes |
| `--eternafoldParams PATH` | bundled path | EternaFold parameter file *(eternafold engine)* |
| `--kappa FLOAT` | 1.0 (contrafold default) | Weight on the SHAPE/DMS evidence *(eternafold engine)* |
| `--partitionWindowSize N` / `--partitionStepSize N` | 1200 / 100 | Partition window length / spacing |
| `--foldWindowSize N` / `--foldStepSize N` | 3000 / 300 | Fold window length / spacing |
| `--trimInterior N` | 300 | Nucleotides trimmed from partition-window interiors before merging |
| `--maxPairingDist N` | 600 | Maximum base-pairing distance *(rnastructure engine; warns under eternafold)* |
| `--SHAPEslope` / `--SHAPEintercept` | 1.8 / -0.6 | SHAPE pseudo-free-energy params *(rnastructure engine; warns under eternafold)* |
| `--ssRegion FILE` / `--pkRegion FILE` | — | Forced single-stranded / pseudoknot constraints *(rnastructure engine; warns under eternafold)* |
| `--pvclient` | off | Enable PVclient (PseudoViewer) structure drawing; needs `httplib2` + a reachable server |
| `--noPVclient` | — | Deprecated no-op alias (PVclient is already off by default) |

---

## Running the tests

UltraFold ships a regression harness ([tests/](tests/)): pure-Python unit tests
plus end-to-end **golden-output** tests that run the real pipeline on a fixed
ESR1 slice and byte-compare the merged `.dp` / `.ct` / `shannon` against committed
references for each engine.

```bash
make test            # unit tests (no external tools needed)
make test-e2e        # end-to-end golden tests (need the engine tools + DATAPATH)
```

GitHub Actions runs the unit tests on every push; the end-to-end tests skip where
the folding tools aren't installed. See [tests/README.md](tests/README.md).

### Reproducibility / validation

v2.0.0 was validated to reproduce the **v1.1.1** reference outputs within
float-repr precision on both engines: `merged.ct` is byte-identical and
`merged.dp` / `shannon` match to ~5×10⁻¹² (Python 3 simply prints more float
digits). **v2.1.0 is byte-identical to v2.0.0 on default runs** (both engines).
The goldens are tool-version-specific — regenerate them with
`python tests/update_goldens.py` when you intentionally change behavior.

Every run also writes `results/run_manifest_<name>.txt` recording the engine, the
full parameter set, and md5 checksums of the input and the EternaFold parameter
file — so any result traces back to exactly how it was produced.

---

## Repository layout

```
UltraFold/
├── src/ultrafold/        # the Python 3 pipeline
│   ├── Ultrafold.py          # main pipeline / entry point
│   ├── RNAtools.py           # CT / dot-plot / SHAPE I/O
│   ├── drawArcRibbons_simple.py  # arc-diagram plotting
│   ├── PyCircleCompareSF.py  # circle-plot comparison
│   └── pvclient.py           # PVclient structure drawing (optional, off by default)
├── tests/                # regression harness (unit + golden e2e) + goldens
├── tools/                # standalone helper utilities
├── examples/ESR1/        # small runnable example
├── docs/                 # file formats, external tools, v2 plan, issues
├── CHANGELOG.md
├── CITATION.cff
├── ROADMAP.md            # the v2+ plan (deps, GPU, etc.)
├── CONTRIBUTING.md
├── requirements.txt
└── LICENSE               # GPLv3
```

---

## Citing UltraFold

See [CITATION.cff](CITATION.cff). Please cite **v1.0.0** for results produced
with the reference implementation.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE). Derived from
GPLv3-licensed SuperFold / ShapeMapper; original author attributions are
retained in the source headers.
