# ProofBench — Build Plan to Submission
**Event:** Kane CLI Online Hackathon (TestMu AI) · $3,000 ($1,500/$1,000/$500)
**Deadline: Thu 19 Nov 2026, 23:59 IST.** Fresh-build rule: repo must be
initialised on/after 12 Nov 2026, commit history checked — all code in this
folder was written fresh on 12 Nov 2026, and nothing was copied from any
earlier project.

## Done — scaffold night (12 Nov)
- [x] Core loop end-to-end: spec → extraction (8 patterns) → check
      generation → runner → evidence pack (JSON + Markdown, integrity hash)
- [x] Bundled demo target (LedgerLite) with 3 deliberate spec lies
- [x] Kane test-plan export (`kane-verify/test-plan v1`) + honest
      AWAITING/import channel (validated, provenance-labelled)
- [x] Bench UI in the calibration-instrument identity (design constitution
      + registry written before code)
- [x] 25/25 tests PASS; full HTTP smoke PASS (health, verify, pack.md,
      plan, import, bad-import 400)

## Done — night 2 (12 Nov)
- [x] **Kane CLI attempted for real** (`KANE_RUN_REPORT.md`, verbatim logs):
      `@testmuai/kane-cli` installs cleanly from npm (v0.10.4) and the binary
      works — no demo/upgrade gate in the tool. BUT every account operation is
      hard-gated on login: `kane-cli run` against the local ProofBench target
      stopped with "Not authenticated. Run: kane-cli login --oauth, or
      kane-cli login --username <user> --access-key <key>". **Unblock (user's
      hand, one step):** TestMu username + access key from
      accounts.lambdatest.com → Credentials, handed over via Secure Vault —
      then `login` → `whoami`/`balance` → run the exported plan. OAuth needs
      the user's own browser. Kane channel stays AWAITING until then.
- [x] **Git initialised fresh** (12 Nov, per the fresh-build rule) — first
      commit `9971d56` on `main`, 23 files, `.gitignore` excludes
      `__pycache__`/`.venv`/secrets. No remote yet, nothing pushed.
- [x] **Launch-post drafts ready** (`LAUNCH_POSTS.md`) — X post (259/280
      chars) + LinkedIn post, with `[LIVE LINK]` / `[REPO]` placeholders;
      nothing posted.

## Next steps, in order
1. **Real-browser pass** — click through every control in
   `qa/INTERACTION_INVENTORY.md`, check the trace animation, mobile
   viewport, keyboard-only run. Update inventory statuses with evidence.
2. **GitHub repo** — local init DONE 12 Nov (commit `9971d56`, see above).
   Still to do: create the public repo, push, confirm it renders and the
   README reads clean.
3. **Deploy** — free-tier host that runs a Python stdlib server (or adapt
   to the host's model); verify the LIVE URL end-to-end as a stranger:
   sample spec → CALIBRATE → 7 PASS / 3 FAIL → downloads work. Record the
   deployed commit SHA in `deployment/RELEASE_MANIFEST.json` and write
   `deployment/DEPLOYMENT_RUNBOOK.md`.
4. **Kane CLI integration — the judging core** — credits have landed
   (11,000 TestMu credits on the user's registered account); the gate is now
   **credentials, not credits** (see `KANE_RUN_REPORT.md`): login needs the
   username + access key from accounts.lambdatest.com → Credentials (via
   Secure Vault) or an OAuth approval in the user's own browser.
   - Get the real Kane CLI — DONE 12 Nov: installed (v0.10.4), help/version
     captured in `KANE_RUN_REPORT.md`. Still to learn from the tool itself,
     post-login: its actual script format and result output (do not guess).
   - Write the adapter mapping `kane-verify/test-plan v1` steps → native
     Kane scripts, pointed at the deployed ProofBench target.
   - Run it for real. Aim for the two judged moments: (a) Kane catching a
     bug / a green run against the app, (b) an agent↔Kane feedback moment
     (Kane result changes something — e.g. the imported results panel
     disagreeing with or confirming the local bench).
   - Wire the import to Kane's real output shape; keep the provenance
     label honest until the import is genuinely Kane-produced, then say so.
5. **Demo video (~3 min, from the LIVE URL only)** — script: spec lies
   politely (0:00) → paste sample spec, CALIBRATE, 3 FAILs caught (0:30) →
   evidence pack + integrity hash (1:20) → export plan, Kane CLI runs
   against the app, results land in the Kane channel (1:50) → verdict +
   closing line (2:45). Record `submission/DEMO_VIDEO_MANIFEST.md` with
   the production URL + commit SHA.
6. **Submit** — public repo + live URL + video + ≥2 public launch posts
   (drafts ready in `LAUNCH_POSTS.md` — post once the live URL and public
   repo exist, swap the placeholders, re-check the X character count) + the
   one paragraph:
   "Specs lie politely; ProofBench makes them prove it — claims are
   extracted deterministically, checked against the target, sealed into a
   tamper-evident evidence pack, and the same checks run under Kane CLI."

## Risks / watch-items
- Step 4 is gated on the user's access key / OAuth approval, NOT on credits
  (11,000 already on the account; balance becomes verifiable only after
  login). Everything else must be finished so the Kane day is only about Kane.
- If Kane's format forces check-model changes, the runner's kind-dispatch
  is the single seam to change; extraction and pack stay untouched.
- Rulebook gates still open: Gate C visual check, Gate E deploy + commit
  match, Gate F live-recorded video. Status today: **IN_PROGRESS**.
