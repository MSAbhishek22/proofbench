"""Deterministic claim extraction from a product spec.

No LLM, no guessing. A line becomes a claim only if it matches one of the
documented sentence patterns below; every other non-empty line is reported
back as UNPARSED so nothing is silently dropped.

Supported patterns (case-insensitive, trailing full stop optional):
  1. "<Product> supports X" / "support for X"          -> supports
  2. "<Product> does not support X" / "no support for" -> not_supports
  3. "<Product> never <phrase>"                        -> never
  4. "GET /path returns status 200" / "returns 200"    -> endpoint_status
  5. "GET /path returns a body containing <token>"     -> endpoint_contains
  6. "<label> is <N> <unit>"  (unit: MB, days, items)  -> value_equals
  7. "responds within <N> ms" / "under <N> ms"         -> latency_max
  8. "requires authentication"                         -> requires_auth
"""
from __future__ import annotations

import re

_HEADING = re.compile(r"^\s*#")
_NEG_SUPPORT = re.compile(
    r"(?:does not support|doesn't support|no support for)\s+(.+?)\s*$", re.I)
_NEVER = re.compile(r"\bnever\s+(.+?)\s*$", re.I)
_SUPPORT = re.compile(r"\bsupports?\s+(?:for\s+)?(.+?)\s*$", re.I)
_STATUS = re.compile(
    r"\b(GET|POST|PUT|DELETE)\s+(/\S+)\s+returns\s+(?:status\s+)?(\d{3})\b", re.I)
_CONTAINS = re.compile(
    r"\b(GET|POST|PUT|DELETE)\s+(/\S+)\s+returns\s+.*?containing\s+(.+?)\s*$", re.I)
_VALUE = re.compile(
    r"\b(.+?)\s+is\s+(\d+)\s*(MB|GB|days|items|users)\b", re.I)
_LATENCY = re.compile(r"\bresponds?\s+(?:within|in under|under)\s+(\d+)\s*ms\b", re.I)
_AUTH = re.compile(r"\brequires?\s+authentication\b", re.I)


def _clean(text: str) -> str:
    """Normalise a captured phrase: lowercase, single spaces, no full stop."""
    text = text.strip().rstrip(".")
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def _subject(raw: str) -> str:
    """A support subject ends at ' of ...' ('CSV export of all reports')."""
    text = _clean(raw)
    text = re.split(r"\s+of\s+", text, maxsplit=1)[0]
    return text.strip()


def extract_claims(spec_text: str) -> dict:
    """Return {'claims': [...], 'unparsed': [...]} for a spec text.

    Each claim: {id, line, source, type, ...type-specific fields}.
    Each unparsed entry: {line, source}.
    """
    claims: list[dict] = []
    unparsed: list[dict] = []
    for lineno, raw_line in enumerate(spec_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or _HEADING.match(line):
            continue
        claim = _match_line(line)
        if claim is None:
            unparsed.append({"line": lineno, "source": line})
        else:
            claim["line"] = lineno
            claim["source"] = line
            claims.append(claim)
    for i, claim in enumerate(claims, start=1):
        claim["id"] = f"CLM-{i:02d}"
    return {"claims": claims, "unparsed": unparsed}


def _match_line(line: str) -> dict | None:
    m = _NEG_SUPPORT.search(line)
    if m:
        return {"type": "not_supports", "subject": _subject(m.group(1))}
    m = _NEVER.search(line)
    if m:
        return {"type": "never", "phrase": _clean(m.group(1))}
    m = _STATUS.search(line)
    if m:
        return {"type": "endpoint_status", "method": m.group(1).upper(),
                "path": m.group(2), "expected_status": int(m.group(3))}
    m = _CONTAINS.search(line)
    if m:
        return {"type": "endpoint_contains", "method": m.group(1).upper(),
                "path": m.group(2), "token": _clean(m.group(3))}
    m = _LATENCY.search(line)
    if m:
        return {"type": "latency_max", "max_ms": int(m.group(1))}
    m = _VALUE.search(line)
    if m:
        label = _clean(m.group(1))
        previous = None
        while previous != label:  # strip stacked prefixes: "the maximum …"
            previous = label
            label = re.sub(r"^(the\s+|maximum\s+|max\s+|data\s+)", "", label)
        return {"type": "value_equals", "label": label,
                "expected_value": int(m.group(2)), "unit": m.group(3)}
    if _AUTH.search(line):
        return {"type": "requires_auth"}
    m = _SUPPORT.search(line)
    if m:
        return {"type": "supports", "subject": _subject(m.group(1))}
    return None
