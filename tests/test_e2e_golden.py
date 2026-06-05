"""End-to-end regression tests: run the real pipeline on a fixed ESR1 slice and
compare the merged dp / ct / shannon outputs to committed goldens.

These require the external folding tools + DATAPATH and SKIP automatically when
they're absent (e.g. on CI). The RNAstructure engine is much slower, so its test
is opt-in via UF_TEST_RNASTRUCTURE=1.

Regenerate goldens with: python tests/update_goldens.py [--engines ...]
"""

import os
import tempfile
import shutil
import unittest

import _harness as H


class EternaFoldGolden(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not H.eternafold_available():
            raise unittest.SkipTest("EternaFold tools (contrafold/dot2ct) or DATAPATH not available")
        for key, _ in H.MERGED_PATTERNS:
            if not os.path.exists(H.golden_path("eternafold", key)):
                raise unittest.SkipTest("eternafold goldens missing; run tests/update_goldens.py")
        cls.workdir = tempfile.mkdtemp(prefix="uf_e2e_ef_")
        cls.rc, cls.out = H.run_pipeline("eternafold", nprocs=4, workdir=cls.workdir)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "workdir", None) and os.path.isdir(cls.workdir):
            shutil.rmtree(cls.workdir)

    def test_pipeline_succeeded(self):
        self.assertEqual(self.rc, 0, "pipeline exited non-zero; see run.log")
        for key, _ in H.MERGED_PATTERNS:
            self.assertIsNotNone(self.out[key], "missing merged output: %s" % key)

    def test_dotplot_matches_golden(self):
        self.assertTrue(H.files_identical(self.out["dp"], H.golden_path("eternafold", "dp")),
                        "merged .dp differs from golden (eternafold)")

    def test_structure_matches_golden(self):
        self.assertTrue(H.files_identical(self.out["ct"], H.golden_path("eternafold", "ct")),
                        "merged .ct differs from golden (eternafold)")

    def test_shannon_matches_golden(self):
        self.assertTrue(H.files_identical(self.out["shannon"], H.golden_path("eternafold", "shannon")),
                        "shannon entropy differs from golden (eternafold)")

    def test_np_determinism(self):
        # Fix #2 invariant: parallel window dispatch must be byte-identical to serial.
        wd = tempfile.mkdtemp(prefix="uf_e2e_ef_np1_")
        try:
            rc1, out1 = H.run_pipeline("eternafold", nprocs=1, workdir=wd)
            self.assertEqual(rc1, 0)
            for key, _ in H.MERGED_PATTERNS:
                self.assertTrue(H.files_identical(self.out[key], out1[key]),
                                "np=4 vs np=1 differ for %s (non-deterministic dispatch)" % key)
        finally:
            shutil.rmtree(wd)


@unittest.skipUnless(os.environ.get("UF_TEST_RNASTRUCTURE") == "1",
                     "set UF_TEST_RNASTRUCTURE=1 to run the slow RNAstructure golden test")
class RNAstructureGolden(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not H.rnastructure_available():
            raise unittest.SkipTest("RNAstructure tools or DATAPATH not available")
        for key, _ in H.MERGED_PATTERNS:
            if not os.path.exists(H.golden_path("rnastructure", key)):
                raise unittest.SkipTest("rnastructure goldens missing; run tests/update_goldens.py --engines rnastructure")
        cls.workdir = tempfile.mkdtemp(prefix="uf_e2e_rs_")
        cls.rc, cls.out = H.run_pipeline("rnastructure", nprocs=4, workdir=cls.workdir)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "workdir", None) and os.path.isdir(cls.workdir):
            shutil.rmtree(cls.workdir)

    def test_matches_goldens(self):
        self.assertEqual(self.rc, 0, "pipeline exited non-zero; see run.log")
        for key, _ in H.MERGED_PATTERNS:
            self.assertTrue(H.files_identical(self.out[key], H.golden_path("rnastructure", key)),
                            "%s differs from golden (rnastructure)" % key)


if __name__ == "__main__":
    unittest.main()
