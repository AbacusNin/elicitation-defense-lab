import pytest

from elicitation_defense_lab.taxonomy import Technique, load_taxonomy  # noqa: F401


def test_loads_seed_records():
    techs = load_taxonomy()
    by_id = {t.id: t for t in techs}
    assert "A1" in by_id
    assert by_id["A1"].technique_class == "ego"
    assert by_id["A1"].sources  # non-empty
    assert isinstance(by_id["A1"].default_weight, float)


def test_rejects_bad_class(tmp_path):
    bad = tmp_path / "t.json"
    bad.write_text('[{"id":"X","name":"x","family":"elicitation",'
                   '"technique_class":"nonsense","definition":"d","mechanism":"m",'
                   '"recognition_cue":"r","countermeasure":"c","sources":["s"],'
                   '"confidence":"high","default_weight":1.0}]')
    with pytest.raises(ValueError):
        load_taxonomy(str(bad))
