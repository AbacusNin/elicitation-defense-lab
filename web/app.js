// Client-side scoring for the elicitation defense lab.
//
// The three scorers below are line-for-line ports of the Python scorers in
// elicitation_defense_lab/score/. They read the same config.json, techniques,
// and banks that build_data.py froze into web/data/, and tests/test_parity.py
// pins them to the Python numbers so the two implementations cannot drift.
// Sums run in the same order as Python so the floating-point results match.

export const BASE_CLASSES = ["ego", "reciprocity", "social_pressure", "cognitive_cue"];
export const DIMENSIONS = ["recognition", "countermeasure", "response"];

export function tierFor(score, config) {
  if (score >= config.tier_thresholds.high) return "high";
  if (score >= config.tier_thresholds.elevated) return "elevated";
  return "low";
}

// hits: {technique_id: hit_score}. Buckets hits by class, weights them, and
// normalizes each class against the max achievable for that class. Non-base
// (composite/none) and unknown technique ids are ignored, matching common.py.
export function weightedClassScores(hits, techniques, config) {
  const byId = new Map(techniques.map((t) => [t.id, t]));
  const raw = {};
  const ceiling = {};
  for (const cls of BASE_CLASSES) {
    raw[cls] = 0.0;
    ceiling[cls] = 0.0;
  }

  for (const t of techniques) {
    if (!BASE_CLASSES.includes(t.technique_class)) continue;
    const weight = config.technique_weights[t.id] ?? t.default_weight;
    const classWeight = config.class_weights[t.technique_class] ?? 1.0;
    ceiling[t.technique_class] += weight * classWeight;
  }

  for (const [techId, hitScore] of Object.entries(hits)) {
    const t = byId.get(techId);
    if (t === undefined || !BASE_CLASSES.includes(t.technique_class)) continue;
    const weight = config.technique_weights[t.id] ?? t.default_weight;
    const classWeight = config.class_weights[t.technique_class] ?? 1.0;
    raw[t.technique_class] += hitScore * weight * classWeight;
  }

  const out = {};
  for (const cls of BASE_CLASSES) {
    out[cls] = ceiling[cls] > 0 ? raw[cls] / ceiling[cls] : 0.0;
  }
  return out;
}

function itemValue(item, answer) {
  if (!Number.isInteger(answer) || answer < 0 || answer > 4) {
    throw new Error(`answer for ${item.id} must be an integer 0-4, got ${answer}`);
  }
  const value = answer / 4;
  return item.reverse ? 1 - value : value;
}

export function scoreSelf(answers, config, techniques, bank) {
  const classSums = {};
  const classCounts = {};
  for (const cls of BASE_CLASSES) {
    classSums[cls] = 0.0;
    classCounts[cls] = 0;
  }
  let exposureSum = 0.0;
  let exposureCount = 0;

  const byId = new Map(bank.map((item) => [item.id, item]));
  for (const [itemId, answer] of Object.entries(answers)) {
    const item = byId.get(itemId);
    if (item === undefined) continue;
    const value = itemValue(item, answer);
    if (item.exposure) {
      exposureSum += value;
      exposureCount += 1;
    } else if (BASE_CLASSES.includes(item.technique_class)) {
      classSums[item.technique_class] += value;
      classCounts[item.technique_class] += 1;
    }
  }

  const classScores = {};
  for (const cls of BASE_CLASSES) {
    classScores[cls] = classCounts[cls] ? classSums[cls] / classCounts[cls] : 0.0;
  }
  const exposureScore = exposureCount ? exposureSum / exposureCount : 0.0;

  let weightTotal = 0.0;
  for (const cls of BASE_CLASSES) weightTotal += config.class_weights[cls] ?? 1.0;
  let classComponent = 0.0;
  if (weightTotal) {
    let acc = 0.0;
    for (const cls of BASE_CLASSES) acc += classScores[cls] * (config.class_weights[cls] ?? 1.0);
    classComponent = acc / weightTotal;
  }
  const overallScore = (classComponent + exposureScore) / 2;

  return {
    overall_score: overallScore,
    tier: tierFor(overallScore, config),
    class_scores: classScores,
    exposure_score: exposureScore,
  };
}

