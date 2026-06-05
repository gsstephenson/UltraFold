# Add RNAstructure 6.6 as a parallel cross-validation / capability track

<!-- labels: feature, high, science, engine -->
<!-- milestone: v2.0 -->

## Summary
RNAstructure 6.6 (released 2026-04-02, actively maintained) is the only mainstream engine with
native **DMS** (`-dmsnt`), **hard constraints** (`-C` forced/forbidden), **max-pairing-distance**
(`-md`), and **pseudoknots** (ShapeKnots) — i.e. the four capabilities EternaFold structurally
lacks (Issues 06, 07). It is also the engine SuperFold used, so the windowing/merge code maps
1:1. Add it as a **second engine track** for the capabilities EternaFold can't provide and as an
orthogonal cross-validation of EternaFold results. This also preserves the "faithful reference"
framing better than a wholesale swap.

## Why a parallel track (not a replacement)
- The 2024–2026 deep-learning models are all sequence-only at inference and cannot ingest your
  ShapeMapper2 reactivities — so EternaFold remains the best *probing-directed* engine and stays
  primary.
- EternaFold vs RNAstructure accuracy on probing-directed natural RNAs is statistically
  indistinguishable, so running both and comparing is strictly informative.

## Proposed work
- Add an `--engine {eternafold,rnastructure,both}` selector.
- RNAstructure path = essentially the upstream SuperFold commands (already in
  `/tmp/superfold-upstream/Superfold.py` for reference):
  `partition ... -dmsnt/-sh -sm -si -md -C` → `ProbabilityPlot -t` → `.dp`; `Fold ... -md -C -m 100 -w 0`.
- Reuse the existing windowing, `mainAssemble`, `MasterModel_*`.
- Emit a comparison artifact (EternaFold vs RNAstructure: pair agreement, ΔShannon) per run.

## Acceptance criteria
- [ ] `--engine rnastructure` reproduces SuperFold-style constrained, max-distance, DMS-aware folding.
- [ ] `--engine both` produces a side-by-side comparison on ESR1.
- [ ] Constraints (Issue 06 Option A) demonstrably affect the RNAstructure-track structure.
- [ ] Licensing note: RNAstructure is GPL-2.0 — fine as an external `PATH` dependency.

## References
SOTA survey "RNAstructure: strong, confirmed-fit complement"; upstream SuperFold commands.
