# Tracked issues

These are the planned work items from the 2026 codebase assessment, one file per issue, in
GitHub-issue format. See [`../v2_plan.md`](../v2_plan.md) for the milestones and rationale.

Each file's front matter lists a suggested **title**, **labels**, and **milestone**. The body
has: Summary → Evidence (`file:line`) → Why it matters → Proposed fix → Acceptance criteria.

## Bulk-create on GitHub

`gh` is not yet installed in this environment. Once it is (`gh auth login` against
`github.com/gsstephenson/UltraFold`), create every issue from these files:

```bash
cd docs/issues
for f in [0-9][0-9]-*.md; do
  title=$(sed -n 's/^# //p' "$f" | head -1)
  gh issue create --title "$title" --body-file "$f"
done
```

Or create labels/milestones first, then pass `--label`/`--milestone` per file.

## Index

| # | Title | Milestone | Priority |
|---|---|---|---|
| 01 | Partition step ignores reactivity (`--evidence` missing) | v1.0.1 | critical |
| 02 | Restore parallel window dispatch; honor `--np` | v1.0.1 | high |
| 03 | `runCheck()` validates the wrong toolchain | v1.0.1 | high |
| 04 | Missing-data sentinels (`-999`/NaN) fed to the engine as evidence | v1.0.1 | high |
| 05 | `concatonateDP` magic-500 / coverage division / partition 3′ gap | v1.0.1 | high |
| 06 | Decide constraint behavior (EternaFold constraints⊕evidence) | v2.0 | high |
| 07 | Inert CLI knobs — wire or remove | v2.0 | high |
| 08 | Add RNAstructure 6.6 as a parallel cross-validation track | v2.0 | high |
| 09 | Configurable EternaFold params path; expose `--kappa` | v2.0 | medium |
| 10 | Python 3 port (incl. silent `np.array(map(...))` hazard) | v2.x | high |
| 11 | Regression harness + CI (golden ESR1 outputs) | v2.x | high |
| 12 | Reproducible `safeName` (hash contents + full params) | v2.x | medium |
| 13 | Code hygiene (duplicate defs, dead writes, flag inversion) | v2.x | medium |
| 14 | Evaluate LinearPartition-E (linear-time; needs evidence port) | v3.0 | medium |
| 15 | GPU / deep-learning research spike | v3.0 | low |
