# Missing-data sentinels (`-999`/NaN) are fed to the engine as evidence

<!-- labels: bug, high, science -->
<!-- milestone: v1.1 -->

## Summary
`create_bpp2seq` writes the raw normalized reactivity verbatim into the evidence column,
including ShapeMapper's `-999` no-data sentinel and any NaN. EternaFold's documented convention
is `-1` for "no data" and it ignores values `≤ 1e-5`; it expects **positive** unpairedness
potentials. Feeding `-999`/negatives is outside the documented contract and corrupts the
restraint at masked positions instead of treating them as "no constraint".

## Evidence
- `create_bpp2seq` writes raw value: [`Ultrafold.py:346`](../../src/ultrafold/Ultrafold.py#L346)
- Reactivity source includes `-999`/NaN: [`:906`](../../src/ultrafold/Ultrafold.py#L906), `.map` format (`0.0`/`-999` = no data).
- Verified against `/opt/EternaFold` `SStruct.cpp` (`UNKNOWN_POTENTIAL = -1`, `THRESH_NO_DATA = 1e-5`).

## Why it matters
Masked / low-coverage nucleotides should contribute **no** restraint; instead they push a
garbage potential into the fold.

## Proposed fix
Map no-data to EternaFold's convention before writing the `.bpp2seq`:
- `-999`, negatives, and NaN → emit `-1` (or omit / set `≤1e-5`) so the engine treats them as absent.
- Keep genuine `0.0` distinct from "no data" if the upstream `.map` distinguishes them.

## Acceptance criteria
- [ ] No `.bpp2seq` row carries `-999`/NaN as a positive potential.
- [ ] Masked positions verifiably contribute no restraint (compare posteriors with masked vs unmasked).
- [ ] Unit test for the reactivity→evidence mapping.

## References
Gap analysis "missing-data masking: critical"; EternaFold source contract.
