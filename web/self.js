// Page script for self.html. Loads the self-assessment bank, renders it, and
// scores it with scoreSelf from app.js.

import { scoreSelf } from "./app.js";
import { showResult } from "./ui.js";

const STORAGE_KEY = "edl-self-progress";
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
  fetch("data/self_assessment.json").then((r) => r.json()),
])
  .then(([config, techniques, selfBank]) => {
    render(config, techniques, selfBank);
  })
  .catch((err) => {
    el("load-error").textContent = `Could not load assessment data: ${err.message}`;
    el("load-error").hidden = false;
  });

function render(config, techniques, selfBank) {
  const container = el("self-items");
  container.textContent = "";
  const labels = ["0 strongly disagree", "1", "2", "3", "4 strongly agree"];
  for (const item of selfBank) {
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
      if (state[item.id] === v) input.checked = true;
      input.addEventListener("change", () => {
        state[item.id] = v;
        saveState(state);
      });
      label.appendChild(input);
      label.append(` ${labels[v]}`);
      row.appendChild(label);
    }
    container.appendChild(row);
  }
  el("self-run").addEventListener("click", () => {
    const result = scoreSelf(state, config, techniques, selfBank);
    showResult("self", result, "general");
  });
}
