# Configurable EternaFold params path; expose `--kappa` evidence weight

<!-- labels: feature, medium, reproducibility -->
<!-- milestone: v2.0 -->

## Summary
The EternaFold parameter file is hardcoded in 5 places, and the evidence weight `--kappa` (which
controls how strongly reactivity influences folding) is never set — UltraFold relies on whatever
weight is baked into the params file. Both hurt reproducibility and tunability.

## Evidence
- Hardcoded `/opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1` ×5:
  [`Ultrafold.py:508`](../../src/ultrafold/Ultrafold.py#L508), `:516`, `:525`, `:533`, `:586`.
- No `--kappa` on any command (EternaFold's own example uses `0.1`; default is `1.0`).

## Proposed fix
- Add `--eternafold-params PATH` (CLI flag) and/or `ULTRAFOLD_ETERNAFOLD_PARAMS` env var; default
  to the current path for back-compat. Validate readability in `runCheck` (Issue 03).
- Add `--kappa FLOAT` and pass it through to the `contrafold` commands.
- Record the params file path **and a checksum** in the run log for provenance (ties to Issue 12).

## Acceptance criteria
- [ ] EternaFold installed at a non-`/opt` location works without editing source.
- [ ] `--kappa` measurably changes the evidence influence (compare posteriors at 0.1 vs 1.0).
- [ ] Run log records params path + checksum.

## References
v2 plan; gap analysis (`--kappa` not exposed); docs/external_tools.md hardcoded-path note.