export function scoreInteraction(present, config, techniques, bank) {
  const byId = new Map(bank.map((item) => [item.id, item]));
  let totalDiagnosticity = 0.0;
  for (const item of bank) totalDiagnosticity += item.diagnosticity;
  let presentDiagnosticity = 0.0;
  for (const itemId of present) {
    if (byId.has(itemId)) presentDiagnosticity += byId.get(itemId).diagnosticity;
  }
  const overallScore = totalDiagnosticity ? presentDiagnosticity / totalDiagnosticity : 0.0;

  const hits = {};
  const matchedTechniques = [];
  for (const itemId of present) {
    const item = byId.get(itemId);
    if (item === undefined || item.technique_id === undefined) continue;
    hits[item.technique_id] = 1.0;
    matchedTechniques.push(item.technique_id);
  }

  return {
    overall_score: overallScore,
    tier: tierFor(overallScore, config),
    class_scores: weightedClassScores(hits, techniques, config),
    matched_techniques: matchedTechniques,
    reporting_flag: overallScore >= config.reporting_threshold,
  };
}

function responseCorrectId(item, context) {
  return item.report_paths[context] ?? item.report_paths.general;
}

function dimensionScore(item, dimension, chosen, correctId) {
  if (chosen === correctId) return 1.0;
  if (item.partial && item.partial[dimension] === chosen) return 0.5;
  return 0.0;
}

export function scoreKnowledge(answers, config, techniques, bank, context) {
  const dimSums = {};
  const dimCounts = {};
  for (const dim of DIMENSIONS) {
    dimSums[dim] = 0.0;
    dimCounts[dim] = 0;
  }
  const hits = {};
  const feedback = [];

  for (const item of bank) {
    const answer = answers[item.id];
    if (answer === undefined || answer === null) continue;

    const correctIds = {
      recognition: item.correct.recognition,
      countermeasure: item.correct.countermeasure,
      response: responseCorrectId(item, context),
    };

    let itemTotal = 0.0;
    for (const dim of DIMENSIONS) {
      const score = dimensionScore(item, dim, answer[dim], correctIds[dim]);
      itemTotal += score;
      dimSums[dim] += score;
      dimCounts[dim] += 1;
    }

    hits[item.technique_id] = itemTotal / DIMENSIONS.length;

    feedback.push({
      item_id: item.id,
      recognition: item.feedback.recognition[correctIds.recognition],
      countermeasure: item.feedback.countermeasure[correctIds.countermeasure],
      response: item.feedback.response[correctIds.response],
    });
  }

  const dimensionScores = {};
  for (const dim of DIMENSIONS) {
    dimensionScores[dim] = dimCounts[dim] ? dimSums[dim] / dimCounts[dim] : 0.0;
  }

  const weights = config.knowledge_dimension_weights;
  let weightTotal = 0.0;
  for (const dim of DIMENSIONS) weightTotal += weights[dim] ?? 1.0;
  let overallScore = 0.0;
  if (weightTotal) {
    let acc = 0.0;
    for (const dim of DIMENSIONS) acc += dimensionScores[dim] * (weights[dim] ?? 1.0);
    overallScore = acc / weightTotal;
  }

  return {
    overall_score: overallScore,
    tier: tierFor(overallScore, config),
    class_scores: weightedClassScores(hits, techniques, config),
    dimension_scores: dimensionScores,
    feedback,
  };
}

// ---------------------------------------------------------------------------
// Event assembly: mirrors elicitation_defense_lab/schema.py build_event so the
// JSON the page shows matches what the CLI would emit for the same run.
// ---------------------------------------------------------------------------

const SCHEMA_VERSION = "1.0";
const INSTRUMENT_VERSION = "1.0";

