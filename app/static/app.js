"use strict";
/* ProofBench bench controller — every control on the page is wired here. */
const $ = (id) => document.getElementById(id);
const els = {
  spec: $("spec-input"), error: $("spec-error"),
  btnSample: $("btn-sample"), btnRun: $("btn-run"),
  runState: $("run-state"), verdict: $("verdict-lamp"),
  claimsEmpty: $("claims-empty"), claimsWrap: $("claims-wrap"),
  claimsBody: $("claims-body"),
  unparsedWrap: $("unparsed-wrap"), unparsedList: $("unparsed-list"),
  resultsEmpty: $("results-empty"), resultsWrap: $("results-wrap"),
  resultsBody: $("results-body"), summary: $("summary"),
  trace: $("trace"), traceLine: $("trace-line"),
  hashLine: $("hash-line"), specHash: $("spec-hash"), packHash: $("pack-hash"),
  kaneState: $("kane-state"), kaneDetail: $("kane-detail"),
  kaneWrap: $("kane-results-wrap"), kaneBody: $("kane-results-body"),
  kaneFile: $("kane-file"), kaneError: $("kane-error"),
};
let hasRun = false;

function setDownloadsEnabled(on) {
  document.querySelectorAll(".btn.dl").forEach((a) =>
    a.setAttribute("aria-disabled", on ? "false" : "true"));
}
setDownloadsEnabled(false);

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({ ok: false, error: "Bad response." }));
  if (!res.ok || data.ok === false) {
    throw new Error(data.error || `Request failed (${res.status}).`);
  }
  return data;
}

/* 01 — specimen ------------------------------------------------------- */
els.btnSample.addEventListener("click", async () => {
  els.error.hidden = true;
  try {
    const res = await fetch("/api/sample-spec");
    if (!res.ok) throw new Error("Sample spec could not be loaded.");
    els.spec.value = await res.text();
    els.spec.focus();
  } catch (err) {
    els.error.textContent = err.message;
    els.error.hidden = false;
  }
});

/* 02/03/04 — calibrate ------------------------------------------------ */
els.btnRun.addEventListener("click", async () => {
  els.error.hidden = true;
  const spec = els.spec.value.trim();
  if (!spec) {
    els.error.textContent = "Spec is empty — paste at least one claim line.";
    els.error.hidden = false;
    els.spec.focus();
    return;
  }
  els.btnRun.disabled = true;
  els.btnRun.textContent = "MEASURING…";
  els.runState.textContent = "MEASURING";
  try {
    const data = await api("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ spec, target: "demo" }),
    });
    renderPack(data.pack);
  } catch (err) {
    els.error.textContent = err.message;
    els.error.hidden = false;
    els.runState.textContent = "ERROR";
  } finally {
    els.btnRun.disabled = false;
    els.btnRun.textContent = "▶ CALIBRATE — EXTRACT & MEASURE";
  }
});

function renderPack(pack) {
  hasRun = true;
  els.runState.textContent = "COMPLETE";
  els.verdict.textContent = pack.verdict;
  els.verdict.className = "readout " +
    (pack.verdict === "SPEC HOLDS" ? "verdict-holds" : "verdict-disputed");

  const checkByClaim = {};
  pack.checks.forEach((c) => { checkByClaim[c.claim_id] = c; });
  els.claimsBody.innerHTML = pack.claims.map((c) => {
    const chk = checkByClaim[c.id];
    return `<tr><td>${esc(c.id)}</td>` +
      `<td>${esc(chk.description)}</td>` +
      `<td class="src">L${c.line}: ${esc(c.source)}</td>` +
      `<td>${esc(chk.id)}</td></tr>`;
  }).join("");
  els.claimsEmpty.hidden = pack.claims.length > 0;
  els.claimsWrap.hidden = pack.claims.length === 0;

  els.unparsedList.innerHTML = pack.unparsed.map((u) =>
    `<li>L${u.line}: ${esc(u.source)}</li>`).join("");
  els.unparsedWrap.hidden = pack.unparsed.length === 0;

  const claimById = {};
  pack.claims.forEach((c) => { claimById[c.id] = c; });
  els.resultsBody.innerHTML = pack.results.map((r) =>
    `<tr><td>${esc(r.claim_id)} — ${esc(claimById[r.claim_id].source)}</td>` +
    `<td>${esc(r.expected)}</td><td>${esc(r.observed)}</td>` +
    `<td><span class="chip ${r.status === "PASS" ? "pass" : "fail"}">` +
    `${r.status === "PASS" ? "✓" : "✕"} ${r.status}</span></td></tr>`).join("");
  els.resultsEmpty.hidden = pack.results.length > 0;
  els.resultsWrap.hidden = pack.results.length === 0;

  drawTrace(pack.results);
  const s = pack.summary;
  els.summary.textContent =
    `MEASURED ${s.total_claims} CLAIMS · ${s.passed} PASS · ${s.failed} FAIL · ` +
    `${s.unparsed_lines} UNPARSED — VERDICT: ${pack.verdict}`;
  els.summary.hidden = false;

  els.specHash.textContent = pack.spec_sha256;
  els.packHash.textContent = pack.integrity_sha256;
  els.hashLine.hidden = false;
  setDownloadsEnabled(true);
}

/* The result trace: one segment per check, up for PASS, down for FAIL. */
function drawTrace(results) {
  if (!results.length) { els.trace.hidden = true; return; }
  const step = 1000 / results.length;
  let pts = "0,45";
  results.forEach((r, i) => {
    const y = r.status === "PASS" ? 14 : 76;
    pts += ` ${(i + 0.5) * step},${y} ${(i + 1) * step},${y}`;
  });
  els.traceLine.setAttribute("points", pts);
  els.trace.hidden = false;
  const len = els.traceLine.getTotalLength ? els.traceLine.getTotalLength() : 0;
  if (len && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    els.traceLine.style.strokeDasharray = String(len);
    els.traceLine.style.strokeDashoffset = String(len);
    requestAnimationFrame(() => { els.traceLine.style.strokeDashoffset = "0"; });
  }
}

/* 05 — Kane channel ---------------------------------------------------- */
async function refreshKane() {
  try {
    const data = await api("/api/kane/status");
    els.kaneState.textContent = data.label;
    els.kaneState.className = "readout" +
      (data.state === "imported" ? "" : " amber");
    els.kaneDetail.textContent = data.detail;
    if (data.state === "imported") {
      els.kaneBody.innerHTML = data.results.map((r) =>
        `<tr><td>${esc(r.check_id)}</td>` +
        `<td><span class="chip ${r.status === "PASS" ? "pass" : "fail"}">${esc(r.status)}</span></td>` +
        `<td>${esc(r.output)}</td></tr>`).join("");
      els.kaneWrap.hidden = data.results.length === 0;
    } else {
      els.kaneWrap.hidden = true;
    }
  } catch (err) {
    els.kaneError.textContent = err.message;
    els.kaneError.hidden = false;
  }
}
refreshKane();

els.kaneFile.addEventListener("change", async () => {
  els.kaneError.hidden = true;
  const file = els.kaneFile.files[0];
  if (!file) return;
  try {
    const doc = JSON.parse(await file.text());
    await api("/api/kane/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(doc),
    });
    await refreshKane();
  } catch (err) {
    els.kaneError.textContent =
      "Import failed: " + (err.message || "file is not valid JSON.");
    els.kaneError.hidden = false;
  } finally {
    els.kaneFile.value = "";
  }
});
