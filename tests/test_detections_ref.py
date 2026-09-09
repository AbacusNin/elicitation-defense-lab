from elicitation_defense_lab.detections_ref import flag_events


def test_reference_flags_report_and_high_tier():
    events = [
        {"module": "interaction", "reporting_flag": True, "subject_id": "u1", "tier": "high"},
        {"module": "self", "reporting_flag": None, "subject_id": "u2", "tier": "high"},
        {"module": "self", "reporting_flag": None, "subject_id": "u3", "tier": "low"},
    ]
    out = flag_events(events)
    assert "u1" in out["reported_interactions"]
    assert "u2" in out["high_self_assessments"]
    assert "u3" not in out["high_self_assessments"]


def test_subject_trend_groups_by_subject_and_orders_by_timestamp():
    events = [
        {"subject_id": "u1", "overall_score": 0.9, "timestamp": "2026-01-03T00:00:00Z"},
        {"subject_id": "u2", "overall_score": 0.1, "timestamp": "2026-01-01T00:00:00Z"},
        {"subject_id": "u1", "overall_score": 0.2, "timestamp": "2026-01-01T00:00:00Z"},
        {"subject_id": "u1", "overall_score": 0.5, "timestamp": None},
        # events with no subject_id do not start a trend group
        {"overall_score": 0.7, "timestamp": "2026-01-02T00:00:00Z"},
    ]
    out = flag_events(events)
    trend = out["subject_trend"]

    assert set(trend) == {"u1", "u2"}
    assert trend["u2"] == [{"timestamp": "2026-01-01T00:00:00Z", "overall_score": 0.1}]
    # u1's entries sort by timestamp ascending, with the missing timestamp sorted last
    assert trend["u1"] == [
        {"timestamp": "2026-01-01T00:00:00Z", "overall_score": 0.2},
        {"timestamp": "2026-01-03T00:00:00Z", "overall_score": 0.9},
        {"timestamp": None, "overall_score": 0.5},
    ]