export function buildEvent(module, result, context) {
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  return {
    schema_version: SCHEMA_VERSION,
    instrument_version: INSTRUMENT_VERSION,
    module,
    tier: result.tier,
    overall_score: result.overall_score,
    class_scores: result.class_scores,
    timestamp,
    context,
    subject_id: null,
    peer_group: null,
    dimension_scores: result.dimension_scores ?? null,
    matched_techniques: result.matched_techniques ?? null,
    reporting_flag: result.reporting_flag ?? null,
  };
}

// The detection queries a defender would run over the emitted event. These match
// the ElicitationAssessment table/index the Task 13 detections build against.
export function detectionQueries(event) {
  const kql = [
    "ElicitationAssessment",
    `| where module == "${event.module}"`,
    "| where tier in (\"elevated\", \"high\")",
  ];
  if (event.reporting_flag) kql.push("| where reporting_flag == true");
  kql.push("| project timestamp, subject_id, module, tier, overall_score, class_scores");

  const spl = [
    `index=elicitation_assessment module="${event.module}" (tier="elevated" OR tier="high")`,
  ];
  if (event.reporting_flag) spl.push("reporting_flag=true");
  spl.push("| table _time subject_id module tier overall_score");

  return { kql: kql.join("\n"), spl: spl.join(" ") };
}

// ---------------------------------------------------------------------------
// Page wiring. Only runs in the browser; skipped when app.js is imported by the
// parity runner under Node.
// ---------------------------------------------------------------------------

if (typeof document !== "undefined") {
  initPage();
}

