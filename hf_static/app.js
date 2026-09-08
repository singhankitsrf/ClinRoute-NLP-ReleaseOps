"use strict";

let model = null;
let evaluation = null;

const $ = (id) => document.getElementById(id);
const pretty = (value) => String(value || "").replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
const pct = (value) => `${(Number(value) * 100).toFixed(1)}%`;

function setTabs() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((x) => x.classList.remove("active"));
      button.classList.add("active");
      $(button.dataset.tab).classList.add("active");
    });
  });
}

function renderEvidence(report) {
  const metrics = [
    ["Route macro-F1", report.route.macro_f1.toFixed(3)],
    ["Urgency macro-F1", report.urgency.macro_f1.toFixed(3)],
    ["Route ECE", report.route.ece.toFixed(3)],
    ["Urgency ECE", report.urgency.ece.toFixed(3)]
  ];
  $("metricCards").innerHTML = metrics.map(([name, value]) => `<div class="metric"><span>${name}</span><strong>${value}</strong></div>`).join("");
  const rows = [
    ["Input rows", report.input_rows], ["Unique notes", report.unique_notes],
    ["Train samples", report.train_samples], ["Test samples", report.test_samples],
    ["Exact overlap", report.train_test_text_overlap], ["Seed", report.seed]
  ];
  $("protocol").innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
}

function analyze() {
  $("error").textContent = "";
  const text = $("note").value.trim();
  if (!text) {
    $("error").textContent = "Enter a synthetic referral or choose an example.";
    return;
  }
  if (!model) {
    $("error").textContent = "Model bundle has not loaded yet.";
    return;
  }
  const result = ClinRouteRuntime.predictBundle(model, text);
  $("route").textContent = pretty(result.route);
  $("routeConf").textContent = pct(result.route_confidence);
  $("urgency").textContent = pretty(result.urgency);
  $("urgencyConf").textContent = pct(result.urgency_confidence);
  $("review").textContent = result.review_required ? "Human review required by confidence policy" : "Confidence policy does not require review";
  $("review").classList.toggle("flag", result.review_required);
  $("details").textContent = JSON.stringify(result, null, 2);
}

async function boot() {
  setTabs();
  document.querySelectorAll("[data-example]").forEach((button) => {
    button.addEventListener("click", () => { $("note").value = button.dataset.example; analyze(); });
  });
  $("analyze").addEventListener("click", analyze);
  try {
    const [modelResponse, evaluationResponse] = await Promise.all([fetch("model.json"), fetch("evaluation.json")]);
    if (!modelResponse.ok || !evaluationResponse.ok) throw new Error("Static evidence bundle could not be loaded");
    model = await modelResponse.json();
    evaluation = await evaluationResponse.json();
    renderEvidence(evaluation);
    $("revision").textContent = `Model ${model.model_version} · source ${model.source_revision.slice(0, 12)}`;
  } catch (error) {
    $("error").textContent = `Initialization failed: ${error.message}`;
    $("revision").textContent = "Model bundle unavailable";
  }
}

boot();
