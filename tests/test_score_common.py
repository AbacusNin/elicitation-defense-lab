from elicitation_defense_lab.taxonomy import load_taxonomy
from elicitation_defense_lab.config import default_config
from elicitation_defense_lab.score.common import weighted_class_scores, tier_for


def test_tiers_partition():
    c = default_config()
    assert tier_for(0.0, c) == "low"
    assert tier_for(1.0, c) == "high"


def test_class_scores_normalized():
    techs = load_taxonomy()
    c = default_config()
    cs = weighted_class_scores({"A1": 1.0}, techs, c)  # A1 is ego
    assert 0.0 <= cs["ego"] <= 1.0
    assert cs["reciprocity"] == 0.0
