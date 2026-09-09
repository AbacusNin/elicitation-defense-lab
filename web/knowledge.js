// Page script for knowledge.html. Loads the knowledge-check bank, renders it,
// and scores it with scoreKnowledge from app.js. Also owns the reporting-context
// selector, since context only changes which response choice scores as correct
// on this module.

import { scoreKnowledge } from "./app.js";
import { showResult } from "./ui.js";

const STORAGE_KEY = "edl-knowledge-progress";
const CONTEXT_KEY = "edl-context";
const DIMENSIONS = ["recognition", "countermeasure", "response"];
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
  const container = el("knowledge-items");
  container.textContent = "";
  for (const item of knowledgeBank) {
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
      for (const choice of item.choices[dim]) {
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
    const result = scoreKnowledge(state, config, techniques, knowledgeBank, context);
    showResult("knowledge", result, context);
  });
}
