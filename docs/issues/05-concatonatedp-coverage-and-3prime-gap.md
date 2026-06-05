# `concatonateDP` magic-500 / coverage division + partition 3′ coverage gap

<!-- labels: bug, high, science -->
<!-- milestone: v1.0.1 -->

## Summary
Two window-merge defects that silently distort the merged dot plot (and therefore the 99%
constraints and Shannon entropy):

1. **Magic `return 500`.** `calcCoverage` returns a hardcoded `500` for any pair with
   `j - i ≥ 600`, and the merge divides the summed linear probability by that coverage — crushing
   long-range pairs by orders of magnitude. Because `--maxPairingDist` is inert (Issue 07), such
   long-range pairs *do* appear (up to the window size).
2. **Partition 3′ gap.** The partition window loop can leave up to `step-1` (≤99) terminal
   nucleotides uncovered when `(rnaLength - windowSize) % step != 0` — unlike the fold stage,
   which adds 5′/3′ end windows. Those nt get zero pairing probability / Shannon.

## Evidence
- `calcCoverage` hardcoded 500 + division: [`Ultrafold.py:1054-1060`](../../src/ultrafold/Ultrafold.py#L1054-L1060), [`:1119`](../../src/ultrafold/Ultrafold.py#L1119)
- Partition windowing: [`:594-598`](../../src/ultrafold/Ultrafold.py#L594-L598)
- (Note: a separately-claimed div-by-zero here was **investigated and refuted** — every merged
  pair is covered by its own source window; do not "fix" that non-bug. See the audit-method memo.)

## Why it matters
Corrupts long-range pair probabilities and drops terminal nucleotides — affects every transcript
long enough to window, invisibly.

## Proposed fix
- Replace the `500` constant with the real coverage count (and guard against degenerate values).
- Define explicit max-pairing-distance handling that matches the documented `--maxPairingDist`
  (post-filter pairs by `|i-j|`), or remove the option (coordinate with Issue 07).
- Cover the partition 3′ gap with end windows like the fold stage, or clamp the final window to
  `rnaLength`.

## Acceptance criteria
- [ ] No hardcoded `500`; long-range pair probabilities are not artificially crushed.
- [ ] All nucleotides (incl. the 3′ terminus) receive coverage / pairing probability.
- [ ] Regression check on ESR1 before/after, documented as a v1.0.1 correctness change.

## References
99-agent audit (confirmed findings) + gap analysis; refuted div-by-zero noted in audit-method memo.
