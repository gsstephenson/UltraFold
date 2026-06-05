# UltraFold regression tests

A safety net for the Python 2.7 reference implementation: pure-Python unit tests
plus end-to-end golden-output tests on a fixed ESR1 slice. Goldens are captured
from **v1.1.1** (the first release whose default-engine output is correct).

## Layout

| Path | What |
|------|------|
| `test_unit.py` | Pure-Python tests (RNAtools `CT`/`dotPlot`, the `create_bpp2seq` no-data sanitizer). Needs only numpy (+ pandas/matplotlib to import the main module). Runs anywhere. |
| `test_e2e_golden.py` | Runs the real pipeline on `data/esr1_1650.map` and byte-compares the merged `.dp` / `.ct` / `shannon` to `golden/`. Also checks `--np 4` == `--np 1` (Fix #2 determinism). **Skips** if the folding tools / `DATAPATH` are missing. |
| `update_goldens.py` | Regenerate goldens (run deliberately). |
| `_harness.py` | Shared helpers. |
| `data/esr1_1650.map` | Fixed test input (first 1650 nt of the ESR1 example — exercises multi-window merge and the 3′-coverage fix). |
| `golden/<engine>/` | Reference `merged.dp` / `merged.ct` / `shannon.txt` per engine. |

## Running

The reference implementation is **Python 2.7** — use a py2.7 interpreter (e.g. the
`py2-MaP` conda env).

```bash
# unit tests only (no external tools needed)
make test PYTHON=~/anaconda3/envs/py2-MaP/bin/python

# end-to-end golden tests (needs contrafold + dot2ct + DATAPATH on PATH/env)
export DATAPATH=/path/to/RNAstructure/data_tables
make test-e2e PYTHON=~/anaconda3/envs/py2-MaP/bin/python

# include the (slow) RNAstructure engine e2e
UF_TEST_RNASTRUCTURE=1 make test-e2e PYTHON=~/anaconda3/envs/py2-MaP/bin/python
```

CI (`.github/workflows/ci.yml`) runs the unit tests under a py2.7 conda env; the
e2e tests skip there because the folding binaries aren't installed.

## Goldens are tool-version-specific

The `.dp` / `.ct` / `shannon` references depend on the installed EternaFold /
RNAstructure versions. When you intentionally change behavior (or move to a
machine with different tool versions), regenerate and commit them together with
the change that motivated it:

```bash
python update_goldens.py --engines eternafold rnastructure
```

Never regenerate goldens just to make a failing test pass — a diff against the
golden means either a real regression or a deliberate, reviewed behavior change.
