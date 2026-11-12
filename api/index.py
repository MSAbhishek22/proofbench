"""ProofBench on Vercel — BaseHTTPRequestHandler entrypoint (thin shim).

Vercel's Python runtime serves a ``BaseHTTPRequestHandler`` subclass
named ``handler`` from this file. The entire app stays in app/server.py;
this file only re-exports its Handler under the name Vercel looks for.

Path safety: app/server.py resolves every filesystem path from its own
``__file__`` (BASE_DIR / STATIC_DIR / SAMPLE_SPEC), never from the
process working directory, so the handler behaves identically no matter
where Vercel starts the function from. The only cwd-sensitive step is
importing the ``app`` package itself, so the project root (this file's
parent's parent) is put on ``sys.path`` first — the same defensive
pattern as the user's other Vercel Python adapters.

State caveat (inherited from app/server.py, unchanged): the bench keeps
its last evidence pack in a module-level in-memory dict. On serverless
that state lives only for the life of a warm instance and can differ
across instances; locally the behaviour is identical to run.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.server import Handler as handler  # noqa: E402,F401
