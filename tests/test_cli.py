import json

from elicitation_defense_lab.cli import main


def test_cli_emits_valid_event(tmp_path, capsys):
    ans = tmp_path / "a.json"
    ans.write_text(json.dumps({}))
    rc = main(["interaction", "--answers", str(ans), "--context", "private_industry"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["module"] == "interaction"
    assert out["schema_version"]
