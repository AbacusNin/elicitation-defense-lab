// Shared UI helpers for the three module pages: sampling banks down to a
// shown subset, and rendering a scored result. self.js is the first page
// wired to these; interaction.js and knowledge.js are expected to move onto
// shuffle/sampleBank/renderScorecard next, so the two below are kept generic
// rather than self-specific.

import { BASE_CLASSES, buildEvent, detectionQueries, tierFor } from "./app.js";

function pct(x) {
  return `${(x * 100).toFixed(1)}%`;
}

// Fisher-Yates. Does not mutate the input.
export function shuffle(array) {
  const out = array.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// Draw a subset of a bank for display. Two modes, usable together:
//   - stratified: opts.groupKey names the field to group by (e.g.
//     "technique_class"); opts.perGroup caps how many items are drawn from
//     each group value present in the bank. Items missing that field are
//     skipped by this pass.
//   - extra: opts.extraFilter picks a side pool (e.g. exposure items) drawn
//     up to opts.extraCount items (all of them if extraCount is omitted).
//   - plain random: opts.count alone, with neither groupKey nor extraFilter,
//     draws N items from the whole bank.
// The result is shuffled once more before it is returned, so the stratified
// and extra items are not blocked together.
export function sampleBank(bank, opts = {}) {
  const { groupKey, perGroup, extraFilter, extraCount, count } = opts;
  let drawn = [];

  if (groupKey && perGroup) {
    const groups = new Map();
    for (const item of bank) {
      const key = item[groupKey];
      if (key === undefined || key === null) continue;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(item);
    }
    for (const items of groups.values()) {
      drawn.push(...shuffle(items).slice(0, perGroup));
    }
  }

  if (extraFilter) {
    const pool = bank.filter(extraFilter);
    const n = extraCount ?? pool.length;
    drawn.push(...shuffle(pool).slice(0, n));
  }

  if (!groupKey && !extraFilter && count) {
    drawn = shuffle(bank).slice(0, count);
  }

  return shuffle(drawn);
}

// Plain-language reading of an overall tier.
const TIER_READING = {
  low: "Limited susceptibility to the conversational pressure and pull to disclose covered here.",
  elevated:
    "A moderate pull to disclose under some of these techniques. Review the classes flagged below.",
  high: "A strong pull to disclose under several of these techniques. Treat the flagged classes as a training priority.",
};

const CLASS_LABELS = {
  ego: "Ego",
  reciprocity: "Reciprocity",
  social_pressure: "Social pressure",
  cognitive_cue: "Cognitive cue",
};

// One line per class per risk tier: what the tier means, and for elevated
// and high, which countermeasures to drill. Grounded in the Catalog A
// elicitation techniques each class covers (elicitation-catalog-comprehensive.md).
const CLASS_INFO = {
  ego: {
    low: "Praise, doubt, and criticism aimed at your work do not appear to pull extra detail out of you.",
    elevated:
      "Praise, doubt, or criticism sometimes pulls more detail out of you than the setting calls for. Practice acknowledging it without expanding.",
    high: "Flattery, feigned doubt, criticism, and one-upping reliably pull extra detail out of you. Drill acknowledging praise or a challenge without expanding, and letting a wrong claim about your work stand uncorrected (flattery, provocation, false statement, criticism, one-upper countermeasures).",
  },
  reciprocity: {
    low: "Offered confidences, favors, or fast rapport do not appear to create a felt obligation to share in return.",
    elevated:
      "A confided secret, an unprompted favor, or quick rapport sometimes tips you toward sharing more than you meant to.",
    high: "Confided secrets, unprompted favors, attentive listening, and fast rapport reliably create a felt debt that gets paid in information. Drill noticing the obligation and declining to trade (confidential bait, quid pro quo, good listener, mutual interest, offering-assistance countermeasures).",
  },
  social_pressure: {
    low: "Direct questions, surveys, and informal settings do not appear to push you past your own limits.",
    elevated:
      "A blunt question, a survey, or a relaxed setting sometimes pushes you to answer before you have judged whether you should.",
    high: "Direct questions, surveys, unverified recruiters, venting, and relaxed off-site settings reliably override your judgment about what to share. Drill pausing before a direct ask and holding the same discretion off-site as in the office (direct question, survey, ruse interview, urge-to-complain, setting-manipulation countermeasures).",
  },
  cognitive_cue: {
    low: "Assumed knowledge, estimates, leading questions, and hypotheticals do not appear to draw confirmations out of you.",
    elevated:
      "An assumed-knowledge opener, a rough estimate, or a leading question sometimes draws a confirming detail out of you.",
    high: "Assumed knowledge, bracketed estimates, leading questions, and hypotheticals reliably draw confirming detail out of you. Drill verifying what someone actually knows before you fill a gap, and refusing to narrow a range or engage a hypothetical on sensitive ground (assumed-knowledge, bracketing, leading-question, hypothetical countermeasures).",
  },
};

function riskFor(score, config) {
  return tierFor(score, config);
}

// Render a scored result as a scorecard: the overall tier with a
// plain-language reading, and each of the four classes with its own risk
// indicator (low / elevated / high) plus one line on what that means and
// which countermeasures to drill. Returns a detached DOM node; the caller
// inserts it wherever the page wants it.
export function renderScorecard(result, config) {
  const wrap = document.createElement("div");
  wrap.className = "scorecard";

  const overall = document.createElement("p");
  const tierStrong = document.createElement("strong");
  tierStrong.textContent = `${result.tier} (${pct(result.overall_score)})`;
  overall.append("Overall: ", tierStrong, ". ", TIER_READING[result.tier] ?? "");
  wrap.appendChild(overall);

  const list = document.createElement("ul");
  list.className = "scorecard-classes";
  for (const cls of BASE_CLASSES) {
    const score = result.class_scores[cls];
    const risk = riskFor(score, config);
    const li = document.createElement("li");
    li.className = `risk-${risk}`;
    const head = document.createElement("strong");
    head.textContent = `${CLASS_LABELS[cls]}: ${risk} (${pct(score)})`;
    li.appendChild(head);
    const line = document.createElement("p");
    line.textContent = CLASS_INFO[cls][risk];
    li.appendChild(line);
    list.appendChild(li);
  }
  wrap.appendChild(list);

  if (result.reporting_flag) {
    const flag = document.createElement("p");
    flag.className = "flag";
    flag.textContent = "Reporting threshold met: this run would raise a reporting flag.";
    wrap.appendChild(flag);
  }

  return wrap;
}

// Fill in the result/event-JSON/KQL/SPL panels every module page shares.
// Pass config to get the scorecard rendering (per-class risk indicators);
// without it this falls back to a plain score list, so pages that have not
// moved onto renderScorecard yet still work unchanged.
export function showResult(module, result, context, config) {
  const el = (id) => document.getElementById(id);
  el("result").hidden = false;

  const summary = el("result-summary");
  summary.textContent = "";

  if (config) {
    summary.appendChild(renderScorecard(result, config));
  } else {
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
  }

  const event = buildEvent(module, result, context);
  el("event-json").textContent = JSON.stringify(event, null, 2);

  const q = detectionQueries(event);
  el("kql").textContent = q.kql;
  el("spl").textContent = q.spl;

  el("result").scrollIntoView({ behavior: "smooth" });
}
