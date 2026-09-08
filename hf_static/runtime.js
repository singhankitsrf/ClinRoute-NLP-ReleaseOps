(function (root) {
  "use strict";

  const SYMPTOMS = [
    "ear pain", "ear discharge", "blocked ear", "hearing loss", "hearing difficulty",
    "tinnitus", "nasal obstruction", "sinus pressure", "reduced smell",
    "persistent nasal discharge", "hoarseness", "voice fatigue", "difficulty swallowing",
    "neck swelling", "sore throat", "tonsil concern"
  ];
  const FINDINGS = [
    "inflamed tympanic membrane", "perforated tympanic membrane", "middle ear effusion",
    "retracted tympanic membrane", "deviated nasal septum", "nasal polyp",
    "recurrent tonsillitis", "persistent dysphonia"
  ];

  function redact(text) {
    let out = String(text || "");
    out = out.replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[EMAIL_REDACTED]");
    out = out.replace(/(^|[^\w])((?:\+?\d[\d\-\s]{7,}\d))(?!\w)/g, "$1[PHONE_REDACTED]");
    out = out.replace(/\b(?:MRN[:\s-]*)?(?:SYN|MRN)[-_ ]?\d{5,12}\b/gi, "[MRN_REDACTED]");
    return out;
  }

  function tokens(text) {
    const lower = String(text || "").toLowerCase();
    const unigram = lower.match(/[\p{L}\p{N}_]{2,}/gu) || [];
    const features = unigram.slice();
    for (let i = 0; i + 1 < unigram.length; i += 1) {
      features.push(unigram[i] + " " + unigram[i + 1]);
    }
    return features;
  }

  function vectorize(spec, text) {
    const counts = new Map();
    for (const term of tokens(text)) {
      if (!Object.prototype.hasOwnProperty.call(spec.vocabulary, term)) continue;
      const idx = spec.vocabulary[term];
      counts.set(idx, (counts.get(idx) || 0) + 1);
    }
    const sparse = [];
    let norm2 = 0;
    for (const [idx, count] of counts.entries()) {
      const tf = spec.sublinear_tf ? 1 + Math.log(count) : count;
      const value = tf * spec.idf[idx];
      sparse.push([idx, value]);
      norm2 += value * value;
    }
    const norm = Math.sqrt(norm2);
    if (norm > 0) {
      for (const pair of sparse) pair[1] /= norm;
    }
    return sparse;
  }

  function softmax(values) {
    const max = Math.max.apply(null, values);
    const exp = values.map((x) => Math.exp(x - max));
    const total = exp.reduce((a, b) => a + b, 0);
    return exp.map((x) => x / total);
  }

  function predictTask(spec, text) {
    const x = vectorize(spec, text);
    const scores = spec.intercept.slice();
    for (let c = 0; c < spec.classes.length; c += 1) {
      let score = scores[c];
      const row = spec.coef[c];
      for (const [idx, value] of x) score += row[idx] * value;
      scores[c] = score;
    }
    const probabilities = softmax(scores);
    let best = 0;
    for (let i = 1; i < probabilities.length; i += 1) {
      if (probabilities[i] > probabilities[best]) best = i;
    }
    return {
      label: spec.classes[best],
      confidence: probabilities[best],
      probabilities: Object.fromEntries(spec.classes.map((label, i) => [label, probabilities[i]]))
    };
  }

  function extractEntities(text) {
    const found = [];
    const lower = text.toLowerCase();
    for (const [type, terms] of [["SYMPTOM", SYMPTOMS], ["FINDING", FINDINGS]]) {
      for (const term of terms) {
        let start = 0;
        while (true) {
          const idx = lower.indexOf(term, start);
          if (idx < 0) break;
          found.push({ type, value: text.slice(idx, idx + term.length), start: idx, end: idx + term.length });
          start = idx + term.length;
        }
      }
    }
    const duration = /\b(?:for\s+)?\d+\s*(?:day|days|week|weeks|month|months|year|years)\b/gi;
    for (const match of text.matchAll(duration)) {
      found.push({ type: "DURATION", value: match[0], start: match.index, end: match.index + match[0].length });
    }
    return found.sort((a, b) => (a.start - b.start) || (a.end - b.end));
  }

  function predictBundle(model, rawText) {
    const cleaned = redact(rawText);
    const route = predictTask(model.route, cleaned);
    const urgency = predictTask(model.urgency, cleaned);
    return {
      route: route.label,
      route_confidence: route.confidence,
      route_probabilities: route.probabilities,
      urgency: urgency.label,
      urgency_confidence: urgency.confidence,
      urgency_probabilities: urgency.probabilities,
      review_required: route.confidence < 0.70 || urgency.confidence < 0.70,
      redacted_text: cleaned,
      entities: extractEntities(cleaned),
      model_version: model.model_version,
      source_revision: model.source_revision,
      disclaimer: "Research/engineering output; not a clinical diagnosis."
    };
  }

  const api = { redact, tokens, vectorize, predictTask, extractEntities, predictBundle };
  root.ClinRouteRuntime = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
