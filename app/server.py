"""ProofBench server — Python 3 stdlib only, no dependencies.

Run from the project root:
    python3 run.py            # http://127.0.0.1:8773
    python3 -m app.server

Routes:
  GET  /                      index.html
  GET  /static/<file>         style.css / app.js
  GET  /health                {"status": "ok", ...}
  GET  /api/sample-spec       the bundled sample spec (plain text)
  POST /api/verify            {spec, target} -> evidence pack (JSON)
  GET  /api/pack.json         last evidence pack (download)
  GET  /api/pack.md           last evidence pack as Markdown (download)
  GET  /api/kane-plan.json    last run exported as a Kane test plan
  GET  /api/kane/status       Kane channel state (awaiting / imported)
  POST /api/kane/import       {results: [{check_id, status, output}]}
                              -> stores IMPORTED external results.
                              Imported != produced by Kane: the response and
                              the UI both label provenance as unverified.
"""
from __future__ import annotations

import json
import mimetypes
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.checks import build_kane_plan
from app.runner import pack_to_markdown, run_bench
from app.target import get_target

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SAMPLE_SPEC = os.path.join(BASE_DIR, "sample", "spec.md")
PORT = 8773
HOST = "127.0.0.1"

# In-memory bench state (single-user demo tool; restart clears it).
STATE: dict = {"pack": None, "plan": None, "kane_import": None}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, body: bytes, ctype: str, status: int = 200,
              filename: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if filename:
            self.send_header("Content-Disposition",
                             f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, status: int = 200,
              filename: str | None = None) -> None:
        self._send(json.dumps(payload, ensure_ascii=False, indent=2).encode(),
                   "application/json; charset=utf-8", status, filename)

    def _static(self, name: str) -> None:
        safe = os.path.basename(name)
        path = os.path.join(STATIC_DIR, safe)
        if not os.path.exists(path):
            self._json({"ok": False, "error": "Not found."}, 404)
            return
        with open(path, "rb") as fh:
            body = fh.read()
        ctype, _ = mimetypes.guess_type(path)
        self._send(body, ctype or "application/octet-stream")

    def _body_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return None

    # -- GET ------------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            if path == "/":
                self._static("index.html")
                return
            if path.startswith("/static/"):
                self._static(path[len("/static/"):])
                return
            if path == "/favicon.ico":
                self.send_response(204)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if path == "/health":
                self._json({"ok": True, "status": "ok", "app": "proofbench",
                            "target": "bundled demo target (simulated)"})
                return
            if path == "/api/sample-spec":
                with open(SAMPLE_SPEC, encoding="utf-8") as fh:
                    self._send(fh.read().encode(), "text/plain; charset=utf-8")
                return
            if path == "/api/pack.json":
                if STATE["pack"] is None:
                    self._json({"ok": False,
                                "error": "No run yet — calibrate first."}, 409)
                    return
                self._json(STATE["pack"], filename="evidence-pack.json")
                return
            if path == "/api/pack.md":
                if STATE["pack"] is None:
                    self._json({"ok": False,
                                "error": "No run yet — calibrate first."}, 409)
                    return
                self._send(pack_to_markdown(STATE["pack"]).encode(),
                           "text/markdown; charset=utf-8", 200,
                           "evidence-pack.md")
                return
            if path == "/api/kane-plan.json":
                if STATE["plan"] is None:
                    self._json({"ok": False,
                                "error": "No run yet — calibrate first."}, 409)
                    return
                self._json(STATE["plan"], filename="kane-test-plan.json")
                return
            if path == "/api/kane/status":
                self._json(self._kane_status())
                return
        except Exception as exc:  # never leak a stack trace to the client
            self._json({"ok": False, "error": f"Server error: {exc}"}, 500)
            return
        self._json({"ok": False, "error": "Not found."}, 404)

    def _kane_status(self) -> dict:
        if STATE["kane_import"] is None:
            return {"ok": True, "state": "awaiting_first_run",
                    "label": "AWAITING FIRST KANE RUN",
                    "detail": ("No Kane CLI results have been imported yet. "
                               "Export the test plan, run it with Kane CLI, "
                               "then import the results file here.")}
        return {"ok": True, "state": "imported",
                "label": "IMPORTED RESULTS — PROVENANCE NOT VERIFIED",
                "detail": ("These results were imported from a user-supplied "
                           "file. ProofBench has not verified that Kane CLI "
                           "produced them."),
                "results": STATE["kane_import"]}

    # -- POST -----------------------------------------------------------
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path == "/api/verify":
                data = self._body_json()
                if data is None:
                    self._json({"ok": False, "error": "Malformed JSON body."}, 400)
                    return
                spec = (data.get("spec") or "").strip()
                if not spec:
                    self._json({"ok": False,
                                "error": "Spec is empty — paste at least one claim line."},
                               400)
                    return
                try:
                    target = get_target(data.get("target") or "demo")
                except ValueError as exc:
                    self._json({"ok": False, "error": str(exc)}, 400)
                    return
                pack = run_bench(spec, target)
                STATE["pack"] = pack
                STATE["plan"] = build_kane_plan(pack["claims"], pack["checks"],
                                                 target.name)
                self._json({"ok": True, "pack": pack})
                return
            if path == "/api/kane/import":
                data = self._body_json()
                if data is None or not isinstance(data.get("results"), list):
                    self._json({"ok": False,
                                "error": "Expected JSON: {results: [{check_id, status, output}]}."},
                               400)
                    return
                cleaned = []
                for row in data["results"]:
                    if not isinstance(row, dict) or "check_id" not in row \
                            or row.get("status") not in ("PASS", "FAIL"):
                        self._json({"ok": False,
                                    "error": "Each result needs check_id and status PASS or FAIL."},
                                   400)
                        return
                    cleaned.append({"check_id": str(row["check_id"]),
                                    "status": row["status"],
                                    "output": str(row.get("output", ""))})
                STATE["kane_import"] = cleaned
                self._json(self._kane_status())
                return
        except Exception as exc:
            self._json({"ok": False, "error": f"Server error: {exc}"}, 500)
            return
        self._json({"ok": False, "error": "Not found."}, 404)


def main(host: str = HOST, port: int = PORT) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"ProofBench listening on http://{host}:{port}")
    print("Target: bundled demo target (simulated ground truth)")
    server.serve_forever()


if __name__ == "__main__":
    main()
