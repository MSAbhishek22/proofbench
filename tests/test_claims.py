import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.claims import extract_claims  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "sample", "spec.md")


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        with open(SAMPLE, encoding="utf-8") as fh:
            self.result = extract_claims(fh.read())

    def test_sample_yields_ten_claims(self):
        self.assertEqual(len(self.result["claims"]), 10)

    def test_sample_types_in_order(self):
        types = [c["type"] for c in self.result["claims"]]
        self.assertEqual(types, [
            "supports", "supports", "endpoint_status", "endpoint_contains",
            "value_equals", "value_equals", "latency_max", "requires_auth",
            "never", "not_supports",
        ])

    def test_support_subject_strips_of_phrase(self):
        c = self.result["claims"][0]
        self.assertEqual(c["subject"], "csv export")

    def test_value_claim_fields(self):
        c = self.result["claims"][4]
        self.assertEqual((c["label"], c["expected_value"], c["unit"]),
                         ("upload size", 10, "MB"))

    def test_line_numbers_point_at_source(self):
        for claim in self.result["claims"]:
            self.assertGreaterEqual(claim["line"], 3)
            self.assertTrue(claim["source"])

    def test_marketing_line_is_unparsed_not_dropped(self):
        unparsed = self.result["unparsed"]
        self.assertEqual(len(unparsed), 1)
        self.assertIn("friendliest", unparsed[0]["source"])

    def test_heading_and_blanks_skipped(self):
        result = extract_claims("# Title\n\n\nProduct supports CSV export.\n")
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(result["unparsed"], [])

    def test_empty_spec(self):
        result = extract_claims("   \n\n")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["unparsed"], [])


if __name__ == "__main__":
    unittest.main()
