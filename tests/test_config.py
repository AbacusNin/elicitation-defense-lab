import json

import pytest

from elicitation_defense_lab.config import default_config, load_config


def test_reciprocity_weighted_heaviest_by_default():
    c = default_config()
    assert c.class_weights["reciprocity"] == max(c.class_weights.values())


def test_override_merges(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"reporting_threshold": 0.9}))
    c = load_config(str(p))
    assert c.reporting_threshold == 0.9
    assert c.class_weights  # untouched defaults survive


def test_bad_config_raises(tmp_path):
    p = tmp_path / "c.json"
    p.write_text('{"class_weights": {"nonsense": 2.0}}')
    with pytest.raises(ValueError):
        load_config(str(p))
