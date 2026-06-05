"""Pure-Python unit tests (no external folding tools required).

Covers the core data structures (RNAtools CT / dotPlot) and the v1.1.1
missing-data sanitizer in create_bpp2seq. RNAtools needs only numpy; the
sanitizer test imports the main module (numpy/pandas/matplotlib) and skips
cleanly if those aren't importable.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "ultrafold")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from RNAtools import CT, dotPlot


class TestDotPlot(unittest.TestCase):

    def _dp(self, length, i, j, logbp):
        dp = dotPlot()
        dp.length = length
        dp.dp['i'] = np.array(i, dtype=float)
        dp.dp['j'] = np.array(j, dtype=float)
        dp.dp['logBP'] = np.array(logbp, dtype=float)
        return dp

    def test_writedp_readdp_roundtrip(self):
        dp = self._dp(10, [2, 1], [8, 9], [1.0, 0.5])
        f = tempfile.mktemp(suffix=".dp")
        dp.writeDP(f)
        dp2 = dotPlot(f)
        os.remove(f)
        self.assertEqual(dp2.length, 10)
        self.assertEqual(sorted(dp2.pairList()), [(1, 9), (2, 8)])

    def test_requireprob_band(self):
        dp = self._dp(20, [1, 2, 3], [10, 11, 12], [0.5, 2.0, 5.0])
        # requireProb(min) keeps entries with 0 < logBP < min (smaller logBP = more probable)
        self.assertEqual(len(dp.requireProb(3.0).pairList()), 2)
        self.assertEqual(len(dp.requireProb(1.0).pairList()), 1)

    def test_calcshannon_shape(self):
        dp = self._dp(12, [1, 2], [12, 11], [0.3, 0.7])
        sh = dp.calcShannon()
        self.assertEqual(len(sh), 12)
        self.assertTrue(all(x >= 0 for x in sh))


class TestCT(unittest.TestCase):

    def test_pair2ct_pairlist(self):
        ct = CT()
        ct.pair2CT([(1, 10), (2, 9)], list("ACGUACGUAC"))
        self.assertEqual(sorted(ct.pairList()), [(1, 10), (2, 9)])

    def test_cutct_inclusive_renumber(self):
        ct = CT()
        ct.pair2CT([(1, 10), (2, 9), (3, 8)], list("ACGUACGUAC"))
        sub = ct.cutCT(2, 9)  # inclusive 8-nt window
        self.assertEqual(len(sub.seq), 8)
        # (2,9)->(1,8) and (3,8)->(2,7); (1,10) straddles the window and is dropped
        self.assertEqual(sorted(sub.pairList()), [(1, 8), (2, 7)])


class TestBpp2seqSanitize(unittest.TestCase):
    """v1.1.1 #4: no-data reactivity must become EternaFold's -1.0, never a raw
    -999 / NaN / +/-inf written as a real evidence value."""

    def setUp(self):
        try:
            import Ultrafold
            self.U = Ultrafold
        except Exception as e:  # heavy deps (pandas/matplotlib) unavailable
            self.skipTest("cannot import Ultrafold: %s" % e)

    def test_no_data_mapped_to_minus_one(self):
        U = self.U
        m = U.shapeMAP(None)
        m.seq = list("ACGUACGUAC")  # 10 nt
        m.shape = [0.5, -999.0, 0.0, float('nan'), float('inf'), float('-inf'), 1.8, 0.0, 0.2, 0.9]
        f = tempfile.mktemp(suffix=".bpp2seq")
        U.create_bpp2seq(m, 1, 10, f)
        vals = [float(line.rstrip("\n").split("\t")[3]) for line in open(f)]
        os.remove(f)
        self.assertEqual(len(vals), 10)
        # 1-based positions 2 (-999), 4 (nan), 5 (+inf), 6 (-inf) -> -1.0
        for idx in (1, 3, 4, 5):
            self.assertEqual(vals[idx], -1.0)
        # genuine values pass through unchanged
        self.assertEqual(vals[0], 0.5)
        self.assertEqual(vals[6], 1.8)
        self.assertEqual(vals[2], 0.0)
        # nothing more negative than the -1 sentinel and no inf leaked
        for v in vals:
            self.assertFalse(v < -1.0)
            self.assertNotEqual(v, float('inf'))
            self.assertEqual(v, v)  # not NaN


if __name__ == "__main__":
    unittest.main()
