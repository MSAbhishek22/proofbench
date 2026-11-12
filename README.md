# ProofBench — requirements that test themselves

**Specs lie politely.** A spec says "supports PDF export", "uploads up to
10 MB", "responds within 200 ms" — and everyone nods, and the lies ship.
ProofBench makes a spec *prove it*: paste the spec in, and the bench
extracts its verifiable claims, generates one executable check per claim,
measures them against the target, and hands back an **evidence pack** —
claim → check → observed result — sealed with a SHA-256 integrity hash.

Built for the **Kane CLI Online Hackathon** (TestMu AI), Lane 4 —
*Requirements that test themselves*. The generated checks export as a
documented JSON test plan, ready to be driven by **Kane CLI**; Kane's
results import back into the same bench, next to the local measurements.

**Live:** https://proofbench-xi.vercel.app · **Code:** https://github.com/MSAbhishek22/proofbench

## The demo in 30 seconds

The bundled target is **LedgerLite**, a fictional accounting API with known
ground truth. Its sample spec (`sample/spec.md`) makes 10 claims. The bench
measures all 10 and reports **7 PASS · 3 FAIL — SPEC DISPUTED**:

- "supports PDF export" → **FAIL** (not supported)
- "maximum upload size is 10 MB" → **FAIL** (observed 25 MB)
- "does not support webhooks" → **FAIL** (it does)

A bench that never reports FAIL proves nothing. This one catches the spec
lying three times before your users do.

## How it works

1. **Extract** — deterministic, rule-based parsing (no LLM, no guessing).
   Eight documented sentence patterns (`supports X`, `GET /p returns 200`,
   `responds within N ms`, `never …`, …). Anything else is reported as
   UNPARSED — never silently dropped.
2. **Generate** — exactly one check per claim, as data, with a human
   sentence describing what will be measured.
3. **Measure** — the runner executes each check against a target adapter
   and records the observed value *verbatim*.
4. **Seal** — the evidence pack (JSON + Markdown) carries the spec's
   SHA-256 and an integrity hash over claims+results; `verify_pack()`
   detects tampering.
5. **Hand to Kane** — the same checks export as `kane-verify/test-plan v1`
   JSON for the Kane CLI adapter, and external results import back through
   a validated endpoint.

## Run it

```bash
python3 run.py            # http://127.0.0.1:8773 — stdlib only, no installs
python3 -m unittest discover -s tests   # 25 tests
```

Load the sample spec in the UI, hit **CALIBRATE**, and watch the bench
dispute the spec.

## Honest limits (read before believing anything)

- The demo target is **simulated** — deterministic ground truth bundled so
  the bench can be exercised end to end. Real targets plug in by writing a
  new adapter with the same interface as `app/target.py`.
- The Kane export is ProofBench's documented JSON test-plan format — the
  stable input the Kane adapter maps from. It is **not** claimed to be a
  native Kane CLI script: Kane's native format is mapped once the real CLI
  is in hand (see `app/checks.py`).
- **No Kane run has happened yet.** The Kane channel honestly reads
  `AWAITING FIRST KANE RUN` until results are imported, and imported
  results are labelled *provenance not verified* — importing a file is not
  proof Kane produced it.
- Extraction is deliberately narrow: claims outside the 8 patterns are
  unparsed, by design, and shown to the user.

## Layout

```
app/claims.py    deterministic claim extraction (8 patterns)
app/checks.py    one check per claim + Kane test-plan export
app/target.py    bundled demo target (LedgerLite, simulated)
app/runner.py    check execution, evidence pack, integrity hash, Markdown
app/server.py    stdlib HTTP server + API (verify / pack / kane)
app/static/      the bench UI — calibration-instrument identity
design/          design constitution + registry comparison
qa/              interaction inventory
tests/           25 tests: extraction, generation, runner, pack, server
sample/spec.md   the sample spec that lies three times
BUILD_PLAN.md    the road to the 19 Nov deadline
```
