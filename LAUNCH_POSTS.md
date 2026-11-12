# ProofBench — Launch Post Drafts

**Status: DRAFTS — not posted anywhere.** Written 12 Nov 2026 for the Kane CLI
Online Hackathon submission (Step 04 at kaneclihack.sh, due 19 Nov 23:59 IST),
which requires **≥2 public launch posts**.

**Placeholders filled in 12 Nov 2026:** the live URL
(https://proofbench-xi.vercel.app) and the public repo
(https://github.com/MSAbhishek22/proofbench) are both real now, and the X
character count below was re-measured with them in place (X counts each URL
as 23 characters). Still drafts — post only on the user's go.

Honesty note baked into both drafts: they say the checks *export as a Kane test
plan* — true today. They do **not** claim a completed Kane CLI run; per
`KANE_RUN_REPORT.md`, Kane runs are gated on the account login, which is still
pending. If the authenticated Kane run lands before posting, one line can be
upgraded — with the real run output as the source.

---

## (a) X post — 273 / 280 characters

(With the real URLs in, the draft measured 288 — over the limit. Two minimal
trims brought it to 273: "paste a product spec" → "paste a spec", and "seals
the results into" → "seals them into".)

```
Specs lie politely. ProofBench makes them prove it.

Built for the Kane CLI Hackathon: paste a spec, ProofBench extracts its claims, tests them against the app, and seals them into a tamper-evident evidence pack.

Live: https://proofbench-xi.vercel.app
Code: https://github.com/MSAbhishek22/proofbench
```

## (b) LinkedIn post — 3 short paragraphs

```
Every product spec makes claims nobody checks. "Supports PDF export." "Responds within 200 ms." "Never stores passwords in plain text." They read fine — until a user finds out the hard way.

ProofBench makes specs prove it. Paste a spec and it deterministically extracts the testable claims, generates a check for each one, runs them against the target, and seals the results into an evidence pack (JSON + Markdown) with an integrity hash. Its bundled demo target's spec lies three times — ProofBench catches all three.

I built ProofBench for the Kane CLI Online Hackathon by TestMu AI; the same checks export as a Kane test plan, so they can run under Kane CLI as well. Try the live bench: https://proofbench-xi.vercel.app · Code: https://github.com/MSAbhishek22/proofbench
```
