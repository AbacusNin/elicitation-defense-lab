# elicitation-defense-lab

![ci](https://github.com/AbacusNin/elicitation-defense-lab/actions/workflows/ci.yml/badge.svg)

A defensive counter-elicitation assessment tool. Elicitation is the practice of pulling sensitive information out of someone through ordinary-sounding conversation rather than direct questioning. This package scores how exposed a person is to it, whether a specific conversation they had looks like an elicitation attempt, and whether they can recognize the techniques and respond correctly.

This is a grounded assessment, not a validated instrument. Every technique and question cites its source, and the taxonomy carries a confidence field. It gives a structured way to reason about elicitation exposure and to train recognition of it, not a certified psychometric measure of anyone's resistance. See `docs/limitations.md` for the full posture and the open verification items, and `docs/validation-research-proposal.md` for the study that would close the gap.

It is a companion to the flagship `insider-access-drift`. Where that tool watches technical access telemetry, this one addresses the human channel. The two share identity keys (`subject_id`, `peer_group`) so an analyst can correlate them, but nothing in this repository depends on the flagship.

## The three modules

One shared taxonomy of elicitation techniques (`taxonomy/techniques.json`), three scoring paradigms:

- **Self-assessment.** A susceptibility index. Likert items map to four technique classes (ego, reciprocity, social pressure, cognitive cue) plus an exposure score (role, access, public footprint, travel). Output is a vulnerability profile, not a pass or fail.
- **Interaction assessment.** An indicator rubric closer to a detection than a survey. An assessor marks which techniques and conversational-control patterns were present in a conversation they are reviewing. Output is a likelihood score, a tier, the matched techniques, and a reporting flag when the score crosses a threshold.
- **Knowledge.** Graded scenario drills, scored on three dimensions: recognition, countermeasure, and response (including the reporting channel correct for the taker's context). Every item gives feedback, because the evidence favors practice over a one-shot quiz.

Each module emits the same event shape (`schema.py`). The detections and the cross-feed correlation with `insider-access-drift` both operate on that shared event stream. See `docs/scoring.md` for how each module's score is built and why the weights are set where they are, and `docs/configuration.md` for every tunable dial.

## The static page

`web/index.html` runs all three modules client-side, no backend, no analytics, no transmission of any kind. Answers are scored locally and never leave the browser; in-progress state lives only in `localStorage`, wrapped so the page still works when storage is unavailable. The page's data is generated from the same taxonomy, banks, and default config the Python package uses (`web/build_data.py`), and a parity test checks the JavaScript and Python scorers agree.

## Detections and the SIEM path, stated honestly

`detections/kql` and `detections/spl` are reference queries over the emitted event schema, not over raw questionnaire answers. The assessments score a person's answers and emit a structured event; the KQL and SPL then run over a stream of those events to flag things like a high self-assessment tier or an interaction with the reporting flag set. Answers are never compiled directly into a detection. `elicitation_defense_lab/detections_ref.py` is the stdlib reference implementation that CI checks the KQL and SPL logic against, since CI has no KQL or Splunk engine. `detections/deployable/` holds real-schema templates for an actual ingestion pipeline; nothing in this repository has one, and building it is on whoever deploys this tool, not on this package. See `detections/deployable/README.md` for the detail.

## Development

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```

## Documentation

- `docs/configuration.md` - every dial in `Config`, its default, and how to override it.
- `docs/scoring.md` - how each module's score is built, and the weight philosophy behind the defaults.
- `docs/sources.md` - the consolidated bibliography and confidence marks.
- `docs/limitations.md` - the grounded-not-validated posture, in full, and the open verification items.
- `docs/validation-research-proposal.md` - the study that would validate this instrument.
