# Inert CLI knobs — wire them in or remove them

<!-- labels: design, high, docs -->
<!-- milestone: v2.0 -->

## Summary
Several documented CLI options are parsed and threaded through function signatures but never
reach the executed `contrafold` command, so tuning them changes only the output directory name
(via the `safeName` hash), not the result. This is an invisible reproducibility/validity trap.

## Inert options (verified)
| Flag | Status | Note |
|---|---|---|
| `--maxPairingDist` | inert | no EternaFold flag; not post-filtered (see Issue 05) |
| `--SHAPEslope` / `--SHAPEintercept` | inert | EternaFold uses learned evidence, not Deigan slope/intercept |
| `--trimInterior` | inert | trimming hardcoded to `trim=300` in `mainAssemble` |
| `--DMS` | inert | EternaFold treats SHAPE/DMS identically; command unchanged |

## Evidence
- Params accepted but unused in engine fns: [`Ultrafold.py:488`](../../src/ultrafold/Ultrafold.py#L488), [`:562`](../../src/ultrafold/Ultrafold.py#L562)
- `--trimInterior` parsed ([`:820`](../../src/ultrafold/Ultrafold.py#L820)) but `mainAssemble(... trim=300)` hardcoded ([`:622`](../../src/ultrafold/Ultrafold.py#L622)).
- `--DMS` never branches inside the engine fns (no `usedms` conditional).

## Proposed fix (per knob)
- `--maxPairingDist`: implement as a post-filter on merged pairs (`|i-j| ≤ maxDist`) — ties to Issue 05 — or route through the RNAstructure track (Issue 08) where `-md` is native.
- `--trimInterior`: pass the parsed value into `mainAssemble` instead of the literal `300`.
- `--SHAPEslope/intercept`: remove from the EternaFold path (meaningless), or keep only on the RNAstructure track where Deigan params apply.
- `--DMS`: only meaningful on the RNAstructure track (`-dmsnt`); on the EternaFold path, document that it has no effect (or remove).

## Acceptance criteria
- [ ] Every advertised flag either measurably changes output or is removed/marked no-op in `-h` and README.
- [ ] No flag silently affects only the `safeName` directory.

## References
v2 plan EternaFold-limits table; gap analysis "inert tuning knobs".
