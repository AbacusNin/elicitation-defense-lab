"""Interaction-assessment indicator scorer.

Bank items mark either a technique (technique_id) or a conversational-control
pattern from the CDSE cross-cutting detection signal (pattern: true). Overall
likelihood is the diagnosticity-weighted share of present indicators; class
scores route only the technique hits through weighted_class_scores, so pattern
items and forward-referenced or composite-class technique ids affect the
overall score but not the four class buckets.
"""

import json
from pathlib import Path

from elicitation_defense_lab.config import Config
from elicitation_defense_lab.score.common import tier_for, weighted_class_scores
from elicitation_defense_lab.taxonomy import Technique

DEFAULT_BANK_PATH = (
    Path(__file__).resolve().parent.parent.parent / "taxonomy" / "banks" / "interaction.json"
)


def load_bank(path: str | None = None) -> list[dict]:
    """Load the interaction indicator bank from JSON."""
    file_path = Path(path) if path is not None else DEFAULT_BANK_PATH
    return json.loads(file_path.read_text(encoding="utf-8"))


def score_interaction(
    present: list[str], config: Config, techniques: list[Technique], bank: list[dict]
) -> dict:
    """Score an interaction assessment from the bank indicators marked present.

    Overall score is the sum of diagnosticity over present indicators divided
    by the sum over the whole bank, so marking every indicator scores 1.0 and
    marking none scores 0.0. Unknown ids in `present` are ignored.
    """
    by_id = {item["id"]: item for item in bank}
    total_diagnosticity = sum(item["diagnosticity"] for item in bank)
    present_diagnosticity = sum(
        by_id[item_id]["diagnosticity"] for item_id in present if item_id in by_id
    )
    overall_score = present_diagnosticity / total_diagnosticity if total_diagnosticity else 0.0

    hits = {}
    matched_techniques = []
    for item_id in present:
        item = by_id.get(item_id)
        if item is None or "technique_id" not in item:
            continue
        hits[item["technique_id"]] = 1.0
        matched_techniques.append(item["technique_id"])

    return {
        "overall_score": overall_score,
        "tier": tier_for(overall_score, config),
        "class_scores": weighted_class_scores(hits, techniques, config),
        "matched_techniques": matched_techniques,
        "reporting_flag": overall_score >= config.reporting_threshold,
    }