function initPage() {
  const STORAGE_KEY = "edl-in-progress";
  const state = loadState();
  let data = null;

  const el = (id) => document.getElementById(id);

  Promise.all([
    fetch("data/config.json").then((r) => r.json()),
    fetch("data/techniques.json").then((r) => r.json()),
    fetch("data/self_assessment.json").then((r) => r.json()),
    fetch("data/interaction.json").then((r) => r.json()),
    fetch("data/knowledge.json").then((r) => r.json()),
  ])
    .then(([config, techniques, selfBank, interactionBank, knowledgeBank]) => {
      data = { config, techniques, selfBank, interactionBank, knowledgeBank };
      renderSelf();
      renderInteraction();
      renderKnowledge();
    })
    .catch((err) => {
      el("load-error").textContent = `Could not load assessment data: ${err.message}`;
      el("load-error").hidden = false;
    });

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? {};
    } catch {
      return {};
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // storage unavailable (private mode, disabled); the page still scores fine.
    }
  }

  function techLabel(techId) {
    const t = data.techniques.find((x) => x.id === techId);
    return t ? `${t.id} ${t.name}` : techId;
  }

  function patternLabel(id) {
    const words = id.replace(/^pattern_/, "").split("_");
    const text = words.join(" ");
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  // --- self-assessment ---

  function renderSelf() {
    state.self = state.self ?? {};
    const container = el("self-items");
    container.textContent = "";
    const labels = ["0 strongly disagree", "1", "2", "3", "4 strongly agree"];
    for (const item of data.selfBank) {
      const row = document.createElement("fieldset");
      row.className = "item";
      const legend = document.createElement("legend");
      legend.textContent = item.prompt;
      row.appendChild(legend);
      for (let v = 0; v <= 4; v++) {
        const id = `self-${item.id}-${v}`;
        const label = document.createElement("label");
        label.className = "likert";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `self-${item.id}`;
        input.value = String(v);
        input.id = id;
        if (state.self[item.id] === v) input.checked = true;
        input.addEventListener("change", () => {
          state.self[item.id] = v;
          saveState();
        });
        label.appendChild(input);
        label.append(` ${labels[v]}`);
        row.appendChild(label);
      }
      container.appendChild(row);
    }
    el("self-run").addEventListener("click", () => {
      const result = scoreSelf(state.self, data.config, data.techniques, data.selfBank);
      showResult("self", result);
    });
  }

  // --- interaction ---

  function renderInteraction() {
    state.interaction = state.interaction ?? {};
    const container = el("interaction-items");
    container.textContent = "";
    for (const item of data.interactionBank) {
      const label = document.createElement("label");
      label.className = "check";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = item.id;
      if (state.interaction[item.id]) input.checked = true;
      input.addEventListener("change", () => {
        state.interaction[item.id] = input.checked;
        saveState();
      });
      label.appendChild(input);
      const text = item.technique_id ? techLabel(item.technique_id) : patternLabel(item.id);
      label.append(` ${text}`);
      container.appendChild(label);
    }
    el("interaction-run").addEventListener("click", () => {
      const present = data.interactionBank
        .map((item) => item.id)
        .filter((id) => state.interaction[id]);
      const result = scoreInteraction(present, data.config, data.techniques, data.interactionBank);
      showResult("interaction", result);
    });
  }

  // --- knowledge ---

  function renderKnowledge() {
    state.knowledge = state.knowledge ?? {};
    const container = el("knowledge-items");
    container.textContent = "";
    for (const item of data.knowledgeBank) {
      state.knowledge[item.id] = state.knowledge[item.id] ?? {};
      const block = document.createElement("div");
      block.className = "scenario";
      const p = document.createElement("p");
      p.textContent = item.scenario;
      block.appendChild(p);
      for (const dim of ["recognition", "countermeasure", "response"]) {
        const group = document.createElement("fieldset");
        group.className = "item";
        const legend = document.createElement("legend");
        legend.textContent = dim;
        group.appendChild(legend);
        for (const choice of item.choices[dim]) {
          const label = document.createElement("label");
          label.className = "choice";
          const input = document.createElement("input");
          input.type = "radio";
          input.name = `know-${item.id}-${dim}`;
          input.value = choice.id;
          if (state.knowledge[item.id][dim] === choice.id) input.checked = true;
          input.addEventListener("change", () => {
            state.knowledge[item.id][dim] = choice.id;
            saveState();
          });
          label.appendChild(input);
          label.append(` ${choice.text}`);
          group.appendChild(label);
        }
        block.appendChild(group);
      }
      container.appendChild(block);
    }
    el("knowledge-run").addEventListener("click", () => {
      const context = el("context").value;
      const result = scoreKnowledge(
        state.knowledge,
        data.config,
        data.techniques,
        data.knowledgeBank,
        context
      );
      showResult("knowledge", result);
    });
  }

  // --- result view ---

  function pct(x) {
    return `${(x * 100).toFixed(1)}%`;
  }

  function showResult(module, result) {
    const context = el("context").value;
    el("result").hidden = false;

    const summary = el("result-summary");
    summary.textContent = "";
    const head = document.createElement("p");
    const scoreStrong = document.createElement("strong");
    scoreStrong.textContent = pct(result.overall_score);
    const tierStrong = document.createElement("strong");
    tierStrong.textContent = result.tier;
    head.append("Overall ", scoreStrong, ", tier ", tierStrong, ".");
    summary.appendChild(head);

    const classList = document.createElement("ul");
    for (const cls of BASE_CLASSES) {
      const li = document.createElement("li");
      li.textContent = `${cls}: ${pct(result.class_scores[cls])}`;
      classList.appendChild(li);
    }
    summary.appendChild(classList);

    if (result.reporting_flag) {
      const flag = document.createElement("p");
      flag.className = "flag";
      flag.textContent = "Reporting threshold met: this run would raise a reporting flag.";
      summary.appendChild(flag);
    }

    const event = buildEvent(module, result, context);
    el("event-json").textContent = JSON.stringify(event, null, 2);

    const q = detectionQueries(event);
    el("kql").textContent = q.kql;
    el("spl").textContent = q.spl;

    el("result").scrollIntoView({ behavior: "smooth" });
  }
}
