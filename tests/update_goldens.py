#!/usr/bin/env python
"""Regenerate the committed golden outputs for the end-to-end regression tests.

Run this DELIBERATELY, only when you intend to bless new reference output (e.g.
after a vetted behavior change, or to (re)capture on a machine with the folding
tools). It runs the real pipeline on tests/data/esr1_1650.map for each engine
and copies the merged dp / ct / shannon files into tests/golden/<engine>/.

    python tests/update_goldens.py                 # eternafold (default)
    python tests/update_goldens.py --engines eternafold rnastructure

Requires the external tools + DATAPATH for the chosen engine(s). Goldens are
specific to the installed EternaFold / RNAstructure versions on this machine;
commit them together with the code/tool state they were captured from.
"""

import argparse
import os
import shutil
import sys
import tempfile

import _harness as H


def regenerate(engine):
    avail = H.eternafold_available() if engine == "eternafold" else H.rnastructure_available()
    if not avail:
        print "[skip] {0}: required tools / DATAPATH not available".format(engine)
        return False
    workdir = tempfile.mkdtemp(prefix="uf_golden_{0}_".format(engine))
    print "[run ] {0} engine in {1} ...".format(engine, workdir)
    rc, out = H.run_pipeline(engine, nprocs=4, workdir=workdir)
    if rc != 0 or any(out[k] is None for k, _ in H.MERGED_PATTERNS):
        print "[FAIL] {0}: pipeline rc={1}, outputs={2} (see {3}/run.log)".format(
            engine, rc, out, workdir)
        return False
    dest = os.path.join(H.GOLDEN_DIR, engine)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for key, _pat in H.MERGED_PATTERNS:
        shutil.copy(out[key], H.golden_path(engine, key))
    shutil.rmtree(workdir)
    print "[ ok ] {0}: goldens written to {1}".format(engine, dest)
    return True


def main():
    ap = argparse.ArgumentParser(description="Regenerate UltraFold golden test outputs.")
    ap.add_argument("--engines", nargs="+", default=["eternafold"],
                    choices=["eternafold", "rnastructure"],
                    help="which engine goldens to regenerate (default: eternafold)")
    args = ap.parse_args()
    ok = True
    for eng in args.engines:
        ok = regenerate(eng) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
