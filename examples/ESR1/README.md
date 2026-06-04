# Example: ESR1 (first 3000 nt)

A small DMS dataset for the human *ESR1* mRNA (first 3000 nucleotides),
useful as a quick functional check and as a regression reference for future
Python 3 ports.

## File

- `E_DMS_fwd_ESR1_first_3000.map` — ShapeMapper-derived `.map` input
  (position, normalized DMS reactivity, stderr, nucleotide). See
  [../../docs/file_formats.md](../../docs/file_formats.md).

## Run

Requires Python 2.7 and the external tools on your `PATH`
(see [../../docs/external_tools.md](../../docs/external_tools.md)):

```bash
cd ../../src/ultrafold
python Ultrafold.py ../../examples/ESR1/E_DMS_fwd_ESR1_first_3000.map --DMS
```

Generated outputs (`.ct`, `.dp`, `.bpp2seq`, `results/`, etc.) are ignored by
git (see the repository `.gitignore`).
