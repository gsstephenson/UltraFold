# UltraFold v2 Plan

> Status: planning. This document and the issues in [`docs/issues/`](issues/) translate the
> 2026 codebase assessment into tracked, actionable work. It **supplements** (does not
> replace) [`ROADMAP.md`](../ROADMAP.md) — the roadmap states the *direction*; this states
> the *specific, evidence-backed work* and the engine decision.

## How this plan was produced

The v1.0.0 source was read line-by-line and then audited by multi-agent review, cross-checked
against an upstream clone of **SuperFold** (`github.com/Weeks-UNC/Superfold`) and against the
real capabilities of **EternaFold/CONTRAfold** (verified against the local `/opt/EternaFold`
C++ source), **RNAstructure 6.6** (released 2026-04-02), and the 2024–2026 RNA-folding engine
landscape. Every issue cites concrete `file:line` evidence.

## Headline findings

1. **All v1.0.0 engineering lives in one file.** `Ultrafold.py` is the only module that
   diverges from upstream SuperFold; `RNAtools.py`, `batchSubmit.py`, `drawArcRibbons_simple.py`,
   `pvclient.py`, `PyCircleCompareSF.py` are byte-identical to upstream.
2. **The engine swap (RNAstructure → EternaFold) is ~60–65% faithful.** It preserved the
   windowed-consensus skeleton but dropped four `Fold`/`partition` capabilities — and three of
   those are *blocked by EternaFold itself*, not merely unfinished.
3. **Two engine-independent bugs dominate everything else:**
   - The **partition step is sequence-only** — [`Ultrafold.py:586`](../src/ultrafold/Ultrafold.py#L586)
     omits `--evidence`, so the merged dot-plot, the 99% constraint pairs, and the entire
     Shannon-entropy / region analysis ignore the SHAPE/DMS data. (Issue 01)
   - **Everything runs serially** — `batchSubmit` is imported but never called; `--np` is
     ignored. (Issue 02)
4. **EternaFold is still the right engine for this niche.** The entire 2024–2026 deep-learning
   wave is sequence-only at inference and cannot ingest your ShapeMapper2 reactivities. **Do not
   switch to a DL model.**
5. **RNAstructure 6.6 is the natural complement.** It is actively maintained and the only
   mainstream engine with native DMS, hard constraints, max-pairing-distance, and pseudoknots —
   exactly the capabilities EternaFold structurally lacks.
6. **GPU is not the cheap efficiency win.** EternaFold has no GPU path; GPU-native models are
   sequence-only. The real same-science speedup is restoring parallelism (Issue 02), then
   linear-time CPU folding (Issue 14).

## EternaFold capability limits (verified against `/opt/EternaFold` source)

| RNAstructure `Fold`/`partition` capability | EternaFold status | Note |
|---|---|---|
| SHAPE soft restraint | ✅ via `--evidence` | different (learned) model; `--kappa` not exposed |
| SHAPE in **partition** step | ❌ **bug** | `--evidence` omitted (Issue 01) |
| Hard constraints `-C` (99% + ss/pk) | ⛔ **blocked** | `--constraints` and `--evidence` are mutually exclusive (`Contrafold.cpp:688`) |
| Max pairing distance `-md` | ⛔ **blocked** | deliberately removed from EternaFold source |
| Suboptimal ensemble `-m 100` | ⛔ **blocked** | single MEA structure only |
| DMS-specific model `-dmsnt` | ⛔ **blocked** | SHAPE/DMS treated identically; `--DMS` inert |
| Missing-data handling | ❌ bug | raw `-999` piped as evidence (Issue 04) |
| Parallel dispatch | ❌ bug | serial loop (Issue 02) |

## Milestones & issues

### v1.1 — Correctness hotfixes (no engine change; behavior-*correcting*)
- **[01]** Partition step ignores reactivity — add `--evidence` *(critical)*
- **[02]** Restore parallel window dispatch; honor `--np` *(high)*
- **[03]** `runCheck()` validates the wrong toolchain *(high)*
- **[04]** Missing-data sentinels (`-999`/NaN) fed as evidence *(high)*
- **[05]** `concatonateDP` magic-500 / coverage division / partition 3′ gap *(high)*

> ⚠️ These change scientific output (they *correct* it). Land them as **v1.1**, validated
> against v1.0.0 with the bug clearly documented — do **not** silently edit v1.0.0.

### v2.0 — Faithful engine completion & decisions
- **[06]** Decide constraint behavior (EternaFold can't do constraints + evidence together) *(high, design)*
- **[07]** Inert CLI knobs — wire or remove (`--maxPairingDist`, `--SHAPEslope/intercept`, `--trimInterior`, `--DMS`) *(high)*
- **[08]** Add **RNAstructure 6.6** as a parallel cross-validation / capability track *(high)*
- **[09]** Make EternaFold params path configurable; expose `--kappa` *(medium)*

### v2.x — Python 3 port, reproducibility, hygiene
- **[10]** Python 3 port — incl. the silent `np.array(map(...))` hazard *(high)*
- **[11]** Regression harness + CI (golden ESR1 outputs) *(high)*
- **[12]** Reproducibility: `safeName` hashes path string, omits params *(medium)*
- **[13]** Code hygiene — duplicate `mainAssemble`/`CT`, dead writes, `--noPVclient` inversion, "SuperFold" self-ID *(medium)*

### v3.0 — Performance (research)
- **[14]** Evaluate LinearPartition-E (linear-time; needs an evidence C++ port) *(medium)*
- **[15]** GPU / deep-learning — research spike, gated by restraint support *(low)*

## Critical sequencing note

The regression goldens in **Issue 11** must be captured **after** the coverage/`inf` fixes in
**Issue 05** (and ideally after Issues 01/04), otherwise the harness will canonize corrupt
output as the reference — which would also make the ROADMAP's "validate byte-for-byte against
v1.0.0" goal validate *against bugs*.

## Engine decision summary

**Keep EternaFold as the primary evidence engine; add RNAstructure 6.6 as a parallel track;
do not adopt a deep-learning engine; treat GPU as a separate long-term research direction.**
Rationale and alternatives ranked in Issue 08 and the assessment that produced this plan.
