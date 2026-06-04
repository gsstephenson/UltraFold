# Contributing to UltraFold

Thanks for your interest in improving UltraFold!

## Important: the v1.0.0 reference implementation is frozen

`src/ultrafold/` at version 1.0.0 is the **Python 2.7 reference implementation**
used to produce published results. To protect reproducibility:

- **Do not make algorithmic changes to v1.0.0.** Bug-for-bug fidelity matters
  for anyone reproducing or citing published work.
- Modernization (Python 3, dependency upgrades, GPU, refactors) happens in new
  versions, validated against v1.0.0 output. See [ROADMAP.md](ROADMAP.md).

## Where changes go

| Change | Where |
|--------|-------|
| Docs, examples, packaging metadata | anytime, any version |
| New helper utilities | `tools/` |
| Python 3 port | a dedicated `py3-port` branch / `v2` line |
| Performance / GPU work | post-v2, on its own branch |

## Development setup (v1.0.0)

v1.0.0 requires **Python 2.7**:

```bash
conda create -n ultrafold-py27 python=2.7
conda activate ultrafold-py27
pip install -r requirements.txt
```

You will also need the external tools on your `PATH` — see
[docs/external_tools.md](docs/external_tools.md).

## Validation expectation for ports

Any Python 3 port (or dependency change) must reproduce v1.0.0 output on the
bundled example (and ideally a larger reference set) within documented
tolerance **before** it is merged. Pay particular attention to Python 2/3
integer-division differences.

## Pull requests

- Keep PRs focused and describe what you changed and why.
- Note explicitly whether a change affects scientific output.
- Update `CHANGELOG.md` and bump the version where appropriate.
