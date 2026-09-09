// Run the JavaScript scorers over the same inputs the Python fixtures used and
// print the results as JSON, in the same order. test_parity.py diffs this
// against tests/fixtures/parity_cases.json. Reads the shared web/data/ files so
// the JS scores off the exact numbers build_data.py froze from the Python config.
//
// Prints the full result per case (everything but feedback, dropped the same
// way tests/fixtures/make_parity_cases.py drops it), not just overall_score
// and tier, so the class-score path (weightedClassScores) gets checked too.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { scoreSelf, scoreInteraction, scoreKnowledge } from "../../web/app.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");

const readJson = (...parts) => JSON.parse(readFileSync(join(root, ...parts), "utf-8"));

const config = readJson("web", "data", "config.json");
const techniques = readJson("web", "data", "techniques.json");
const selfBank = readJson("web", "data", "self_assessment.json");
const interactionBank = readJson("web", "data", "interaction.json");
const knowledgeBank = readJson("web", "data", "knowledge.json");

const cases = readJson("tests", "fixtures", "parity_cases.json");

const results = cases.map(({ module, input }) => {
  let result;
  if (module === "self") {
    result = scoreSelf(input.answers, config, techniques, selfBank);
  } else if (module === "interaction") {
    result = scoreInteraction(input.present, config, techniques, interactionBank);
  } else if (module === "knowledge") {
    result = scoreKnowledge(input.answers, config, techniques, knowledgeBank, input.context);
  } else {
    throw new Error(`unknown module: ${module}`);
  }
  const { feedback, ...comparable } = result;
  return comparable;
});

process.stdout.write(JSON.stringify(results));
