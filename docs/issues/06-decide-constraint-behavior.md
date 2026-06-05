# Decide constraint behavior — EternaFold can't do constraints + evidence together

<!-- labels: design, high, science, decision -->
<!-- milestone: v2.0 -->

## Summary
SuperFold's core mechanism is *SHAPE-restrained folding **with** the 99%-confident partition
pairs (and user `--ssRegion`/`--pkRegion`) forced as hard constraints, simultaneously*. UltraFold
still computes the 99% pairs and writes the full RNAstructure `.const` file — but `contrafold`
never receives them, so all constraints are silently dropped at the fold step. **This cannot be
fixed within EternaFold alone:** its `--constraints` and `--evidence` flags are **mutually
exclusive** (the binary errors out if both are given).

## Evidence
- 99% pairs computed: [`Ultrafold.py:210-214`](../../src/ultrafold/Ultrafold.py#L210-L214); threaded into fold: [`:232`](../../src/ultrafold/Ultrafold.py#L232)
- `.const` written by `constraintFile`: [`:939-951`](../../src/ultrafold/Ultrafold.py#L939-L951), called [`:971`](../../src/ultrafold/Ultrafold.py#L971)
- Fold command references only `.bpp2seq` (no `--constraints`): [`:508`](../../src/ultrafold/Ultrafold.py#L508)
- `/opt/EternaFold` `Contrafold.cpp:688` — *"You can only use either constraints or evidence, not both together."*

## Decision required
Choose one (and document it honestly — right now the code implies constraints are applied when
they aren't):

- **Option A — recover the mechanism via RNAstructure (recommended).** Keep EternaFold for the
  evidence-driven partition/BPP; perform the *constrained Fold* step with RNAstructure `Fold -C`
  + `-md` (Issue 08). This reunites the two halves and is exactly SuperFold's method, modernized.
- **Option B — EternaFold-only, constraints as hard input.** Build a BPSEQ input with forced
  pairs in the pairing column and run `--constraints` **without** `--evidence` — but this
  sacrifices the SHAPE soft restraint. (Generally inferior for this pipeline.)
- **Option C — declare unconstrained folding the method.** Delete the `.const` machinery and
  state in README/`-h` that folding uses SHAPE evidence only, no hard constraints.

## Acceptance criteria
- [ ] A written decision recorded in `docs/v2_plan.md`.
- [ ] Code and docs agree: either constraints demonstrably affect the fold, or the machinery is
      removed and docs say so.
- [ ] If Option A: the 99% pairs measurably change the RNAstructure-track structure.

## References
Gap analysis (blocked-by-engine); EternaFold source; SuperFold upstream `Fold ... -C {f}.const`.
