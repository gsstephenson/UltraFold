# Evaluate LinearPartition-E for scale (linear-time; needs an evidence C++ port)

<!-- labels: performance, medium, research -->
<!-- milestone: v3.0 -->

## Summary
LinearPartition/LinearFold compute the partition function + base-pair probabilities in **linear
time/memory** (vs CONTRAfold's O(n³)), and a LinearPartition-**E** build uses EternaFold's own
parameters. For very long mRNAs this could collapse the per-window partition step into a single
pass. **Gating caveat:** the `-E` build carries **zero** SHAPE/evidence code — `--shape` works
only in Vienna/Deigan mode — so using it with UltraFold's `--evidence` restraint requires custom
C++ to port the EternaFold evidence/posterior potential into the `lpe` build, then numeric
re-validation.

## Key facts (verified)
- Headline 256×/2,771× speedups are for monolithic 16k–33k nt sequences; on UltraFold's capped
  1200/3000 nt windows the realized per-window speedup is ~10–100×.
- Beam pruning makes the partition **approximate** → BPP posteriors differ numerically from
  CONTRAfold even with identical params (not byte-identical).
- License: custom **non-OSI** academic license (more restrictive than EternaFold's BSD-3) —
  install as an external `PATH` tool only; do **not** vendor into GPLv3 UltraFold.

## Proposed work (spike)
- [ ] Prototype the EternaFold-evidence port into LinearPartition-E (or confirm infeasibility).
- [ ] Benchmark wall-clock vs parallelized EternaFold (Issue 02) on ESR1 and a larger transcript.
- [ ] Quantify BPP divergence vs CONTRAfold; decide if within tolerance for a new validated version.

## Decision gate
Only pursue if (a) the evidence port is tractable and (b) parallelized EternaFold (Issue 02) is
still the bottleneck on real transcript sizes. Otherwise defer.

## References
GPU/efficiency study "Lever A, Step 2".
