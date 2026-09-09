"""Config object for scoring weights, tier thresholds, and reporting cutoff.

The reciprocity class weight is evidence-anchored: van der Kleij's work on
elicitation susceptibility found reciprocity-based techniques the strongest
predictor of compliance, so it is set above the other three classes by
default. The remaining defaults (the other class weights, tier thresholds,
reporting threshold, knowledge dimension weights) are provisional and meant
to be tuned once real scoring data exists.
"""

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

from elicitation_defense_lab.taxonomy import TECHNIQUE_CLASSES, load_taxonomy

CLASS_WEIGHT_KEYS = TECHNIQUE_CLASSES - {"composite"}


@dataclass(frozen=True)
class Config:
    class_weights: dict[str, float]
    technique_weights: dict[str, float]
    tier_thresholds: dict[str, float]
    reporting_threshold: float
    knowledge_dimension_weights: dict[str, float] = field(
        default_factory=lambda: {"recognition": 1.0, "countermeasure": 1.0, "response": 1.0}
    )


def default_config() -> Config:
    return Config(
        class_weights={
            "ego": 1.0,
            "reciprocity": 1.5,
            "social_pressure": 1.0,
            "cognitive_cue": 1.0,
        },
        technique_weights={t.id: t.default_weight for t in load_taxonomy()},
        tier_thresholds={"elevated": 0.4, "high": 0.7},
        reporting_threshold=0.5,
        knowledge_dimension_weights={"recognition": 1.0, "countermeasure": 1.0, "response": 1.0},
    )


def load_config(path: str) -> Config:
    """Load a JSON override and merge it onto the defaults.

    Raises ValueError on an unknown class-weight key or a non-numeric weight.
    Any field the override omits keeps its default value; dict fields are
    merged key by key rather than replaced wholesale.
    """
    overrides = json.loads(Path(path).read_text(encoding="utf-8"))
    config = default_config()

    if "class_weights" in overrides:
        merged = dict(config.class_weights)
        for key, value in overrides["class_weights"].items():
            if key not in CLASS_WEIGHT_KEYS:
                raise ValueError(f"unknown class-weight key: {key!r}")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"class weight for {key!r} is not numeric: {value!r}")
            merged[key] = float(value)
        config = replace(config, class_weights=merged)

    if "technique_weights" in overrides:
        merged = dict(config.technique_weights)
        for key, value in overrides["technique_weights"].items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"technique weight for {key!r} is not numeric: {value!r}")
            merged[key] = float(value)
        config = replace(config, technique_weights=merged)

    if "tier_thresholds" in overrides:
        merged = dict(config.tier_thresholds)
        for key, value in overrides["tier_thresholds"].items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"tier threshold for {key!r} is not numeric: {value!r}")
            merged[key] = float(value)
        config = replace(config, tier_thresholds=merged)

    if "knowledge_dimension_weights" in overrides:
        merged = dict(config.knowledge_dimension_weights)
        for key, value in overrides["knowledge_dimension_weights"].items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"knowledge weight for {key!r} is not numeric: {value!r}")
            merged[key] = float(value)
        config = replace(config, knowledge_dimension_weights=merged)

    if "reporting_threshold" in overrides:
        value = overrides["reporting_threshold"]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"reporting_threshold is not numeric: {value!r}")
        config = replace(config, reporting_threshold=float(value))

    return config
