import json
import pathlib
import shutil
import subprocess

import pytest

FIXTURES = pathlib.Path("tests/fixtures/parity_cases.json")
RUNNER = pathlib.Path("tests/parity/run_js.mjs")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_js_scoring_matches_python():
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    out = subprocess.run(
        ["node", str(RUNNER)],
        capture_output=True,
        text=True,
        check=True,
    )
    js = json.loads(out.stdout)
    assert len(cases) == len(js)
    for case, got in zip(cases, js):
        expected = case["expected"]
        assert abs(expected["overall_score"] - got["overall_score"]) < 1e-9
        assert expected["tier"] == got["tier"]
        for cls, score in expected["class_scores"].items():
            assert abs(score - got["class_scores"][cls]) < 1e-9
        if "dimension_scores" in expected:
            for dim, score in expected["dimension_scores"].items():
                assert abs(score - got["dimension_scores"][dim]) < 1e-9
        if "matched_techniques" in expected:
            assert set(expected["matched_techniques"]) == set(got["matched_techniques"])
        if "reporting_flag" in expected:
            assert expected["reporting_flag"] == got["reporting_flag"]
        if "exposure_score" in expected:
            assert abs(expected["exposure_score"] - got["exposure_score"]) < 1e-9
