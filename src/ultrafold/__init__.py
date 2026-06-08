"""UltraFold -- windowed RNA secondary-structure modeling from SHAPE/DMS probing data.

v2.x is the Python 3 line. v2.1.0 makes the engine choice reproducible and honest:
the output-directory signature now covers the engine plus the full parameter set, the
EternaFold parameter path and chemical-mapping weight (--kappa) are configurable,
--trimInterior is wired through, RNAstructure-only flags warn under the eternafold
engine, and every run writes a provenance manifest. Reproduces the v1.1.1 reference
within float-repr precision on both engines. The Python 2.7 reference remains frozen
and citable at the v1.0.0 tag. See ``CHANGELOG.md`` / ``ROADMAP.md``.
"""

__version__ = "2.1.0"
__license__ = "GPL-3.0-or-later"
