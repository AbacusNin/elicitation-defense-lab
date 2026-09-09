"""Knowledge-check scorer: three-dimension scenario grading.

Each bank item is a scenario with three graded dimensions: recognition (did
they name the technique), countermeasure (did they pick the taught response),
and response (did they pick the reporting channel correct for their org
context). The first two have a single correct choice per item; the third is
resolved per call from the item's report_paths, keyed by context and falling
back to "general" for a context the item doesn't carry.
"""

import json
from pathlib import Path

from elicitation_defense_lab.config import Config
from elicitation_defense_lab.score.common import tier_for, weighted_class_scores
from elicitation_defense_lab.taxonomy import Technique

DEFAULT_BANK_PATH = (
    Path(__file__).resolve().parent.parent.parent / "taxonomy" / "banks" / "knowledge.json"
)

DIMENSIONS = ("recognition", "countermeasure", "response")


def load_bank(path: str | None = None) -> list[dict]:
    """Load the knowledge scenario bank from JSON."""
    file_path = Path(path) if path is not None else DEFAULT_BANK_PATH
    return json.loads(file_path.read_text(encoding="utf-8"))


def _response_correct_id(item: dict, context: str) -> str:
    report_paths = item["report_paths"]
    return report_paths.get(context, report_paths["general"])


def _dimension_score(item: dict, dimension: str, chosen: str | None, correct_id: str) -> float:
    if chosen == correct_id:
        return 1.0
    if item.get("partial", {}).get(dimension) == chosen:
        return 0.5
    return 0.0


def _choice_text(item: dict, dimension: str, choice_id: str | None) -> str | None:
    """Text for a choice id within one dimension of one item, or None if unset."""
    if choice_id is None:
        return None
    for choice in item["choices"][dimension]:
        if choice["id"] == choice_id:
            return choice["text"]
    return choice_id


def _dimension_feedback(
    item: dict, dimension: str, chosen_id: str | None, correct_id: str, score: float
) -> dict:
    """Per-dimension feedback keyed off the user's own choice, mirroring web/app.js's
    scoreKnowledge: what was chosen, what was correct, and the explanation for the
    choice actually made (not always the correct choice's explanation).
    """
    if chosen_id is None:
        status = "unanswered"
    elif score == 1.0:
        status = "correct"
    elif score == 0.5:
        status = "partial"
    else:
        status = "incorrect"

    explanation_id = chosen_id if chosen_id is not None else correct_id
    return {
        "chosen_id": chosen_id,
        "chosen_text": _choice_text(item, dimension, chosen_id),
        "correct_id": correct_id,
        "correct_text": _choice_text(item, dimension, correct_id),
        "score": score,
        "status": status,
        "explanation": item["feedback"][dimension].get(explanation_id),
    }


def score_knowledge(
    answers: dict[str, dict],
    config: Config,
    techniques: list[Technique],
    bank: list[dict],
    context: str,
) -> dict:
    """Score a knowledge-check run.

    Each answered item is graded on all three dimensions against the item's
    `correct` ids, with the response dimension resolved against
    `report_paths[context]` (falling back to `report_paths["general"]`). A
    defined `partial` near-miss scores 0.5; anything else scores 0.0. Items
    with no answer are skipped entirely (not counted as wrong).
    """
    dim_sums = dict.fromkeys(DIMENSIONS, 0.0)
    dim_counts = dict.fromkeys(DIMENSIONS, 0)
    hits: dict[str, float] = {}
    feedback = []

    for item in bank:
        answer = answers.get(item["id"])
        if answer is None:
            continue

        correct_ids = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": _response_correct_id(item, context),
        }

        item_scores = {}
        per_dimension = {}
        for dimension in DIMENSIONS:
            chosen_id = answer.get(dimension)
            score = _dimension_score(item, dimension, chosen_id, correct_ids[dimension])
            item_scores[dimension] = score
            dim_sums[dimension] += score
            dim_counts[dimension] += 1
            per_dimension[dimension] = _dimension_feedback(
                item, dimension, chosen_id, correct_ids[dimension], score
            )

        hits[item["technique_id"]] = sum(item_scores.values()) / len(DIMENSIONS)

        feedback.append(
            {
                "item_id": item["id"],
                "technique_id": item["technique_id"],
                **per_dimension,
            }
        )

    dimension_scores = {
        dimension: dim_sums[dimension] / dim_counts[dimension] if dim_counts[dimension] else 0.0
        for dimension in DIMENSIONS
    }

    weights = config.knowledge_dimension_weights
    weight_total = sum(weights.get(d, 1.0) for d in DIMENSIONS)
    overall_score = (
        sum(dimension_scores[d] * weights.get(d, 1.0) for d in DIMENSIONS) / weight_total
        if weight_total
        else 0.0
    )

    return {
        "overall_score": overall_score,
        "tier": tier_for(overall_score, config),
        "class_scores": weighted_class_scores(hits, techniques, config),
        "dimension_scores": dimension_scores,
        "feedback": feedback,
    }
