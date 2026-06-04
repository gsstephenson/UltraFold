# External tools

UltraFold orchestrates external folding engines through subprocess/shell calls.
These must be installed separately and available on your `PATH`.

## RNAstructure

Provides the core windowed folding/partition commands:

- `Fold` / `Fold-smp` — minimum-free-energy folding (SHAPE/DMS-directed)
- `partition` / `partition-smp` — partition-function base-pairing probabilities
- `ProbabilityPlot` — convert a `.pfs` to a pairprob file
- `dot2ct` / `ct2dot` — convert between dot-bracket and connectivity table

Install: <https://rna.urmc.rochester.edu/RNAstructure.html>

Typical invocations (from the original development notes,
`docs/original_dev_notes.txt`):

```
Fold-smp {input.fasta} {output.ct} --dmsnt {input.dms} -MD {maxdistance}
partition-smp {input.fasta} {output.pfs} --dmsnt .dms -MD 600
ProbabilityPlot -t {input.pfs} {output_pairprob.txt}
```

## EternaFold / CONTRAFold

Used as an alternative folding engine:

```
contrafold predict {fname}.bpp2seq --evidence --numdatasources 1 \
    --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 > {fname}.db
```

Install: <https://github.com/eternagame/EternaFold>

### ⚠️ Hardcoded parameter path

v1.0.0 references the EternaFold parameter file at:

```
/opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1
```

in `src/ultrafold/Ultrafold.py` (5 occurrences). If EternaFold is installed
elsewhere, either:

1. symlink your install to `/opt/EternaFold/`, or
2. edit the path in `src/ultrafold/Ultrafold.py`.

Making this configurable via a CLI flag/environment variable is a
[roadmap](../ROADMAP.md) item for v2 (kept hardcoded in v1.0.0 for fidelity).

## ShapeMapper 2

Produces the `profile.txt` / `.map` reactivity input.
<https://github.com/Weeks-UNC/shapemapper2>
