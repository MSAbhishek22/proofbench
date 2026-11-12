import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.checks import build_kane_plan, generate_checks  # noqa: E402
from app.claims import extract_claims  # noqa: E402


class GenerationTests(unittest.TestCase):
    def setUp(self):
        claims = extract_claims(
            "Product supports CSV export.\nGET /health returns status 200.\n"
        )["claims"]
        self.claims = claims
        self.checks = generate_checks(claims)

    def test_one_check_per_claim(self):
        self.assertEqual(len(self.checks), len(self.claims))

    def test_check_ids_unique_and_ordered(self):
        ids = [c["id"] for c in self.checks]
        self.assertEqual(ids, ["CHK-01", "CHK-02"])
        self.assertEqual([c["claim_id"] for c in self.checks],
                         [c["id"] for c in self.claims])

    def test_check_description_is_human_sentence(self):
        self.assertIn("csv export", self.checks[0]["description"])
        self.assertIn("200", self.checks[1]["description"])

    def test_kane_plan_shape_and_honesty(self):
        plan = build_kane_plan(self.claims, self.checks, "demo target")
        self.assertEqual(plan["format"], "kane-verify/test-plan")
        self.assertEqual(len(plan["steps"]), 2)
        self.assertEqual(plan["steps"][0]["claim_text"],
                         "Product supports CSV export.")
        # The plan must never claim to be a native Kane script.
        self.assertIn("Not a native Kane script", plan["adapter_note"])


if __name__ == "__main__":
    unittest.main()
