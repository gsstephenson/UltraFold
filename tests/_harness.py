"""Shared helpers for the UltraFold regression harness (Python 3).

The end-to-end golden tests drive the real pipeline (the same way a user does)
on a small, fixed ESR1 slice and compare the merged outputs against committed
golden files. They require the external folding tools + DATAPATH and therefore
skip automatically on machines (e.g. CI) that don't have them. The pure-Python
unit tests in test_unit.py need only numpy (+ pandas/matplotlib to import the
main module) and run anywhere.
"""

import os
import sys
import glob
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "src", "ultrafold")
TEST_INPUT = os.path.join(HERE, "data", "esr1_1650.map")
INPUT_NAME = "esr1_1650.map"
GOLDEN_DIR = os.path.join(HERE, "golden")

# The merged outputs we treat as the regression surface. Filenames carry a
# safeName md5 hash derived from the input filename + params, so we resolve them
# by glob rather than hardcoding the hash.
MERGED_PATTERNS = [("dp", "merged_*.dp"), ("ct", "merged_*.ct"), ("shannon", "shannon_*.txt")]


def tool_available(name):
    try:
        subprocess.call([name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except OSError:
        return False


def datapath_ok():
    dp = os.environ.get("DATAPATH")
    return bool(dp) and os.path.isdir(dp)


def eternafold_available():
    return tool_available("contrafold") and tool_available("dot2ct") and datapath_ok()


def rnastructure_available():
    return (all(tool_available(t) for t in ("Fold", "partition", "ProbabilityPlot"))
            and tool_available("dot2ct") and datapath_ok())


def run_pipeline(engine, nprocs, workdir):
    """Run UltraFold on the fixed test input inside ``workdir``.

    Returns (returncode, {key: path_or_None}) for the merged dp / ct / shannon
    outputs. Output is isolated to workdir so concurrent/repeat runs don't clash.
    """
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    shutil.copy(TEST_INPUT, os.path.join(workdir, INPUT_NAME))

    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, os.path.join(SRC, "Ultrafold.py"), INPUT_NAME,
           "--DMS", "--noPVclient", "--np", str(nprocs), "--engine", engine]
    logpath = os.path.join(workdir, "run.log")
    with open(logpath, "w") as log:
        rc = subprocess.call(cmd, cwd=workdir, stdout=log, stderr=subprocess.STDOUT)

    results = os.path.join(workdir, "results")
    out = {}
    for key, pat in MERGED_PATTERNS:
        hits = glob.glob(os.path.join(results, pat))
        out[key] = hits[0] if hits else None
    return rc, out


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def files_identical(a, b):
    if a is None or b is None or not os.path.exists(a) or not os.path.exists(b):
        return False
    return read_bytes(a) == read_bytes(b)


def golden_path(engine, key):
    ext = {"dp": "merged.dp", "ct": "merged.ct", "shannon": "shannon.txt"}[key]
    return os.path.join(GOLDEN_DIR, engine, ext)
