import pytest

from elicitation_defense_lab.schema import SCHEMA_VERSION, build_event, validate_event


def test_interaction_event_valid():
    ev = build_event(
        "interaction",
        tier="elevated",
        overall_score=0.6,
        class_scores={"ego": 0.0, "reciprocity": 0.6, "social_pressure": 0.0, "cognitive_cue": 0.0},
        timestamp="2026-09-08T00:00:00Z",
        context="private_industry",
        matched_techniques=["A8"],
        reporting_flag=True,
    )
    assert ev["schema_version"] == SCHEMA_VERSION
    assert ev["subject_id"] is None
    validate_event(ev)  # does not raise


def test_bad_module_raises():
    with pytest.raises(ValueError):
        validate_event({"schema_version": SCHEMA_VERSION, "module": "nope"})


def test_self_event_valid():
    ev = build_event(
        "self",
        tier="low",
        overall_score=0.1,
        class_scores={"ego": 0.1, "reciprocity": 0.0, "social_pressure": 0.0, "cognitive_cue": 0.0},
        timestamp="2026-09-08T00:00:00Z",
        context="private_industry",
    )
    validate_event(ev)
    assert ev["peer_group"] is None
    assert ev["subject_id"] is None


def test_knowledge_event_valid():
    ev = build_event(
        "knowledge",
        tier="high",
        overall_score=0.8,
        class_scores={"ego": 0.0, "reciprocity": 0.0, "social_pressure": 0.0, "cognitive_cue": 0.0},
        timestamp="2026-09-08T00:00:00Z",
        context="private_industry",
        dimension_scores={"recognition": 0.9, "countermeasure": 0.7, "response": 0.8},
    )
    validate_event(ev)


def test_bad_tier_raises():
    with pytest.raises(ValueError):
        validate_event(
            {
                "schema_version": SCHEMA_VERSION,
                "module": "self",
                "tier": "extreme",
                "overall_score": 0.1,
                "class_scores": {
                    "ego": 0.0,
                    "reciprocity": 0.0,
                    "social_pressure": 0.0,
                    "cognitive_cue": 0.0,
                },
            }
        )


def test_missing_class_scores_key_raises():
    with pytest.raises(ValueError):
        validate_event(
            {
                "schema_version": SCHEMA_VERSION,
                "module": "self",
                "tier": "low",
                "overall_score": 0.1,
                "class_scores": {"ego": 0.0, "reciprocity": 0.0, "social_pressure": 0.0},
            }
        )


def test_dimension_scores_on_non_knowledge_raises():
    ev = {
        "schema_version": SCHEMA_VERSION,
        "module": "self",
        "tier": "low",
        "overall_score": 0.1,
        "class_scores": {
            "ego": 0.0,
            "reciprocity": 0.0,
            "social_pressure": 0.0,
            "cognitive_cue": 0.0,
        },
        "dimension_scores": {"recognition": 0.5, "countermeasure": 0.5, "response": 0.5},
    }
    with pytest.raises(ValueError):
        validate_event(ev)


def test_matched_techniques_on_non_interaction_raises():
    ev = {
        "schema_version": SCHEMA_VERSION,
        "module": "self",
        "tier": "low",
        "overall_score": 0.1,
        "class_scores": {
            "ego": 0.0,
            "reciprocity": 0.0,
            "social_pressure": 0.0,
            "cognitive_cue": 0.0,
        },
        "matched_techniques": ["A8"],
    }
    with pytest.raises(ValueError):
        validate_event(ev)
