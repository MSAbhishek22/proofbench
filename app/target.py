"""The bundled demo target: LedgerLite, a fictional mini accounting API.

This is a SIMULATED target with known ground truth, bundled so the bench
can be exercised end to end with no external service. Some of its facts
deliberately disagree with the sample spec — a calibration bench that
never reports FAIL proves nothing.

Ground truth (the sample spec in sample/spec.md disagrees on 3 claims):
  supports csv export ......... yes
  supports pdf export ......... NO        (spec claims it -> FAIL)
  supports webhooks ........... yes       (spec denies it -> FAIL)
  GET /health ................. 200
  GET /receipt body ........... contains receipt_id
  upload size ................. 25 MB     (spec claims 10 MB -> FAIL)
  retention ................... 30 days
  health latency (simulated) .. 142 ms
  requires authentication ..... yes
  stores passwords in plaintext NO (never holds)
"""
from __future__ import annotations

_SUPPORTS = {
    "csv export": True,
    "pdf export": False,
    "webhooks": True,
    "dark mode": True,
}

_ENDPOINTS = {
    ("GET", "/health"): (200, '{"status": "ok"}'),
    ("GET", "/receipt"): (200, '{"receipt_id": "rcpt_9182", "total": 499.00}'),
    ("GET", "/reports"): (200, '{"reports": ["q1", "q2"]}'),
}

_VALUES = {  # keyword -> (value, unit); looked up by keyword containment
    "upload": (25, "MB"),
    "retention": (30, "days"),
}

# Phrases the target VIOLATES (for `never` claims). Empty for plaintext
# passwords: the target never does it, so the claim holds.
_VIOLATIONS: set[str] = set()

_LATENCY_MS = 142  # deterministic simulated measurement


class DemoTarget:
    """Adapter the runner measures. Swap this class for a real target."""

    name = "LedgerLite (bundled demo target — simulated ground truth)"
    kind = "demo"

    def supports(self, subject: str) -> bool:
        return _SUPPORTS.get(subject, False)

    def endpoint(self, method: str, path: str) -> tuple[int, str]:
        return _ENDPOINTS.get((method, path), (404, '{"error": "not found"}'))

    def value_for(self, label: str) -> tuple[int, str] | None:
        for keyword, value in _VALUES.items():
            if keyword in label:
                return value
        return None

    def latency_ms(self) -> int:
        return _LATENCY_MS

    def requires_auth(self) -> bool:
        return True

    def never_holds(self, phrase: str) -> bool:
        return phrase not in _VIOLATIONS


def get_target(name: str = "demo") -> DemoTarget:
    if name != "demo":
        raise ValueError(f"Unknown target: {name!r} (only 'demo' is bundled)")
    return DemoTarget()
