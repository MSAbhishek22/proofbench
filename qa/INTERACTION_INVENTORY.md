# Interaction Inventory — ProofBench
Written 12 Nov 2026 (scaffold night). Statuses reflect what was actually
exercised: automated HTTP smoke + unit tests against the real server.
Browser click-through is still owed before release (see BUILD_PLAN.md).

| # | Page / component | User action | Expected behaviour | Implementation | Validation / errors | Evidence | Status |
|---|---|---|---|---|---|---|---|
| 1 | 01 SPECIMEN — textarea `#spec-input` | Paste/type a spec | Text accepted, monospace, resizable | `app/static/index.html` + `app.js` | Empty spec on run → inline error, no request sent | test_server empty-spec 400 (server side); client guard in app.js | PASS (API) / browser check pending |
| 2 | 01 — LOAD SAMPLE SPEC button | Click | Bundled sample spec loads into the textarea | GET `/api/sample-spec` → textarea | Load failure → inline error text | curl smoke: sample fetched and run end-to-end | PASS |
| 3 | 01 — CALIBRATE button | Click | Button disables + "MEASURING…", run state → MEASURING → COMPLETE, claims/results/verdict render | POST `/api/verify` → `renderPack()` | Empty spec → error; server error → error text + run state ERROR; button always re-enabled | HTTP smoke: full loop, verdict SPEC DISPUTED, 10 claims, 7 PASS / 3 FAIL | PASS (API) / browser check pending |
| 4 | 02 — Claims table | (display) | One row per claim: id, measured description, source line, check id | Rendered from pack.claims/checks | — | Smoke pack contained all 10 claims with line refs | PASS |
| 5 | 02 — Unparsed list | (display) | Non-claim lines listed in amber, never dropped | Rendered from pack.unparsed | — | Smoke: marketing line L13 listed | PASS |
| 6 | 03 — Result trace (SVG) | (display) | One segment per check, up = PASS, down = FAIL; static under reduced-motion | `drawTrace()` in app.js; CSS reduced-motion rule | No results → hidden | Code-reviewed; visual pass pending | BLOCKED (visual check owed) |
| 7 | 03 — Results table + summary readout | (display) | Claim → expected → observed → PASS/FAIL chip (word + glyph, never colour-only) | Rendered from pack.results | — | Smoke output matched ground truth incl. 3 FAILs | PASS |
| 8 | Header — verdict readout | (display) | Shows SPEC HOLDS / SPEC DISPUTED after a run; — NO RUN — before | `renderPack()` | — | Smoke verdict verified server-side | PASS |
| 9 | 04 — Evidence Pack (.JSON) download | Click | Downloads the real last pack; disabled-looking before any run | GET `/api/pack.json` (409 before a run) | Before run: aria-disabled + endpoint 409 | Endpoint exercised in test_server (plan) and pack verified via /api/verify | PASS |
| 10 | 04 — Evidence Pack (.MD) download | Click | Downloads Markdown evidence pack | GET `/api/pack.md` | 409 before a run | curl smoke: Markdown rendered with verdict + hashes | PASS |
| 11 | 05 — Kane test plan download | Click | Downloads `kane-verify/test-plan v1` JSON | GET `/api/kane-plan.json` | 409 before a run | curl smoke: plan head verified, adapter_note honest | PASS |
| 12 | 05 — Kane status readout | (display) | AWAITING FIRST KANE RUN until an import exists; then IMPORTED — PROVENANCE NOT VERIFIED | GET `/api/kane/status` | — | curl smoke: both states observed | PASS |
| 13 | 05 — Kane results file input | Choose a JSON file | Valid file imports and renders a results table; invalid file/status → inline error, state unchanged | POST `/api/kane/import` with server-side validation | Bad status value → 400 (smoke-verified); malformed JSON → error | curl smoke: import 200, bad import 400 | PASS (API) / browser check pending |

Known gaps (honest): no real-browser click-through yet; the trace's draw
animation is code-reviewed only; Kane import accepts a documented generic
results shape because Kane CLI's real output format is not yet in hand —
it is an import interface, not a claim that a Kane run happened.
