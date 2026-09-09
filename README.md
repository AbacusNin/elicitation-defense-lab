# elicitation-defense-lab

![ci](https://github.com/AbacusNin/elicitation-defense-lab/actions/workflows/ci.yml/badge.svg)

A lab for testing how well a set of conversational responses resist elicitation, the practice of pulling sensitive information out of someone through ordinary-sounding conversation rather than direct questioning. It scores transcripts against known elicitation techniques and flags where a response gave up more than it needed to.

This is a grounded assessment, not a validated instrument. It gives a structured way to look at a conversation and reason about where it leaked, not a certified measure of anyone's resistance to elicitation.

## Status

Scaffolding only. The package currently exposes `elicitation_defense_lab.__version__` and nothing else. The detection and scoring logic lands in later tasks.

## Development

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```
