import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.runner import pack_integrity, pack_to_markdown, run_bench, verify_pack  # noqa: E402
from app.target import DemoTarget, get_target  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "sample", "spec.md")


class StubTarget(DemoTarget):
    """A target where we control the truth, to prove FAILs are real."""

    def supports(self, subject):
        return subject == "teleportation"


class RunnerTests(unittest.TestCase):
    def setUp(self):
        with open(SAMPLE, encoding="utf-8") as fh:
            self.pack = run_bench(fh.read(), get_target("demo"))

    def test_sample_verdict_is_disputed(self):
        self.assertEqual(self.pack["verdict"], "SPEC DISPUTED")

    def test_sample_counts(self):
        s = self.pack["summary"]
        self.assertEqual((s["total_claims"], s["passed"], s["failed"]),
                         (10, 7, 3))

    def test_known_pass_and_known_fail(self):
        by_claim = {r["claim_id"]: r for r in self.pack["results"]}
        self.assertEqual(by_claim["CLM-01"]["status"], "PASS")   # csv export
        self.assertEqual(by_claim["CLM-02"]["status"], "FAIL")   # pdf export
        self.assertEqual(by_claim["CLM-02"]["observed"], "not supported")
        self.assertEqual(by_claim["CLM-05"]["observed"], "25 MB")  # upload lie
        self.assertEqual(by_claim["CLM-10"]["status"], "FAIL")   # webhooks lie

    def test_deliberately_failing_claim_fails(self):
        pack = run_bench("Product supports teleportation.\n"
                         "Product supports csv export.\n", StubTarget())
        by_kind = {r["claim_id"]: r for r in pack["results"]}
        self.assertEqual(by_kind["CLM-01"]["status"], "PASS")
        self.assertEqual(by_kind["CLM-02"]["status"], "FAIL")
        self.assertEqual(pack["verdict"], "SPEC DISPUTED")

    def test_all_true_spec_holds(self):
        pack = run_bench("LedgerLite supports CSV export.\n"
                         "GET /health returns status 200.\n", get_target("demo"))
        self.assertEqual(pack["verdict"], "SPEC HOLDS")

    def test_pack_integrity_verifies(self):
        self.assertTrue(verify_pack(self.pack))
        self.assertEqual(self.pack["integrity_sha256"], pack_integrity(self.pack))

    def test_tampered_pack_fails_integrity(self):
        self.pack["results"][0]["observed"] = "tampered value"
        self.assertFalse(verify_pack(self.pack))

    def test_markdown_pack_contains_claims_and_verdict(self):
        md = pack_to_markdown(self.pack)
        self.assertIn("SPEC DISPUTED", md)
        self.assertIn("CLM-02", md)
        self.assertIn("Unparsed lines", md)
        self.assertIn(self.pack["integrity_sha256"], md)


if __name__ == "__main__":
    unittest.main()
