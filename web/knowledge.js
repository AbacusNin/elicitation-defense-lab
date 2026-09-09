// Page script for knowledge.html. Draws a random subset of the knowledge
// bank on each load, renders it, and scores it with scoreKnowledge from
// app.js against exactly that shown subset. Also owns the reporting-context
// selector, since context only changes which response choice scores as
// correct on this module.

import { DIMENSIONS, scoreKnowledge } from "./app.js";
import { renderCompetencyScorecard, sampleBank, shuffle, showResult } from "./ui.js";

const STORAGE_KEY = "edl-knowledge-progress";
const CONTEXT_KEY = "edl-context";
const SAMPLE_COUNT = 9;
const el = (id) => document.getElementById(id);

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? {};
  } catch {
    return {};
  }
}

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // storage unavailable (private mode, disabled); the page still scores fine.
  }
}

function loadContext() {
  try {
    return localStorage.getItem(CONTEXT_KEY) ?? "general";
  } catch {
    return "general";
  }
}

function saveContext(context) {
  try {
    localStorage.setItem(CONTEXT_KEY, context);
  } catch {
    // storage unavailable (private mode, disabled); the page still scores fine.
  }
}

const state = loadState();

const contextSelect = el("context");
contextSelect.value = loadContext();
contextSelect.addEventListener("change", () => saveContext(contextSelect.value));

Promise.all([
  fetch("data/config.json").then((r) => r.json()),
  fetch("data/techniques.json").then((r) => r.json()),
  fetch("data/knowledge.json").then((r) => r.json()),
])
  .then(([config, techniques, knowledgeBank]) => {
    render(config, techniques, knowledgeBank);
  })
  .catch((err) => {
    el("load-error").textContent = `Could not load assessment data: ${err.message}`;
    el("load-error").hidden = false;
  });

function render(config, techniques, knowledgeBank) {
  const shown = sampleBank(knowledgeBank, { count: SAMPLE_COUNT });

  const sampleNote = el("sample-note");
  if (sampleNote) {
    sampleNote.textContent = `Showing ${shown.length} of ${knowledgeBank.length} scenarios, drawn fresh each visit.`;
  }

  const container = el("knowledge-items");
  container.textContent = "";
  for (const item of shown) {
    state[item.id] = state[item.id] ?? {};
    const block = document.createElement("div");
    block.className = "scenario";
    const p = document.createElement("p");
    p.textContent = item.scenario;
    block.appendChild(p);
    for (const dim of DIMENSIONS) {
      const group = document.createElement("fieldset");
      group.className = "item";
      const legend = document.createElement("legend");
      legend.textContent = dim;
      group.appendChild(legend);
      // Shuffle the choice order per dimension per render so the correct
      // answer isn't predictably in the same slot every time (it's always
      // choice 0 in the bank data). Scoring compares chosen id to correct
      // id, so this has no effect on grading.
      for (const choice of shuffle(item.choices[dim])) {
        const label = document.createElement("label");
        label.className = "choice";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `know-${item.id}-${dim}`;
        input.value = choice.id;
        if (state[item.id][dim] === choice.id) input.checked = true;
        input.addEventListener("change", () => {
          state[item.id][dim] = choice.id;
          saveState(state);
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
    const context = contextSelect.value;
    // Normalize over exactly what was shown, not the full bank.
    const result = scoreKnowledge(state, config, techniques, shown, context);
    const summary = document.createElement("div");
    summary.appendChild(renderCompetencyScorecard(result, config, techniques));
    summary.appendChild(renderItemFeedback(result.feedback, shown));
    showResult("knowledge", result, context, config, techniques, summary);
  });
}

const STATUS_LABEL = {
  correct: "Correct",
  partial: "Partial credit",
  incorrect: "Incorrect",
  unanswered: "Not answered",
};

// One line per dimension: what the user picked and whether it was right,
// wrong, or partial credit, the correct choice when the pick wasn't it, and
// the explanation for the choice the user actually made (scoreKnowledge
// already resolves that; see dimensionFeedback in app.js). Previously this
// always printed the explanation for the correct choice regardless of what
// was picked, so a wrong answer still read as "Correct."
function renderDimensionLine(dim, entry) {
  const line = document.createElement("p");
  const label = document.createElement("strong");
  label.textContent = `${dim}: `;
  line.appendChild(label);

  const statusLabel = document.createElement("strong");
  statusLabel.textContent = `${STATUS_LABEL[entry.status]}. `;
  line.appendChild(statusLabel);

  if (entry.status === "unanswered") {
    line.append(`Correct answer: "${entry.correct_text}". `);
  } else {
    line.append(`You chose: "${entry.chosen_text}". `);
    if (entry.status !== "correct") {
      line.append(`Correct answer: "${entry.correct_text}". `);
    }
  }
  line.append(entry.explanation ?? "");
  return line;
}

// One card per scored item: the scenario text plus the recognition,
// countermeasure, and response lines, each reflecting the user's own choice
// (right, wrong, or partial) rather than only the correct answer. shown is
// the drawn subset, used to look up each item's scenario text by id.
function renderItemFeedback(feedback, shown) {
  const wrap = document.createElement("div");
  const heading = document.createElement("h3");
  heading.textContent = "Per-item feedback";
  wrap.appendChild(heading);

  const byId = new Map(shown.map((item) => [item.id, item]));
  for (const entry of feedback) {
    const item = byId.get(entry.item_id);
    const card = document.createElement("div");
    card.className = "scenario";
    if (item) {
      const p = document.createElement("p");
      p.textContent = item.scenario;
      card.appendChild(p);
    }
    for (const dim of DIMENSIONS) {
      card.appendChild(renderDimensionLine(dim, entry[dim]));
    }
    wrap.appendChild(card);
  }
  return wrap;
}
