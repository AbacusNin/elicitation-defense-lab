// Page script for interaction.html. Renders every item in the interaction
// indicator bank, grouped into five collapsible sections (the four
// psychological classes plus conversational-control patterns), and scores
// it with scoreInteraction from app.js against the full bank. No sampling:
// every load shows all 34 items, and every item is answerable regardless of
// which section is expanded.

import { scoreInteraction } from "./app.js";
import { CLASS_LABELS, showResult } from "./ui.js";

const STORAGE_KEY = "edl-interaction-progress";
const CONTEXT_KEY = "edl-context";
const ANSWERS = [
  ["yes", "Yes"],
  ["no", "No"],
  ["unsure", "Unsure"],
];

// Group order and labels. The first four are the psychological classes an
// item's technique belongs to (looked up via technique_id in techniques.json);
// the fifth holds the pattern items (item.pattern === true), which carry no
// technique_id and so never sort into the first four.
const GROUP_ORDER = ["ego", "reciprocity", "social_pressure", "cognitive_cue", "patterns"];
const GROUP_LABELS = {
  ...CLASS_LABELS,
  patterns: "Conversational-control patterns",
};

// A28 (the Scharff technique) carries technique_class "composite" in
// techniques.json, not one of the four base classes: taxonomy/reference.md
// describes it as a composite of reciprocity and cognitive cue. It is
// grouped under reciprocity here so every item still lands in exactly one of
// the five sections.
const CLASS_OVERRIDE = { A28: "reciprocity" };

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

// Bucket the bank into the five groups, each ordered by id (numeric-aware,
// so a10 sorts after a9 rather than after a1) rather than by diagnosticity,
// so the layout does not telegraph which indicators weigh most.
function groupItems(interactionBank, techniques) {
  const techById = new Map(techniques.map((t) => [t.id, t]));
  const groups = new Map(GROUP_ORDER.map((key) => [key, []]));

  for (const item of interactionBank) {
    if (item.pattern) {
      groups.get("patterns").push(item);
      continue;
    }
    const cls = CLASS_OVERRIDE[item.technique_id] ?? techById.get(item.technique_id)?.technique_class;
    if (groups.has(cls)) groups.get(cls).push(item);
  }

  for (const items of groups.values()) {
    items.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  }
  return groups;
}

function renderItem(item, container) {
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

function render(config, techniques, interactionBank) {
  const sampleNote = el("sample-note");
  if (sampleNote) {
    sampleNote.textContent = `All ${interactionBank.length} indicators are shown, none sampled.`;
  }

  const groups = groupItems(interactionBank, techniques);

  const groupsContainer = el("interaction-groups");
  groupsContainer.textContent = "";

  const jumpSelect = el("group-jump");
  const detailsByGroup = new Map();

  for (const key of GROUP_ORDER) {
    const items = groups.get(key);

    const details = document.createElement("details");
    details.className = "item-group";
    details.open = true;
    details.id = `group-${key}`;
    detailsByGroup.set(key, details);

    const summary = document.createElement("summary");
    summary.textContent = `${GROUP_LABELS[key]} (${items.length})`;
    details.appendChild(summary);

    for (const item of items) {
      renderItem(item, details);
    }

    groupsContainer.appendChild(details);

    const option = document.createElement("option");
    option.value = key;
    option.textContent = `${GROUP_LABELS[key]} (${items.length})`;
    jumpSelect.appendChild(option);
  }

  jumpSelect.addEventListener("change", () => {
    const key = jumpSelect.value;
    if (!key) return;
    const details = detailsByGroup.get(key);
    details.open = true;
    details.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  el("interaction-run").addEventListener("click", () => {
    const context = contextSelect.value;
    // Only Yes counts as present; Unsure counts as No, same as an unanswered item.
    const present = interactionBank.map((item) => item.id).filter((id) => state[id] === "yes");
    // Score over the full bank: interaction shows every item, no sampling.
    const result = scoreInteraction(present, config, techniques, interactionBank);
    showResult("interaction", result, context, config, techniques);
  });
}
