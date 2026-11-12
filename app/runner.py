"""The runner: execute checks against a target, build the evidence pack.

An evidence pack is the product's output: claim -> check -> result, with
the observed value recorded verbatim, plus a SHA-256 integrity hash over
the claims and results so a pack can be checked for tampering.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from app.checks import generate_checks
from app.claims import extract_claims


def _run_one(check: dict, target) -> dict:
    kind, p = check["kind"], check["params"]
    if kind == "supports":
        observed = target.supports(p["subject"])
        passed = observed is True
        expected_s, observed_s = "supported", "supported" if observed else "not supported"
    elif kind == "not_supports":
        observed = target.supports(p["subject"])
        passed = observed is False
        expected_s = "not supported"
        observed_s = "supported" if observed else "not supported"
    elif kind == "never":
        passed = target.never_holds(p["phrase"])
        expected_s, observed_s = "never happens", "holds" if passed else "VIOLATED"
    elif kind == "endpoint_status":
        status, _body = target.endpoint(p["method"], p["path"])
        passed = status == p["expected_status"]
        expected_s, observed_s = f"HTTP {p['expected_status']}", f"HTTP {status}"
    elif kind == "endpoint_contains":
        _status, body = target.endpoint(p["method"], p["path"])
        passed = p["token"] in body
        expected_s = f"body containing '{p['token']}'"
        observed_s = body[:80]
    elif kind == "value_equals":
        found = target.value_for(p["label"])
        if found is None:
            passed, observed_s = False, "no such value on target"
        else:
            value, unit = found
            passed = value == p["expected_value"] and unit == p["unit"]
            observed_s = f"{value} {unit}"
        expected_s = f"{p['expected_value']} {p['unit']}"
    elif kind == "latency_max":
        observed_ms = target.latency_ms()
        passed = observed_ms <= p["max_ms"]
        expected_s, observed_s = f"<= {p['max_ms']} ms", f"{observed_ms} ms"
    elif kind == "requires_auth":
        observed = target.requires_auth()
        passed = observed is True
        expected_s = "authentication required"
        observed_s = "authentication required" if observed else "no authentication"
    else:  # pragma: no cover - generate_checks only emits known kinds
        raise ValueError(f"Unknown check kind: {kind}")
    return {
        "check_id": check["id"],
        "claim_id": check["claim_id"],
        "kind": kind,
        "status": "PASS" if passed else "FAIL",
        "expected": expected_s,
        "observed": observed_s,
    }


def run_bench(spec_text: str, target) -> dict:
    """Full loop: extract -> generate -> run -> evidence pack."""
    extracted = extract_claims(spec_text)
    claims, unparsed = extracted["claims"], extracted["unparsed"]
    checks = generate_checks(claims)
    results = [_run_one(check, target) for check in checks]
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    pack = {
        "pack_version": 1,
        "product": "ProofBench",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": {"name": target.name, "kind": target.kind},
        "spec_sha256": hashlib.sha256(spec_text.encode("utf-8")).hexdigest(),
        "claims": claims,
        "checks": checks,
        "results": results,
        "unparsed": unparsed,
        "summary": {"total_claims": len(claims), "passed": passed,
                    "failed": failed, "unparsed_lines": len(unparsed)},
        "verdict": "SPEC HOLDS" if failed == 0 and claims else "SPEC DISPUTED",
    }
    pack["integrity_sha256"] = pack_integrity(pack)
    return pack


def pack_integrity(pack: dict) -> str:
    """SHA-256 over the canonical claims+results (the parts that matter)."""
    canonical = json.dumps(
        {"claims": pack["claims"], "results": pack["results"]},
        sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_pack(pack: dict) -> bool:
    return pack.get("integrity_sha256") == pack_integrity(pack)


def pack_to_markdown(pack: dict) -> str:
    s = pack["summary"]
    lines = [
        "# Evidence Pack — ProofBench",
        "",
        f"- Generated: {pack['generated_at']}",
        f"- Target: {pack['target']['name']}",
        f"- Spec SHA-256: `{pack['spec_sha256']}`",
        f"- Pack integrity SHA-256: `{pack['integrity_sha256']}`",
        f"- Verdict: **{pack['verdict']}** "
        f"({s['passed']}/{s['total_claims']} claims passed, "
        f"{s['unparsed_lines']} unparsed lines)",
        "",
        "## Claim → check → result",
        "",
        "| Claim | Source (line) | Check | Expected | Observed | Result |",
        "|---|---|---|---|---|---|",
    ]
    claims = {c["id"]: c for c in pack["claims"]}
    checks = {c["id"]: c for c in pack["checks"]}
    for r in pack["results"]:
        claim = claims[r["claim_id"]]
        check = checks[r["check_id"]]
        lines.append(
            f"| {claim['id']} | {claim['source']} (L{claim['line']}) "
            f"| {check['description']} | {r['expected']} | {r['observed']} "
            f"| **{r['status']}** |")
    if pack["unparsed"]:
        lines += ["", "## Unparsed lines (reported, never silently dropped)", ""]
        for u in pack["unparsed"]:
            lines.append(f"- L{u['line']}: {u['source']}")
    lines.append("")
    return "\n".join(lines)
