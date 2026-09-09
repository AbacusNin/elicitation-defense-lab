"""Shared scoring helpers used by every scorer: class weighting and tiering.

Kept pure (dict/str in, dict/str out, no I/O) so scorers can compose these
without pulling in taxonomy or config loading themselves.
"""

from elicitation_defense_lab.config import Config
from elicitation_defense_lab.taxonomy import Technique

# The four base classes a technique hit can be bucketed into. "composite"
# techniques (e.g. A28 Scharff) are handled by the scorer tasks, not here.
BASE_CLASSES = ("ego", "reciprocity", "social_pressure", "cognitive_cue")


def weighted_class_scores(
    hits: dict[str, float], techniques: list[Technique], config: Config
) -> dict[str, float]:
    """Group technique hits by class, weight them, and normalize to [0,1].

    Each hit's contribution is hit_score * technique_weight * class_weight.
    A class's bucket is that sum divided by the max achievable for the class
    (every technique in the class hit at 1.0), so an empty class scores 0.0.
    Hits for unknown ids and composite-class techniques are ignored.
    """
    by_id = {t.id: t for t in techniques}
    raw = dict.fromkeys(BASE_CLASSES, 0.0)
    ceiling = dict.fromkeys(BASE_CLASSES, 0.0)

    for t in techniques:
        if t.technique_class not in BASE_CLASSES:
            continue
        weight = config.technique_weights.get(t.id, t.default_weight)
        class_weight = config.class_weights.get(t.technique_class, 1.0)
        ceiling[t.technique_class] += weight * class_weight

    for tech_id, hit_score in hits.items():
        t = by_id.get(tech_id)
        if t is None or t.technique_class not in BASE_CLASSES:
            continue
        weight = config.technique_weights.get(t.id, t.default_weight)
        class_weight = config.class_weights.get(t.technique_class, 1.0)
        raw[t.technique_class] += hit_score * weight * class_weight

    return {
        cls: raw[cls] / ceiling[cls] if ceiling[cls] > 0 else 0.0
        for cls in BASE_CLASSES
    }


def tier_for(score: float, config: Config) -> str:
    """Map a score to a tier using config.tier_thresholds."""
    if score >= config.tier_thresholds["high"]:
        return "high"
    if score >= config.tier_thresholds["elevated"]:
        return "elevated"
    return "low"
