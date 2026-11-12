# Kane CLI — Real Run Report (honest, verbatim)

**Date:** 12 Nov 2026 (logs timestamped UTC; IST = UTC+5:30, so 14:47 UTC = 20:17 IST)
**Machine:** this sandbox (Linux, Node v24.22.1, npm 10.9.4)
**Docs read first:** https://www.testmuai.com/support/docs/kane-cli-introduction/ plus its
Installation and Authentication pages (fetched 12 Nov 2026).

## Verdict: CLI is REAL and installs fine — runs are hard-gated on account login. BLOCKED on credentials, nothing else.

- `@testmuai/kane-cli` is a genuine public npm package. It installed cleanly
  (180 packages, exit 0) and the binary works: `kane-cli --version` → `0.10.4`.
- There is **no separate demo/upgrade gate** in the CLI itself — the hint on the
  hackathon page does not correspond to any extra wall in the tool. The one and
  only gate is **authentication**: every command that touches the account
  (`balance`, `run`, …) refuses until you log in.
- The local ProofBench target was up and healthy during the attempt
  (`GET http://127.0.0.1:8773/health` → `{"ok": true, "status": "ok", "app":
  "proofbench", "target": "bundled demo target (simulated)"}`, homepage HTTP 200),
  so the run attempt below failed **only** on auth, not on the target.
- No Kane test output exists yet, and none is claimed anywhere. ProofBench's
  Kane channel stays **AWAITING / provenance-labelled** until a real,
  authenticated Kane run produces output to import.

## Exactly what unblocks it (one of these, user's hand only)

