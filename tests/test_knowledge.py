from elicitation_defense_lab.config import default_config
from elicitation_defense_lab.score.knowledge import load_bank, score_knowledge
from elicitation_defense_lab.taxonomy import load_taxonomy


def test_all_correct_scores_full_and_context_report_accepted():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {}
    for item in bank:
        resp = item["report_paths"]["private_industry"]  # context-correct response
        answers[item["id"]] = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": resp,
        }
    res = score_knowledge(answers, c, techs, bank, context="private_industry")
    assert res["dimension_scores"]["recognition"] == 1.0
    assert res["dimension_scores"]["response"] == 1.0
    assert res["overall_score"] == 1.0


def test_wrong_context_report_scores_zero_on_response():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {}
    for item in bank:
        # answer with the "dod" report path while grading against "federal"
        answers[item["id"]] = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": item["report_paths"]["dod"],
        }
    res = score_knowledge(answers, c, techs, bank, context="federal")
    assert res["dimension_scores"]["response"] == 0.0


def test_unknown_context_falls_back_to_general():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {}
    for item in bank:
        answers[item["id"]] = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": item["report_paths"]["general"],
        }
    res = score_knowledge(answers, c, techs, bank, context="some_unlisted_context")
    assert res["dimension_scores"]["response"] == 1.0


def test_partial_credit_near_miss():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    item = next(i for i in bank if "partial" in i and "recognition" in i["partial"])
    answers = {
        item["id"]: {
            "recognition": item["partial"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": item["report_paths"]["general"],
        }
    }
    res = score_knowledge(answers, c, techs, bank, context="general")
    assert res["dimension_scores"]["recognition"] == 0.5


def test_all_wrong_scores_zero_and_low_tier():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {
        item["id"]: {
            "recognition": "not-a-real-choice",
            "countermeasure": "not-a-real-choice",
            "response": "not-a-real-choice",
        }
        for item in bank
    }
    res = score_knowledge(answers, c, techs, bank, context="general")
    assert res["overall_score"] == 0.0
    assert res["tier"] == "low"


def test_class_scores_exclude_composite_technique():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    scharff_item = next(i for i in bank if i["technique_id"] == "A28")
    answers = {
        scharff_item["id"]: {
            "recognition": scharff_item["correct"]["recognition"],
            "countermeasure": scharff_item["correct"]["countermeasure"],
            "response": scharff_item["report_paths"]["general"],
        }
    }
    res = score_knowledge(answers, c, techs, bank, context="general")
    assert set(res["class_scores"]) == {"ego", "reciprocity", "social_pressure", "cognitive_cue"}
    # A28 is a composite technique, not one of the four base classes, so a
    # perfect score on it must not land in any class bucket.
    assert all(value == 0.0 for value in res["class_scores"].values())


def test_feedback_has_one_entry_per_item():
    techs = load_taxonomy()
    c = default_config()
    bank = load_bank()
    answers = {
        item["id"]: {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": item["report_paths"]["general"],
        }
        for item in bank
    }
    res = score_knowledge(answers, c, techs, bank, context="general")
    assert len(res["feedback"]) == len(bank)


def test_bank_items_have_four_org_contexts_and_general():
    bank = load_bank()
    assert len(bank) > 0
    for item in bank:
        keys = set(item["report_paths"])
        assert {"general", "dod", "federal", "cleared_contractor", "private_industry"} <= keys
