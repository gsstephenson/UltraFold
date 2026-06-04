# Tools

Standalone helper utilities. Unlike the v1.0.0 reference implementation in
`src/ultrafold/` (which is **Python 2.7**), these scripts are **Python 3**
(they use f-strings / pandas) and are independent of the main pipeline.

## `make_bpp2seq.py`

Convert a ShapeMapper `profile.txt` into an EternaFold `.bpp2seq` evidence file
(position, nucleotide, `e1`, normalized reactivity; NaN → `-999`).

```bash
python3 make_bpp2seq.py <profile.txt> <output.bpp2seq>
```

## `convert_to_pairprob.py`

Convert an EternaFold `.bps` posterior file into a pairprob (`.dp`-style) file
(`i  j  -log10(probability)` with a sequence-length header).

```bash
python3 convert_to_pairprob.py <input.bps> <output_pairprob.txt>
```

See [../docs/file_formats.md](../docs/file_formats.md) for format details.
