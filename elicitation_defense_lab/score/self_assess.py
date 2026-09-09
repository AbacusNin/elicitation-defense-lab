"""Self-assessment susceptibility scorer.

Self-assessment items are tagged directly with a technique_class (or with
exposure), not with a technique id, so this module does not route through
weighted_class_scores (that helper buckets technique-id hits and belongs to
the interaction scorer). Instead each class subscore is the plain mean of
that class's answered Likert items, already normalized to [0,1].
"""

import json
from pathlib import Path

from elicitation_defense_lab.config import Config
from elicitation_defense_lab.score.common import BASE_CLASSES, tier_for
from elicitation_defense_lab.taxonomy import Technique

DEFAULT_BANK_PATH = (
    Path(__file__).resolve().parent.parent.parent / "taxonomy" / "banks" / "self_assessment.json"
)


def load_bank(path: str | None = None) -> list[dict]:
    """Load the self-assessment item bank from JSON."""
    file_path = Path(path) if path is not None else DEFAULT_BANK_PATH
    return json.loads(file_path.read_text(encoding="utf-8"))


def _item_value(item: dict, answer: int) -> float:
    """Convert a 0-4 Likert answer to [0,1], flipping direction on reverse items."""
    if not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer <= 4:
        raise ValueError(f"answer for {item['id']!r} must be an integer 0-4, got {answer!r}")
    value = answer / 4
    return 1 - value if item.get("reverse") else value


def score_self(
    answers: dict[str, int],
    config: Config,
    techniques: list[Technique],  # unused: self-assessment items carry no technique id
    bank: list[dict],
) -> dict:
    """Score a self-assessment run.

    Each class score is the mean of that class's answered items. A class
    with no answered items scores 0.0. The overall score combines the four
    class scores (weighted by config.class_weights, normalized) with the
    exposure score in equal measure, then tiers the result with tier_for.
    """
    class_sums = dict.fromkeys(BASE_CLASSES, 0.0)
    class_counts = dict.fromkeys(BASE_CLASSES, 0)
    exposure_sum = 0.0
    exposure_count = 0

    by_id = {item["id"]: item for item in bank}
    for item_id, answer in answers.items():
        item = by_id.get(item_id)
        if item is None:
            continue
        value = _item_value(item, answer)
        if item.get("exposure"):
            exposure_sum += value
            exposure_count += 1
        elif item.get("technique_class") in BASE_CLASSES:
            class_sums[item["technique_class"]] += value
            class_counts[item["technique_class"]] += 1

    class_scores = {
        cls: class_sums[cls] / class_counts[cls] if class_counts[cls] else 0.0
        for cls in BASE_CLASSES
    }
    exposure_score = exposure_sum / exposure_count if exposure_count else 0.0

    weight_total = sum(config.class_weights.get(cls, 1.0) for cls in BASE_CLASSES)
    class_component = (
        sum(class_scores[cls] * config.class_weights.get(cls, 1.0) for cls in BASE_CLASSES)
        / weight_total
        if weight_total
        else 0.0
    )
    overall_score = (class_component + exposure_score) / 2

    return {
        "overall_score": overall_score,
        "tier": tier_for(overall_score, config),
        "class_scores": class_scores,
        "exposure_score": exposure_score,
    }