Per the official Authentication doc (https://www.testmuai.com/docs/kane-cli-authentication):

1. **Basic auth (right route for this sandbox):** the user's TestMu **username**
   and **access key**. The access key lives in his account dashboard:
   sign in at **accounts.lambdatest.com → Credentials** and copy the access key.
   Hand both over via the **Secure Vault** (never chat). Then:
   `kane-cli login --username <user> --access-key <key>`, verify with
   `kane-cli whoami` and `kane-cli balance` (expect the 11,000 hackathon
   credits), then run the exported ProofBench plan against the target.
2. **OAuth:** `kane-cli login --oauth` opens a browser consent page — needs the
   user's own browser/machine; not workable from this headless sandbox.

The user's TestMu password is in the Secure Vault and was **not** available to
this session; no credentials were invented, guessed, or stored.

## Verbatim log — install

```
# Kane CLI attempt log — 2026-11-12T14:47:43+00:00
$ npm install -g @testmuai/kane-cli
npm warn deprecated glob@10.5.0: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me

added 180 packages in 57s

57 packages are looking for funding
  run `npm fund` for details
EXIT=0
```

## Verbatim log — version + help

```
=== 2026-11-12T14:48:45+00:00 ===
$ which kane-cli
/usr/bin/kane-cli

$ kane-cli --version
0.10.4
EXIT=0

$ kane-cli --help
Usage: kane-cli [options] [command]

Kane-CLI — the validation layer for AI coding agents. Natural-language web and
mobile-app automation, plus requirements-to-coverage assurance, called from
your CLI or IDE.

Options:
  -V, --version                       output the version number
  -h, --help                          display help for command

Commands:
  apps [options] <action>             List this account's uploaded app builds
                                      for a device class
  balance [options]                   Check credit balance
  changelog [options]                 Show recent release notes
  config [options] <action> [value]   Show or change settings (show,
                                      set-target, set-device-name,
                                      set-os-version, set-app,
                                      set-auto-grant-permissions,
                                      set-auto-accept-alerts,
                                      set-device-stream, set-mode,
                                      set-assertion-mode, set-network-ws,
                                      set-network-sse, set-bug-detection,
                                      set-assertion-failure-mode,
                                      set-final-validation, set-url, reset-url,
                                      set-window, chrome-profile, project,
                                      folder, reset)
  context                             Add your documents as sources, find the
                                      use-cases in them, and list what's there
  cover [options]                     Coverage: how much of your use-cases your
                                      tests have proven
  design                              Design tests: turn an approved use-case
                                      into acceptance criteria, scenarios, and
                                      one test for each scenario
  devices [options] <action>          List the emulators or simulators on this
                                      machine, or with --remote what the cloud
                                      can provide
  evidence                            Evidence pack operations
  explore [options]                   Explore an app into a map of its screens
                                      and flows
  feedback [options]                  Send thumbs-up/down feedback for a
                                      completed test run
  folders [options] <action> [name]   List or create Test Manager folders
  generate [options] [objective]      Generate Test Manager test cases from a
                                      prompt
  help [command]                      display help for command
  install <target> [version]          Install kane-cli agent skill into Claude
                                      Code / Codex CLI / Gemini CLI (version
                                      defaults to latest compatible)
  login [options]                     Authenticate (interactive; --oauth opens
                                      the browser, or --username/--access-key
                                      for basic auth)
  logout                              Revoke tokens and delete the stored
                                      profile credentials
  maintain                            Keep your tests true to your sources as
                                      they change
  plugin                              Manage kane-cli plugins (install, list,
                                      remove, doctor)
  policy                              Evidence verdict policies: the metrics
                                      they can use, the policies in Test
                                      Manager, and creating one. Judge with a
                                      stored policy via --policy-id on testmd
                                      run, testrun run, evidence verdict and
                                      evidence merge.
  profiles [options] [action] [name]  Manage auth profiles (list | switch |
                                      delete)
  projects [options] <action> [name]  List or create Test Manager projects
  run [options] [objective]           Run a browser or mobile objective (inline
                                      natural-language string)
  testmd                              Manage test.md files (run, list, status,
                                      delete, export, sync)
  testrun                             Run M authored *_test.md files as one
                                      execution (one sealed evidence pack)
  whoami [options]                    Show the authenticated identity, active
                                      profile, and environment

Examples:
  $ kane-cli run "Search for a laptop"
  $ kane-cli testmd run smoke_test.md
  $ kane-cli run "Login as {{user}}" --variables '{"user":{"value":"alice"}}'
  $ kane-cli run "Add to cart" --agent | jq .status

Test files:
  *_test.md are markdown tests with YAML frontmatter and '## ' step headings.
  Run one with:  kane-cli testmd run path/to/foo_test.md
  ('.md' paths are not accepted by 'kane-cli run'.)

Docs  https://www.testmuai.com/support/docs/kane-cli-introduction
Bugs  https://github.com/LambdaTest/kane-cli/issues

EXIT=0
```

## Verbatim log — auth state probes (whoami / balance / profiles)

```
=== 2026-11-12T14:49:10+00:00 ===
$ kane-cli whoami
 Identity
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│  ⚠ Not logged in                                                             │
│                                                                              │
│  Profile       default                                                       │
│  Environment   prod                                                          │
│  Method        none                                                          │
│  Token         missing                                                       │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
EXIT=1

$ kane-cli balance
Not authenticated [prod]. Run "kane-cli login" first.
EXIT=2

$ kane-cli profiles list
No profiles configured. Run: kane-cli login
Skill update available: not installed → 0.1.4 — run `kane-cli install skill`

EXIT=0
```

## Verbatim log — the run attempt against the local ProofBench target

```
=== 2026-11-12T14:50:20+00:00 ===
$ kane-cli config set-url http://127.0.0.1:8773/
Default URL set to http://127.0.0.1:8773/
Skill update available: not installed → 0.1.4 — run `kane-cli install skill`

EXIT=0

$ timeout 120 kane-cli run "Open the ProofBench page and report the page heading" --headless --agent
{"type":"stream_start","cli_version":"0.10.4","surface":"run","pid":5724,"v":1,"ts":"2026-11-12T14:50:23.708Z"}
Skill update available: not installed → 0.1.4 — run `kane-cli install skill`

{"type":"recording_state","enabled":true,"session_id":"370b34a0-1567-4c90-8051-0bfc94bd208d","persist":false,"v":1,"ts":"2026-11-12T14:50:23.733Z"}
Not authenticated. Run: kane-cli login --oauth, or kane-cli login --username <user> --access-key <key>
EXIT=1
```

The decisive line, verbatim from the run attempt:

```
Not authenticated. Run: kane-cli login --oauth, or kane-cli login --username <user> --access-key <key>
```

## Verbatim log — login options (for the unblock step)

```
$ kane-cli login --help
Usage: kane-cli login [options]

Authenticate (interactive; --oauth opens the browser, or
--username/--access-key for basic auth)

Options:
  --oauth                  Login via OAuth (opens browser)
  --username <user>        Basic auth username
  --access-key <key>       Basic auth access key
  --profile <name>         Profile name (default: "default")
  --project-id <id>        Project ID (skip picker)
  --folder-id <id>         Folder ID (skip picker)
  --chrome-profile <path>  Chrome profile path
  -h, --help               display help for command
EXIT=0
```

## What happens the minute credentials land

1. `kane-cli login --username … --access-key …` → `kane-cli whoami` (expect the
   account identity card) → `kane-cli balance` (expect 11,000 credits).
2. Point Kane at the target (`kane-cli config set-url <deployed ProofBench URL>`;
   the local URL http://127.0.0.1:8773/ was already set during this attempt).
3. Run the objectives from ProofBench's exported `kane-verify/test-plan v1`
   (the plan the bench already generates at `/api/kane-plan.json`).
4. Import Kane's real output through `/api/kane/import`, flip the provenance
   label from AWAITING to Kane-produced **only with that real output in hand**,
   and append the run logs to this report.
