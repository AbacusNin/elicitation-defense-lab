"""Emitted-event schema: the shape every scoring run produces and the CLI reads back.

Kept standalone (no imports from the rest of the package) so the CLI and the
detections reference can both build against a single, stable contract without
pulling in the taxonomy or config internals.
"""

MODULES = {"self", "interaction", "knowledge"}
TIERS = {"low", "elevated", "high"}
CLASS_SCORE_KEYS = {"ego", "reciprocity", "social_pressure", "cognitive_cue"}

SCHEMA_VERSION = "1.0"
INSTRUMENT_VERSION = "1.0"


def build_event(
    module: str,
    *,
    tier: str,
    overall_score: float,
    class_scores: dict,
    timestamp: str,
    context: str,
    subject_id: str | None = None,
    peer_group: str | None = None,
    dimension_scores: dict | None = None,
    matched_techniques: list | None = None,
    reporting_flag: bool | None = None,
) -> dict:
    """Assemble an emitted event. Does not validate; call validate_event on the result."""
    return {
        "schema_version": SCHEMA_VERSION,
        "instrument_version": INSTRUMENT_VERSION,
        "module": module,
        "tier": tier,
        "overall_score": overall_score,
        "class_scores": class_scores,
        "timestamp": timestamp,
        "context": context,
        "subject_id": subject_id,
        "peer_group": peer_group,
        "dimension_scores": dimension_scores,
        "matched_techniques": matched_techniques,
        "reporting_flag": reporting_flag,
    }


def validate_event(event: dict) -> None:
    """Validate an emitted event's shape. Raises ValueError with a specific message on failure."""
    module = event.get("module")
    if module not in MODULES:
        raise ValueError(f"unknown module: {module!r}")

    tier = event.get("tier")
    if tier not in TIERS:
        raise ValueError(f"invalid tier: {tier!r}")

    class_scores = event.get("class_scores")
    if not isinstance(class_scores, dict) or set(class_scores) != CLASS_SCORE_KEYS:
        raise ValueError(f"class_scores must have exactly the keys {sorted(CLASS_SCORE_KEYS)}")

    has_dimension_scores = event.get("dimension_scores") is not None
    if has_dimension_scores and module != "knowledge":
        raise ValueError(f"dimension_scores is only valid on knowledge events, not {module!r}")

    has_matched_techniques = event.get("matched_techniques") is not None
    if has_matched_techniques and module != "interaction":
        raise ValueError(f"matched_techniques is only valid on interaction events, not {module!r}")

    has_reporting_flag = event.get("reporting_flag") is not None
    if has_reporting_flag and module != "interaction":
        raise ValueError(f"reporting_flag is only valid on interaction events, not {module!r}")
