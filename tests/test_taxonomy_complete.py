from elicitation_defense_lab.taxonomy import load_taxonomy


def test_all_families_present_and_well_formed():
    techs = load_taxonomy()
    fams = {t.family for t in techs}
    assert {"elicitation", "interrogation", "se_vector"} <= fams
    # Catalog A has 28 elicitation techniques
    assert sum(t.family == "elicitation" for t in techs) >= 28
    # Catalog B has 18 interrogation approaches
    assert sum(t.family == "interrogation" for t in techs) >= 18
    for t in techs:
        assert t.sources and t.definition and t.countermeasure
        assert t.confidence in {"high", "medium", "corroborated"}
