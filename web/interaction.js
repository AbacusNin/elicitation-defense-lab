// Page script for interaction.html. Loads the interaction indicator bank,
// renders it, and scores it with scoreInteraction from app.js.

import { scoreInteraction } from "./app.js";
import { showResult } from "./ui.js";

const STORAGE_KEY = "edl-interaction-progress";
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

const state = loadState();

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

function techLabel(techniques, techId) {
  const t = techniques.find((x) => x.id === techId);
  return t ? `${t.id} ${t.name}` : techId;
}

function patternLabel(id) {
  const words = id.replace(/^pattern_/, "").split("_");
  const text = words.join(" ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function render(config, techniques, interactionBank) {
  const container = el("interaction-items");
  container.textContent = "";
  for (const item of interactionBank) {
    const label = document.createElement("label");
    label.className = "check";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = item.id;
    if (state[item.id]) input.checked = true;
    input.addEventListener("change", () => {
      state[item.id] = input.checked;
      saveState(state);
    });
    label.appendChild(input);
    const text = item.technique_id ? techLabel(techniques, item.technique_id) : patternLabel(item.id);
    label.append(` ${text}`);
    container.appendChild(label);
  }
  el("interaction-run").addEventListener("click", () => {
    const present = interactionBank.map((item) => item.id).filter((id) => state[id]);
    const result = scoreInteraction(present, config, techniques, interactionBank);
    showResult("interaction", result, "general");
  });
}
