from elicitation_defense_lab.score.interaction import load_bank as load_inter
from elicitation_defense_lab.score.knowledge import load_bank as load_know
from elicitation_defense_lab.score.self_assess import load_bank as load_self
from elicitation_defense_lab.taxonomy import load_taxonomy


def test_banks_reference_valid_ids_and_carry_sources():
    ids = {t.id for t in load_taxonomy()}
    classes = {"ego", "reciprocity", "social_pressure", "cognitive_cue"}
    for item in load_self():
        assert item.get("technique_class") in classes or "exposure" in item
        assert item.get("source")
    for item in load_inter():
        assert item.get("technique_id") in ids or item.get("pattern")
        assert "diagnosticity" in item
    for item in load_know():
        assert item["technique_id"] in ids
        assert set(item["report_paths"]) >= {
            "dod",
            "federal",
            "cleared_contractor",
            "private_industry",
        }
        assert item["source"]
