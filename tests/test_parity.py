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
        assert abs(case["expected"]["overall_score"] - got["overall_score"]) < 1e-9
        assert case["expected"]["tier"] == got["tier"]
