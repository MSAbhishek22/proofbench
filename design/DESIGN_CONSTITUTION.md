# ProofBench — Design Constitution
## Kane CLI Online Hackathon (TestMu AI) · Lane 4: Requirements that test themselves
Written 12 Nov 2026, before implementation, per ABHI_22 Rulebook §1.2.

## 1. Product personality and emotional tone
A **calibration bench instrument**. Calm, exact, faintly sceptical. The product
does not celebrate or alarm; it *measures*. Copy is terse and numeric, like a
readout: `CLAIM 03 · EXPECTED ≤ 200 ms · OBSERVED 142 ms · PASS`. The emotional
promise is the relief of certainty: a spec stops being an opinion the moment
it is clamped into the bench and measured.

## 2. Target user's environment
A builder/QA engineer at a desk during a build session, likely with a terminal
and an editor open beside the browser, checking whether the thing they (or an
agent) just built actually does what the spec promised. Desktop-first, works
on a laptop, remains usable on a phone for a quick verdict check.

## 3. Visual metaphor / central design idea
**The spec is a specimen clamped into a measuring instrument.** The page is a
bench: a dark graphite instrument plate with machined section dividers,
registration crosshairs in the corners, a phosphor-green measurement trace
(an oscilloscope-style SVG line whose peaks/valleys encode the pass/fail
sequence of the run), and readout windows that show numbers the way a
5-digit DVM shows a voltage — big, mono, unambiguous. If the metaphor were
removed, the page would degrade into "another dark dashboard"; the trace,
readouts and specimen framing are the product's identity.

## 4. Colour palette (semantic roles)
- **Bench graphite** `#111417` — page background (the instrument chassis).
- **Plate** `#181C20` — section surfaces, 1px machined edge `#2A3036`.
- **Phosphor** `#4ADE80`-family, fixed value `#57E389` — PASS, traces, active
  measurement. Never used decoratively on large areas.
- **Amber** `#E8B33C` — caution: unparsed lines, awaiting states (Kane channel).
- **Fault red** `#E5534B` — FAIL only. A fail is a measurement, not a disaster:
  same size, same weight as a pass.
- **Readout text** `#D7DEE6` primary, `#8A94A0` secondary (labels, units).
- Colour is never the only signal: every verdict also carries the word
  PASS/FAIL, an icon glyph (✓ / ✕) and the observed value in numbers.

## 5. Typography
- **Readouts, data, code, numbers:** ui-monospace stack
  (`"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace`) —
  system fonts only, no webfont dependency.
- **Headings/labels:** same mono stack, uppercase, letter-spaced — instrument
  silkscreen lettering, not a marketing display face.
- Deliberately NOT the serif-editorial identity of Spec Ghost / YojanaSetu
  and NOT the warm display type of ChaiTip. Hierarchy comes from size,
  spacing and the silkscreen/rule system, not from a second typeface.

## 6. Layout grid, spacing, composition
Single-column bench, max width 1080px, sections stacked as instrument
modules with numbered silkscreen labels (`01 · SPECIMEN`, `02 · CLAIMS`,
`03 · MEASUREMENT`, `04 · EVIDENCE PACK`, `05 · KANE CHANNEL`). 8px spacing
scale. A fine graticule grid (CSS background, lines every 32px at 4% opacity)
sits behind the measurement section only. Registration crosshair marks at
module corners (CSS pseudo-elements).

## 7. Navigation and information architecture
One page, one workflow, top to bottom in run order. A slim top plate holds
the product name, the run-state readout (`IDLE / MEASURING / COMPLETE`) and
the verdict lamp. No sidebar, no tabs, no modal flows.

## 8. Component behaviour and interaction patterns
- **Specimen intake:** textarea + "Load sample spec" + file-less paste.
  Validation error inline ("Spec is empty — paste at least one claim line").
- **CALIBRATE button:** the single primary action. Pressed state, disabled +
  "MEASURING…" while the run executes, re-enabled after.
