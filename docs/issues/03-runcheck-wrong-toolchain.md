# `runCheck()` validates the wrong toolchain (RNAstructure required but unused; `dot2ct` unchecked)

<!-- labels: bug, high, packaging -->
<!-- milestone: v1.0.1 -->

## Summary
`runCheck()` aborts unless RNAstructure `Fold`, `partition`, `ProbabilityPlot` and `DATAPATH`
are present — **none of which the EternaFold-swapped pipeline uses** — while the binaries it
*does* need (`contrafold`, `dot2ct`) are not checked. The published "reference" therefore cannot
run out-of-the-box on an EternaFold-only machine: the very first gate exits.

## Evidence
- Probes `["Fold","partition","ProbabilityPlot"]` + `DATAPATH`: [`Ultrafold.py:697-723`](../../src/ultrafold/Ultrafold.py#L697-L723)
- The only RNAstructure binary actually executed is `dot2ct`: [`:414`](../../src/ultrafold/Ultrafold.py#L414)
- Engine is `contrafold`: [`:508`](../../src/ultrafold/Ultrafold.py#L508), `:586`.
- `Fold`/`partition`/`ProbabilityPlot` appear only in the `runCheck` probe — never invoked.

## Why it matters
Reproducibility/usability landmine that contradicts the citability goal.

## Proposed fix
Validate the tools actually used:
- Require `contrafold` (or `eternafold`) and `dot2ct` on `PATH`.
- Require the EternaFold params file to be readable (ties into Issue 09).
- Drop the `Fold`/`partition`/`ProbabilityPlot` + `DATAPATH` requirement from the EternaFold path.
  (Keep an RNAstructure check **only** under the Issue 08 RNAstructure track, where it is real.)
- Note: `dot2ct` does not need `DATAPATH` (pure format converter).

## Acceptance criteria
- [ ] A machine with only `contrafold` + `dot2ct` (no RNAstructure, no `DATAPATH`) runs ESR1 end-to-end.
- [ ] Missing `contrafold` or `dot2ct` produces a clear, correct error.
- [ ] README/`requirements`/`docs/external_tools.md` updated to match.

## References
v2 plan EternaFold-limits table; confirmed across all three studies.
