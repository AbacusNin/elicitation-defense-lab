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


def test_constant_answers_cannot_game_the_score():
    # Anti-gaming property: every class (and exposure) is balanced roughly
    # 10 forward / 10 reverse items, so answering every item the same value
    # must land near neutral, not at either tier extreme. A user who mashes
    # the same button through the whole bank should not be able to read as
    # either especially safe or especially susceptible.
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()

    all_high = {item["id"]: 4 for item in bank}
    res_high = score_self(all_high, c, techs, bank)
    assert 0.35 <= res_high["overall_score"] <= 0.65
    assert res_high["tier"] != "high"
    assert res_high["tier"] != "low"

    all_low = {item["id"]: 0 for item in bank}
    res_low = score_self(all_low, c, techs, bank)
    assert 0.35 <= res_low["overall_score"] <= 0.65
    assert res_low["tier"] != "high"
    assert res_low["tier"] != "low"
