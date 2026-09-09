"""Reference implementation of the detections that run over emitted events.

Pure standard library, no pandas or other runtime dependency, matching the
rest of the package. The logic here is a filter and group over a list of
event dicts, which stdlib handles fine without pulling in a data-frame
library for it.

This is the fast-gate check: it runs in CI against synthetic events and
keeps the KQL and SPL detection logic honest, since those can't run without
a real engine. Phase 2 validates the native rules directly against
Kustainer (KQL) and a Splunk instance (SPL).

The three views mirror the detections/kql and detections/spl files, which
query the same three things over the emitted ElicitationAssessment
table/index: high self-assessment tier, interaction events with the
reporting flag set, and a per-subject trend of scores over time.
"""


def flag_events(events: list[dict]) -> dict:
    """Flag high-tier self-assessments, reported interactions, and build
    a per-subject score trend from a list of emitted events.
    """
    high_self_assessments = [
        e["subject_id"]
        for e in events
        if e.get("module") == "self" and e.get("tier") == "high" and e.get("subject_id")
    ]
    reported_interactions = [
        e["subject_id"]
        for e in events
        if e.get("module") == "interaction"
        and e.get("reporting_flag") is True
        and e.get("subject_id")
    ]

    subject_trend: dict[str, list[dict]] = {}
    for e in events:
        subject_id = e.get("subject_id")
        if not subject_id:
            continue
        subject_trend.setdefault(subject_id, []).append(
            {"timestamp": e.get("timestamp"), "overall_score": e.get("overall_score")}
        )
    for entries in subject_trend.values():
        entries.sort(key=lambda entry: (entry["timestamp"] is None, entry["timestamp"]))

    return {
        "reported_interactions": reported_interactions,
        "high_self_assessments": high_self_assessments,
        "subject_trend": subject_trend,
    }
