# Reproducible `safeName` — hash file contents + the full parameter set

<!-- labels: bug, medium, reproducibility -->
<!-- milestone: v2.x -->

## Summary
`safeName` (which names every output directory/file) hashes the **path string** rather than the
file **contents**, truncates the md5 to 16 bits, and omits several parameters from the hash. As a
result distinct runs can **collide to the same output paths** (overwriting/reusing stale
`fold_*`/`partition_*` dirs), and an output cannot be reliably traced to the inputs that produced
it. Editing the input `.map` in place yields the same name.

## Evidence
- Hash inputs (path string + a subset of params): [`Ultrafold.py:880-891`](../../src/ultrafold/Ultrafold.py#L880-L891)
- Omitted from the hash: `foldStepSize`, `SHAPEslope/intercept`, `np`, `differentialSlope`, `trimInterior`.
- 16-bit truncation: `m.hexdigest()[:4]` ([`:891`](../../src/ultrafold/Ultrafold.py#L891)).

## Proposed fix
- Hash the input file **contents** (stream the `.map`), not the path string.
- Include the **complete** parameter set in the hash.
- Use enough digest bits to make collisions negligible.
- Write the full resolved parameter set + the params-file checksum (Issue 09) into the run log.

## Acceptance criteria
- [ ] Two runs differing in any parameter or in input contents get distinct `safeName`s.
- [ ] Same inputs + same params reproduce the same `safeName`.
- [ ] Run log records the full parameter set used.

## References
99-agent audit (engineering dimension); v2 plan reproducibility risks.
