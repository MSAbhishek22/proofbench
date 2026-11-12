import http.client
import json
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app.server as server_module  # noqa: E402
from app.server import Handler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402


class ServerTests(unittest.TestCase):
    def setUp(self):
        server_module.STATE.update(
            {"pack": None, "plan": None, "kane_import": None})

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def req(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        payload = json.dumps(body) if body is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        conn.request(method, path, payload, headers)
        res = conn.getresponse()
        raw = res.read()
        conn.close()
        return res.status, raw

    def test_health(self):
        status, raw = self.req("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["app"], "proofbench")

    def test_homepage_serves_bench(self):
        status, raw = self.req("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"PROOFBENCH", raw)
        self.assertIn(b"AWAITING FIRST KANE RUN", raw)

    def test_verify_rejects_empty_spec(self):
        status, raw = self.req("POST", "/api/verify", {"spec": "  "})
        self.assertEqual(status, 400)

    def test_kane_status_starts_awaiting(self):
        status, raw = self.req("GET", "/api/kane/status")
        data = json.loads(raw)
        self.assertEqual(data["state"], "awaiting_first_run")

    def test_full_loop_and_kane_import(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "sample", "spec.md"),
                encoding="utf-8") as fh:
            spec = fh.read()
        status, raw = self.req("POST", "/api/verify", {"spec": spec})
        self.assertEqual(status, 200)
        pack = json.loads(raw)["pack"]
        self.assertEqual(pack["summary"]["total_claims"], 10)

        status, raw = self.req("GET", "/api/kane-plan.json")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["format"], "kane-verify/test-plan")

        status, raw = self.req("POST", "/api/kane/import",
                               {"results": [{"check_id": "CHK-01",
                                             "status": "PASS",
                                             "output": "ok"}]})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["state"], "imported")

        status, raw = self.req("POST", "/api/kane/import",
                               {"results": [{"check_id": "CHK-01",
                                             "status": "MAYBE"}]})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
