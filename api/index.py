"""ProofBench on Vercel — WSGI entrypoint (serverless adaptation).

The bench logic is unchanged (app/claims.py + app/checks.py +
app/runner.py + app/target.py: same claim extraction, same check
generation, same evidence packs, same bundled demo target); this file
is only a transport adapter. Vercel's Python runtime calls
``app(environ, start_response)``.

Route-for-route parity with app/server.py (same paths, same JSON
shapes — including its ``indent=2`` encoding — same status codes, same
error strings, same download filenames). The earlier
BaseHTTPRequestHandler shim is gone: Vercel's current Python runtime
rejected it with ``[unused_function]`` because it defines no callable
serverless entrypoint in this file.

The one piece of mutable state is the bench's last-run store
(``STATE`` below: last evidence pack, last Kane plan, imported Kane
results) — a module-level in-memory dict, identical in shape to
app/server.py's. On serverless it lives only for the life of the warm
instance: the pack/plan/Kane-import can differ across instances and
vanish on a cold start, so a ``/api/pack.json`` on a fresh instance
honestly answers 409 "No run yet — calibrate first." That is an
accepted demo caveat (single-user bench, simulated target); locally
the behaviour is identical to app/server.py. The only other
difference: no server process — each request is handled by this WSGI
app. No credentials, no environment variables, no external assets, no
secrets.
"""

import json
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.checks import build_kane_plan  # noqa: E402
from app.runner import pack_to_markdown, run_bench  # noqa: E402
from app.target import get_target  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
SAMPLE_SPEC = os.path.join(BASE_DIR, "sample", "spec.md")

# In-memory bench state (single-user demo tool; restart clears it).
# Mirrors STATE in app/server.py; on serverless it is per warm instance
# only — see the module docstring.
STATE: dict = {"pack": None, "plan": None, "kane_import": None}

_JSON = "application/json; charset=utf-8"


def _json_body(payload: dict) -> bytes:
    # Same encoding as app/server.py's _json (indent=2).
    return json.dumps(payload, ensure_ascii=False, indent=2).encode()


def _json(payload: dict, status: int = 200, filename: str | None = None):
    extra = []
    if filename:
        extra.append(("Content-Disposition",
                      f'attachment; filename="{filename}"'))
    return status, _JSON, _json_body(payload), extra


def _static(name: str):
    safe = os.path.basename(name)
    path = os.path.join(STATIC_DIR, safe)
    if not os.path.exists(path):
        return _json({"ok": False, "error": "Not found."}, 404)
    with open(path, "rb") as fh:
        body = fh.read()
    ctype, _ = mimetypes.guess_type(path)
    return 200, ctype or "application/octet-stream", body, []


def _kane_status() -> dict:
    # Same shapes as app/server.py's Handler._kane_status.
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


def handle_get(path: str):
    if path == "/":
        return _static("index.html")
    if path.startswith("/static/"):
        return _static(path[len("/static/"):])
    if path == "/favicon.ico":
        return 204, "text/plain", b"", []
    if path == "/health":
        return _json({"ok": True, "status": "ok", "app": "proofbench",
                      "target": "bundled demo target (simulated)"})
    if path == "/api/sample-spec":
        with open(SAMPLE_SPEC, encoding="utf-8") as fh:
            return 200, "text/plain; charset=utf-8", fh.read().encode(), []
    if path == "/api/pack.json":
        if STATE["pack"] is None:
            return _json({"ok": False,
                          "error": "No run yet — calibrate first."}, 409)
        return _json(STATE["pack"], filename="evidence-pack.json")
    if path == "/api/pack.md":
        if STATE["pack"] is None:
            return _json({"ok": False,
                          "error": "No run yet — calibrate first."}, 409)
        return (200, "text/markdown; charset=utf-8",
                pack_to_markdown(STATE["pack"]).encode(),
                [("Content-Disposition",
                  'attachment; filename="evidence-pack.md"')])
    if path == "/api/kane-plan.json":
        if STATE["plan"] is None:
            return _json({"ok": False,
                          "error": "No run yet — calibrate first."}, 409)
        return _json(STATE["plan"], filename="kane-test-plan.json")
    if path == "/api/kane/status":
        return _json(_kane_status())
    return _json({"ok": False, "error": "Not found."}, 404)


def _read_json(environ):
    """Mirror of app/server.py's _body_json: parsed body, or None.

    None covers both an unparseable body and a JSON ``null`` body,
    exactly as in the local server.
    """
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(length) if length > 0 else b""
        return json.loads(raw or b"{}")
    except (ValueError, json.JSONDecodeError):
        return None


def handle_post(path: str, environ):
    if path == "/api/verify":
        data = _read_json(environ)
        if data is None:
            return _json({"ok": False, "error": "Malformed JSON body."}, 400)
        spec = (data.get("spec") or "").strip()
        if not spec:
            return _json({"ok": False,
                          "error": "Spec is empty — paste at least one claim line."},
                         400)
        try:
            target = get_target(data.get("target") or "demo")
        except ValueError as exc:
            return _json({"ok": False, "error": str(exc)}, 400)
        pack = run_bench(spec, target)
        STATE["pack"] = pack
        STATE["plan"] = build_kane_plan(pack["claims"], pack["checks"],
                                         target.name)
        return _json({"ok": True, "pack": pack})
    if path == "/api/kane/import":
        data = _read_json(environ)
        if data is None or not isinstance(data.get("results"), list):
            return _json({"ok": False,
                          "error": "Expected JSON: {results: [{check_id, status, output}]}."},
                         400)
        cleaned = []
        for row in data["results"]:
            if not isinstance(row, dict) or "check_id" not in row \
                    or row.get("status") not in ("PASS", "FAIL"):
                return _json({"ok": False,
                              "error": "Each result needs check_id and status PASS or FAIL."},
                             400)
            cleaned.append({"check_id": str(row["check_id"]),
                            "status": row["status"],
                            "output": str(row.get("output", ""))})
        STATE["kane_import"] = cleaned
        return _json(_kane_status())
    return _json({"ok": False, "error": "Not found."}, 404)


_STATUSES = {
    200: "200 OK", 204: "204 No Content", 400: "400 Bad Request",
    404: "404 Not Found", 409: "409 Conflict",
    500: "500 Internal Server Error",
}


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    raw_path = environ.get("PATH_INFO", "/") or "/"
    # Vercel rewrites /(.*) to /api/index: treat the function root as app root.
    path = "/" if raw_path in ("/api/index", "/api") else raw_path
    try:
        if method == "GET":
            code, ctype, body, extra = handle_get(path)
        elif method == "POST":
            code, ctype, body, extra = handle_post(path, environ)
        else:
            code, ctype, body, extra = _json(
                {"ok": False, "error": "Not found."}, 404)
    except Exception as exc:  # never leak a stack trace to the client
        code, ctype, body, extra = _json(
            {"ok": False, "error": f"Server error: {exc}"}, 500)
    start_response(_STATUSES.get(code, "200 OK"),
                   [("Content-Type", ctype),
                    ("Content-Length", str(len(body)))] + extra)
    return [body]
