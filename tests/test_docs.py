import pathlib
import subprocess


def test_required_docs_exist_and_state_grounded():
    names = ["configuration", "scoring", "sources", "limitations", "validation-research-proposal"]
    for name in names:
        p = pathlib.Path(f"docs/{name}.md")
        assert p.exists() and p.read_text().strip()
    lim = pathlib.Path("docs/limitations.md").read_text().lower()
    assert "grounded" in lim and "not" in lim and "valid" in lim  # states the not-validated posture


def test_no_coauthor_trailers_in_repo_docs():
    # git ls-files, not rglob: rglob would also read ignored local files that are
    # not part of the published repo.
    result = subprocess.run(
        ["git", "ls-files", "*.md"], capture_output=True, text=True, check=True
    )
    for name in result.stdout.splitlines():
        if not name.strip():
            continue
        text = pathlib.Path(name).read_text(encoding="utf-8").lower()
        assert "co-authored-by:" not in text, name
