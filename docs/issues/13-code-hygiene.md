# Code hygiene — duplicate definitions, dead writes, flag inversion, self-ID

<!-- labels: cleanup, medium -->
<!-- milestone: v2.x -->

## Summary
Copy-paste accretion that, beyond being untidy, is a **reproducibility hazard**: a maintainer can
edit a shadowed/dead copy and see no effect. Best cleaned up *before* the Py3 port to reduce
porting surface.

## Items (with evidence)
- **Duplicate `mainAssemble`** — the first def is dead/shadowed; only the second runs, and they
  differ in input glob + coverage semantics. Delete the dead one.
  [`:628-694`](../../src/ultrafold/Ultrafold.py#L628-L694) (dead) vs [`:977-1047`](../../src/ultrafold/Ultrafold.py#L977-L1047) (live).
- **Divergent duplicate `CT` class** — `PyCircleCompareSF.py:50-120` carries its own `CT` with
  opposite `skipConflicting` default vs `RNAtools.CT`. Reconcile to one shared import.
- **Dead startup writes** — `temp_seq_file.seq` ([`:123-134`](../../src/ultrafold/Ultrafold.py#L123-L134)) and
  `profile_data.bpp2seq` ([`:136-138`](../../src/ultrafold/Ultrafold.py#L136-L138)) are written but never read.
- **`--noPVclient` inversion** — `store_false` makes the variable mean the opposite of its name;
  also sets the never-read `args.drawPVclient`. ([`:826`](../../src/ultrafold/Ultrafold.py#L826), [`:277-282`](../../src/ultrafold/Ultrafold.py#L277-L282))
- **Self-identification** — header + argparse description still say "SuperFold v1.0 by Gregg Rice."
  ([`:2`](../../src/ultrafold/Ultrafold.py#L2), [`:810`](../../src/ultrafold/Ultrafold.py#L810))
- **Duplicate imports / dead `debug` branch** — `import os`/`import subprocess` repeated; the
  `debug=False` branch in `main()` is dead.

## Acceptance criteria
- [ ] One `mainAssemble`, one shared `CT` class.
- [ ] Dead writes and duplicate imports removed; `debug` branch removed or made a real flag.
- [ ] `--noPVclient` semantics fixed (or clearly documented) and `drawPVclient` removed.
- [ ] Program self-identifies as UltraFold.
- [ ] ESR1 output unchanged (these are non-behavioral except the flag fix).

## References
99-agent audit (inert-features / engineering); see audit-method memo for the refuted non-bugs.
