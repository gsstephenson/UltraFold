# Restore parallel window dispatch; honor `--np`

<!-- labels: bug, performance, high -->
<!-- milestone: v1.0.1 -->

## Summary
The per-window `contrafold` jobs are embarrassingly parallel but run **serially**. `batchSubmit`
is imported but never called, and `--np` is parsed but ignored. A multi-kb mRNA therefore runs
as hundreds of serial, single-threaded folds.

## Evidence
- `import batchSubmit as batch` then never used: [`Ultrafold.py:40`](../../src/ultrafold/Ultrafold.py#L40)
- Serial fold loop: [`:537-545`](../../src/ultrafold/Ultrafold.py#L537-L545)
- Serial partition loop: [`:600-607`](../../src/ultrafold/Ultrafold.py#L600-L607)
- `--np` defined ([`:815`](../../src/ultrafold/Ultrafold.py#L815)) and threaded but never reaches dispatch.

## Why it matters
This is the single biggest **same-science** efficiency win (and the practical answer to "GPU
acceleration"): near-linear speedup of ≈`min(nWindows, nCores)` with byte-identical results.

## Proposed fix
Replace the serial `Popen().communicate()` loops with `concurrent.futures.ProcessPoolExecutor(max_workers=args.np)`.
Two integration details:
- The fold loop calls `convert_db_to_ct` per iteration ([`:545`](../../src/ultrafold/Ultrafold.py#L545)) — move conversion to **after** the pool drains.
- Add an explicit **barrier** so `mainAssemble`/`MasterModel_*` run only after all windows finish.

Prefer stdlib over the in-tree `batchSubmit.py` (busy-wait, hardcoded 24-slot cap, swallowed
exceptions). If `batchSubmit.py` is kept, fix `updateJobs` (references global `currJobs`, ignores
its `currentJobs` arg) and the `[0]*24` cap.

## Acceptance criteria
- [ ] `--np N` runs up to N windows concurrently; wall-clock drops ~linearly with cores.
- [ ] Output is **byte-identical** to the serial run on ESR1 (deterministic DP, unique filenames).
- [ ] A failed window is surfaced (not silently swallowed) — see Issue 13 for error handling.

## References
v2 plan headline finding #3 and #6; GPU/efficiency study "Lever A, Step 1".
