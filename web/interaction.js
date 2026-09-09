// Page script for interaction.html. Draws a random subset of the interaction
// indicator bank on each load, renders each item as a yes/no/unsure question
// with its label, description, and a concrete example, and scores it with
// scoreInteraction from app.js against exactly that shown subset.

import { scoreInteraction } from "./app.js";
import { sampleBank, showResult } from "./ui.js";

const STORAGE_KEY = "edl-interaction-progress";
const CONTEXT_KEY = "edl-context";
const SAMPLE_COUNT = 14;
const ANSWERS = [
  ["yes", "Yes"],
  ["no", "No"],
  ["unsure", "Unsure"],
];
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
  fetch("data/interaction.json").then((r) => r.json()),
])
  .then(([config, techniques, interactionBank]) => {
    render(config, techniques, interactionBank);
  })
  .catch((err) => {
    el("load-error").textContent = `Could not load assessment data: ${err.message}`;
    el("load-error").hidden = false;
  });

function render(config, techniques, interactionBank) {
  const shown = sampleBank(interactionBank, { count: SAMPLE_COUNT });

  const sampleNote = el("sample-note");
  if (sampleNote) {
    sampleNote.textContent = `Showing ${shown.length} of ${interactionBank.length} indicators, drawn fresh each visit.`;
  }

  const container = el("interaction-items");
  container.textContent = "";
  for (const item of shown) {
    const row = document.createElement("fieldset");
    row.className = "item";

    const legend = document.createElement("legend");
    legend.textContent = item.label;
    row.appendChild(legend);

    const desc = document.createElement("p");
    desc.textContent = item.description;
    row.appendChild(desc);

    const example = document.createElement("p");
    example.className = "note";
    example.textContent = `Example: ${item.example}`;
    row.appendChild(example);

    const prompt = document.createElement("p");
    const promptStrong = document.createElement("strong");
    promptStrong.textContent = item.pattern
      ? "Did this happen in the conversation?"
      : "Was this technique used on you?";
    prompt.appendChild(promptStrong);
    row.appendChild(prompt);

    for (const [value, label] of ANSWERS) {
      const id = `interaction-${item.id}-${value}`;
      const optLabel = document.createElement("label");
      optLabel.className = "choice";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `interaction-${item.id}`;
      input.value = value;
      input.id = id;
      if (state[item.id] === value) input.checked = true;
      input.addEventListener("change", () => {
        state[item.id] = value;
        saveState(state);
      });
      optLabel.appendChild(input);
      optLabel.append(` ${label}`);
      row.appendChild(optLabel);
    }

    container.appendChild(row);
  }

  el("interaction-run").addEventListener("click", () => {
    const context = contextSelect.value;
    // Only Yes counts as present; Unsure counts as No, same as an unanswered item.
    const present = shown.map((item) => item.id).filter((id) => state[id] === "yes");
    // Normalize over exactly what was shown, not the full bank.
    const result = scoreInteraction(present, config, techniques, shown);
    showResult("interaction", result, context, config, techniques);
  });
}
