# GPU / deep-learning research spike (gated by restraint support)

<!-- labels: research, low, performance -->
<!-- milestone: v3.0 -->

## Summary
Investigate whether a GPU-native engine can ever fit UltraFold — explicitly as a **research
direction**, not a near-term efficiency fix. The 2024–2026 conclusion: there is **no maintained,
restraint-aware, EternaFold-equivalent GPU partition-function engine** to drop in today.

## Why GPU is not the cheap win
- EternaFold/CONTRAfold has **no GPU path** at inference (its multi build parallelizes *training*).
- GPU-native deep-learning models (UFold, MXfold2, RhoFold+, RNAformer, …) are **sequence-only**:
  they cannot ingest the SHAPE/DMS reactivities that are the point of the pipeline, and most emit
  contact maps, not calibrated base-pair probabilities for the Shannon step.
- `JAX-RNAfold` (GPU, differentiable) is a sequence-*design* tool — no restraints, no BPP.
- `RNAstructure partition-cuda` uses Turner params (not EternaFold) and its CUDA-build SHAPE
  support is unconfirmed.
- The cheap same-science speedups are CPU: parallelism (Issue 02) then linear-time (Issue 14).

## Spike questions
- [ ] Track restraint-conditioned models (e.g. a future RibonanzaNet variant that *consumes*
      input reactivities rather than predicting them) — does one emerge that fits?
- [ ] If the project ever deliberately moves to sequence-only folding, what is the best
      GPU-batched model for windowed inference (and how to produce a usable BPP)?
- [ ] Quantify achievable throughput vs parallelized EternaFold + LinearPartition before
      committing engineering.

## Decision gate
Pursue only if (a) a restraint-aware GPU engine becomes available, **or** (b) leadership decides
to fork a sequence-only mode. Any such change is a **new method/version** with full re-validation,
not a drop-in — and breaks the "faithful reference" framing.

## References
GPU/efficiency study "Lever B"; SOTA survey (DL models are sequence-only).
