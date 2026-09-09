from elicitation_defense_lab.config import default_config
from elicitation_defense_lab.score.self_assess import load_bank, score_self
from elicitation_defense_lab.taxonomy import load_taxonomy


def test_max_answers_give_high_tier():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {item["id"]: 4 for item in bank}
    res = score_self(answers, c, techs, bank)
    assert res["tier"] in {"elevated", "high"}
    assert set(res["class_scores"]) == {"ego", "reciprocity", "social_pressure", "cognitive_cue"}


def test_min_answers_give_low_tier():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    # The lowest-susceptibility answer is 0 on a forward item and 4 (agree
    # with the protective statement) on a reverse item.
    answers = {item["id"]: 4 if item["reverse"] else 0 for item in bank}
    res = score_self(answers, c, techs, bank)
    assert res["tier"] == "low"
    assert res["overall_score"] == 0.0


def test_reverse_items_flip_direction():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    reverse_item = next(item for item in bank if item["reverse"])
    answers = {reverse_item["id"]: 4}
    res = score_self(answers, c, techs, bank)
    cls = reverse_item["technique_class"]
    assert res["class_scores"][cls] == 0.0


def test_unanswered_class_scores_zero():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    ego_item = next(item for item in bank if item.get("technique_class") == "ego")
    res = score_self({ego_item["id"]: 4}, c, techs, bank)
    assert res["class_scores"]["reciprocity"] == 0.0


def test_bank_items_have_sources():
    bank = load_bank()
    assert len(bank) > 0
    for item in bank:
        assert item["source"]
        assert item.get("technique_class") is not None or item.get("exposure") is True
