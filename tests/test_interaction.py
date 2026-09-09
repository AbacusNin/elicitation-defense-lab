from elicitation_defense_lab.config import default_config
from elicitation_defense_lab.score.interaction import load_bank, score_interaction
from elicitation_defense_lab.taxonomy import load_taxonomy


def test_many_indicators_trip_reporting():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    present = [item["id"] for item in bank]
    res = score_interaction(present, c, techs, bank)
    assert res["reporting_flag"] is True
    assert res["matched_techniques"]


def test_no_indicators_no_report():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    res = score_interaction([], c, techs, bank)
    assert res["reporting_flag"] is False
    assert res["tier"] == "low"