- **Claim table:** one row per extracted claim — id, source line, parsed
  expectation, generated check. Unparsed lines listed separately in amber,
  never silently dropped.
- **Result rows:** claim → check → PASS/FAIL chip → observed value verbatim.
- **Downloads:** Evidence Pack (JSON), Evidence Pack (Markdown), Kane test
  plan (JSON) — real files from real endpoints, never fake links.
- **Kane channel:** import control accepts a results JSON file; until a file
  is imported the panel shows the honest state `AWAITING FIRST KANE RUN`.
  Imported results are labelled "imported — provenance not verified".

## 9. Motion language
Transform/opacity only. The trace draws itself (stroke-dashoffset) once per
run; the verdict lamp fades in. No continuous animation, no particles.
`prefers-reduced-motion` disables the trace draw and all transitions; every
state remains fully readable statically.

## 10. 3D / spatial concept
Depth is instrumental, not decorative: (a) the **result trace** — an SVG
oscilloscope trace across the measurement module, one segment per check,
rising for PASS and dropping for FAIL, so the shape of a run is visible at a
glance; (b) **layered instrument plates** — modules sit on stepped graphite
plates with machined edge highlights, and the verdict readout is a recessed
window (inset shadow) like a DVM display. Both are pure CSS/SVG, zero canvas,
zero WebGL cost, with a static fallback (the trace renders fully drawn when
motion is reduced). A richer 3D verdict dial is scheduled in BUILD_PLAN.md
only if it stays meaningful; it is not faked tonight.

## 11. Responsive behaviour
Desktop: two-column claim/result tables. ≤720px: tables collapse to stacked
readout rows; the CALIBRATE button stays full-width and reachable; trace
scales by viewBox. No horizontal overflow; tap targets ≥ 40px.

## 12. Accessibility and reduced motion
Semantic landmarks, labelled textarea and buttons, focus-visible outlines in
phosphor, verdicts never colour-only (word + glyph + value), contrast of
readout text on graphite ≥ 7:1, keyboard-complete workflow (paste → Tab →
Enter runs the bench).

## 13. Design references (inspected 12 Nov 2026 via fetched pages/search)
1. **Phosphor Scope — tactileui.dev/objects/phosphor-scope** (same category:
   measurement display). Learned: phosphor green/amber semantics, graticule,
   "the beam leaves light behind it" — a trace as evidence. NOT copied: their
   WebGL persistence engine; ours is a static SVG trace.
2. **Tektronix 1 Series / TekScope** (allaboutcircuits.com news, 10 Nov 2026)
   (same category: test equipment). Learned: progressive disclosure — channel
   badge shows essentials, depth on demand; automated measurements as
   first-class readouts. NOT copied: touch-first dense menus.
3. **GitHub Checks status model** (depot.dev/docs/ci/observability/github-checks)
   (adjacent: verification results). Learned: the status vocabulary —
   queued / in progress / success / failure — each with icon + text, and
   check *output* (summary + annotations) attached to the result. Translated
   here into PASS/FAIL chips with the observed output on the same row.
4. **Argos visual-approval states** (argos-ci.com blog) (adjacent: evidence
   review). Learned: a result can be *pending human judgement*, states are
   named honestly. Translated into the Kane channel's AWAITING state instead
   of a fake green.
5. **TestDriver CI guide** (testdriver.ai article) (adjacent: UI testing).
   Learned the principle "a green job is meaningful only if a broken UI
   makes it red" — the demo target therefore contains claims designed to
   FAIL, visibly, or the bench proves nothing.

## 14. Original design decisions (not from any reference)
Specimen/clamp framing for a pasted spec; claim rows numbered like
measurement channels (`CH-01…`); the verdict word is binary and blunt —
`SPEC HOLDS` / `SPEC DISPUTED` — because a calibration bench does not do
"mostly passed".
