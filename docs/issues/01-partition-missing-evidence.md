# Partition step ignores reactivity — `--evidence` missing (BPP/Shannon are sequence-only)

<!-- labels: bug, critical, science, engine -->
<!-- milestone: v1.1 -->

## Summary
The partition/posteriors command omits `--evidence`, so `contrafold` ignores the reactivity
column of the `.bpp2seq` file and folds **sequence-only**. As a result the merged dot-plot, the
99%-confident constraint pairs, **and the entire Shannon-entropy / low-SHAPE-low-Shannon region
analysis are computed without the SHAPE/DMS data** — defeating the purpose of the
probing-directed half of the pipeline.

## Evidence
- Partition command (no `--evidence`): [`Ultrafold.py:586`](../../src/ultrafold/Ultrafold.py#L586)
  ```
  contrafold predict {f}.bpp2seq --params .../EternaFoldParams_PLUS_POTENTIALS.v1 --posteriors {cutoff} {out} --numdatasources 1
  ```
- Fold commands (correctly include `--evidence`): [`:508`](../../src/ultrafold/Ultrafold.py#L508), `:516`, `:525`, `:533`.
- Verified against `/opt/EternaFold` source + live binary runs: without `--evidence`, the engine
  reports `Use evidence: 0` and the reactivity column is discarded.

## Why it matters
Critical. The Shannon entropy, the well-determined-region calls, the 99% partition constraints,
and the merged base-pair probabilities all flow from this step. They are currently **not
probing-directed**.

## Proposed fix
Add `--evidence --numdatasources 1` to the partition command:
```
contrafold predict {f}.bpp2seq --evidence --numdatasources 1 --params .../EternaFoldParams_PLUS_POTENTIALS.v1 --posteriors {cutoff} {out}
```
(`--evidence` requires the `..._PLUS_POTENTIALS.v1` params file, which is already used.)

## Acceptance criteria
- [ ] Partition `.bps` posteriors **differ** when the reactivity column is present vs zeroed
      (proves evidence is now consumed).
- [ ] Re-run ESR1 example; confirm merged `.dp`, `shannon_*.txt`, and region calls change.
- [ ] Documented as a v1.0.0→v1.1 behavior change (this is a correctness fix, not a silent edit).

## References
v2 plan headline finding #3; cross-confirmed by the gap analysis and the SOTA survey.
