"""Check generation: exactly one executable check per extracted claim.

A check is data, not code strings — the runner dispatches on `kind`, and
the same check list is what gets exported as the Kane test plan.
"""
from __future__ import annotations

_DESCRIBE = {
    "supports": "Measure whether the target supports '{subject}'.",
    "not_supports": "Measure whether the target does NOT support '{subject}'.",
    "never": "Measure whether the target never does this: '{phrase}'.",
    "endpoint_status": "Call {method} {path}; expect HTTP {expected_status}.",
    "endpoint_contains": "Call {method} {path}; expect the body to contain '{token}'.",
    "value_equals": "Read the target's '{label}'; expect {expected_value} {unit}.",
    "latency_max": "Measure response latency; expect at most {max_ms} ms.",
    "requires_auth": "Measure whether the target requires authentication.",
}


def generate_checks(claims: list[dict]) -> list[dict]:
    """One check per claim, ids CHK-01…, order preserved."""
    checks = []
    for i, claim in enumerate(claims, start=1):
        template = _DESCRIBE[claim["type"]]
        checks.append({
            "id": f"CHK-{i:02d}",
            "claim_id": claim["id"],
            "kind": claim["type"],
            "description": template.format(**claim),
            "params": {k: v for k, v in claim.items()
                       if k not in ("id", "line", "source", "type")},
        })
    return checks


def build_kane_plan(claims: list[dict], checks: list[dict],
                    target_name: str) -> dict:
    """Export the run as a Kane test plan.

    FORMAT NOTE (honest): Kane CLI's native script format was not available
    when this adapter was written, so this exports ProofBench's documented
    JSON test-plan format ("kane-verify/test-plan v1") — the stable input
    the Kane adapter maps from, one step per generated check. It does NOT
    claim to be a native Kane script.
    """
    by_id = {c["id"]: c for c in claims}
    steps = []
    for check in checks:
        claim = by_id[check["claim_id"]]
        steps.append({
            "step_id": check["id"],
            "claim_id": claim["id"],
            "claim_text": claim["source"],
            "action": check["kind"],
            "params": check["params"],
            "expect": check["description"],
        })
    return {
        "format": "kane-verify/test-plan",
        "version": 1,
        "adapter_note": ("ProofBench JSON test plan — the input the Kane CLI "
                         "adapter maps from. Not a native Kane script; the "
                         "mapping is written once the real Kane CLI is in hand."),
        "target": target_name,
        "steps": steps,
    }
