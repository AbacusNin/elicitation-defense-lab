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
