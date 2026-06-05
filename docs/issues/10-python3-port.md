# Python 3 port — including the silent `np.array(map(...))` hazard

<!-- labels: port, high -->
<!-- milestone: v2.x -->

## Summary
Port `Ultrafold.py` (and the helper modules) to Python 3. Two classes of change:

1. **Hard import failures (mechanical):** `print` statements, `xrange`, `open(..., 'rU')`
   (removed in 3.11+), `hashlib.md5().update(str)` (needs bytes), `dict.keys()` iteration during
   mutation, `subprocess.communicate()` bytes vs str.
2. **Silent numeric corruption (dangerous):** `map()`/`range()` stored as object attributes and
   later sliced/indexed/`len`'d. Most raise `TypeError`, **but `np.array(map(...))` at
   [`Ultrafold.py:835`](../../src/ultrafold/Ultrafold.py#L835) silently yields a 0-d object array**,
   so `origSHAPE` becomes garbage and all SHAPE plotting/coloring is wrong **without crashing**.

> Note: the ROADMAP emphasizes integer division, but the audit confirmed scientifically-relevant
> divisions are already float-protected. Redirect that attention to the iterator/object-array
> hazards above.

## Evidence
- `xrange`: `RNAtools.py:349,396`, `PyCircleCompareSF.py:314,361`, `drawArcRibbons_simple.py:87,235`
- `print` statements: pervasive in all modules.
- `'rU'` mode: `Ultrafold.py:91,731`; `RNAtools.py:505,531`; `pvclient.py:207`; `drawArcRibbons_simple.py:412,430`
- `hashlib.update(str)`: [`Ultrafold.py:880-891`](../../src/ultrafold/Ultrafold.py#L880-L891)
- Silent hazard: [`Ultrafold.py:835`](../../src/ultrafold/Ultrafold.py#L835); stored maps `:72-74,904-907`.
- `readSeq` returns undefined `processed` (latent `NameError`): `RNAtools.py:542`.

## Proposed approach
- Do the mechanical sweep first (syntax), then a careful pass wrapping every stored
  `map()`/`range()` in `list(...)`.
- Port on a dedicated `v2`/`py3-port` branch.
- **Gate the port on the regression harness (Issue 11)** — validate output against v1.x goldens
  within documented tolerance before merge.

## Acceptance criteria
- [ ] All modules import and run under Python 3.11+.
- [ ] ESR1 output matches the v1.x golden within tolerance (esp. `origSHAPE`/SHAPE plots).
- [ ] `readSeq` fixed or removed.

## References
99-agent audit (py2to3 dimension); v2 plan headline.
