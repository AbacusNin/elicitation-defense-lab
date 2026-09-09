// Shared result-rendering helper for the three module pages. Each page scores
// its own module with app.js, then hands the result here to fill in the
// result/event-JSON/KQL/SPL panels that all three pages share.

import { BASE_CLASSES, buildEvent, detectionQueries } from "./app.js";

function pct(x) {
  return `${(x * 100).toFixed(1)}%`;
}

export function showResult(module, result, context) {
  const el = (id) => document.getElementById(id);
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
