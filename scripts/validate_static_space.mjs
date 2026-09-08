import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const folder = path.resolve(process.argv[2] || "/tmp/space");
const runtime = require(path.join(folder, "runtime.js"));
const model = JSON.parse(fs.readFileSync(path.join(folder, "model.json"), "utf8"));
const fixtures = JSON.parse(fs.readFileSync(path.join(folder, "validation.json"), "utf8"));

const tolerance = 1e-8;
let checked = 0;
for (const fixture of fixtures) {
  const actual = runtime.predictBundle(model, fixture.text);
  for (const task of ["route", "urgency"]) {
    const expected = fixture[task];
    const label = task === "route" ? actual.route : actual.urgency;
    const confidence = task === "route" ? actual.route_confidence : actual.urgency_confidence;
    const probabilities = task === "route" ? actual.route_probabilities : actual.urgency_probabilities;
    if (label !== expected.label) {
      throw new Error(`${task} label mismatch: ${label} != ${expected.label}`);
    }
    if (Math.abs(confidence - expected.confidence) > tolerance) {
      throw new Error(`${task} confidence mismatch: ${confidence} != ${expected.confidence}`);
    }
    for (const [name, value] of Object.entries(expected.probabilities)) {
      if (Math.abs(probabilities[name] - value) > tolerance) {
        throw new Error(`${task}/${name} probability mismatch: ${probabilities[name]} != ${value}`);
      }
    }
    checked += 1;
  }
}
console.log(`STATIC RUNTIME PARITY: PASS (${checked} task predictions, tolerance ${tolerance})`);
