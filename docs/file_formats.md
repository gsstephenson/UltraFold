# File formats

UltraFold interoperates with ShapeMapper, RNAstructure, and EternaFold. The
main formats are summarized below.

## Input: `.map`

Tab-separated, one row per nucleotide. This is the primary UltraFold input.

| Column | Meaning |
|--------|---------|
| 1 | Nucleotide number (1-based) |
| 2 | Normalized reactivity (`Norm_profile`); `0.0`/`-999` indicates no/low data |
| 3 | Standard error of the reactivity |
| 4 | Nucleotide identity (A/C/G/U) |

Example (`examples/ESR1/E_DMS_fwd_ESR1_first_3000.map`):

```
1	0.000000	0.000000	U
2	0.000000	0.000000	G
3	0.364789	0.126183	U
```

Derived from a ShapeMapper2 `profile.txt`
(<https://github.com/Weeks-UNC/shapemapper2/blob/master/docs/file_formats.md>).

## `.bpp2seq`

EternaFold evidence input. Columns: position, nucleotide, label (e.g. `e1`),
normalized reactivity. Example row: `1 G e1 7.07e+00`. NaN reactivities are
written as `-999`. (See `tools/make_bpp2seq.py`.)

## `.bps`

EternaFold posterior output: per-nucleotide pairing partners with
probabilities. Convertible to a pairprob file (see `tools/convert_to_pairprob.py`).

## pairprob (`.dp` / pairprob text)

`i  j  -log10(probability)` after a header line with the sequence length.
Produced from a `.pfs` via RNAstructure `ProbabilityPlot`, or converted from a
`.bps`.

## `.ct`

RNAstructure connectivity-table secondary structure.
See <https://rna.urmc.rochester.edu/Text/File_Formats.html#CT>.
Convert to/from dot-bracket with `dot2ct` / `ct2dot`.

## `.pfs`

RNAstructure partition-function save file (from `partition` / `partition-smp`),
consumed by `ProbabilityPlot`.
