# elicitation-defense-lab

![ci](https://github.com/AbacusNin/elicitation-defense-lab/actions/workflows/ci.yml/badge.svg)

A defensive counter-elicitation assessment tool. Elicitation is the practice of pulling sensitive information out of someone through ordinary-sounding conversation rather than direct questioning. This package scores how exposed a person is to it, whether a specific conversation they had looks like an elicitation attempt, and whether they can recognize the techniques and respond correctly.

This is a grounded assessment, not a validated instrument. Every technique and question cites its source, and the taxonomy carries a confidence field. It gives a structured way to reason about elicitation exposure and to train recognition of it, not a certified psychometric measure of anyone's resistance. See `docs/limitations.md` for the full posture and the open verification items, and `docs/validation-research-proposal.md` for the study that would close the gap.

It is a companion to the flagship `insider-access-drift`. Where that tool watches technical access telemetry, this one addresses the human channel. The two share identity keys (`subject_id`, `peer_group`) so an analyst can correlate them, but nothing in this repository depends on the flagship.

## The three modules

One shared taxonomy of elicitation techniques (`taxonomy/techniques.json`), three scoring paradigms:

- **Self-assessment.** A susceptibility index, framed as a self-reflection prompt rather than a skills test. Items ask about past-behavior frequency ("in the last year, when someone praised my expertise more than the situation called for, I...") rather than abstract belief, with balanced reverse-scoring so agreeing is not always the risk-indicating direction. Likert items map to four technique classes (ego, reciprocity, social pressure, cognitive cue) plus an exposure score (role, access, public footprint, travel). Output is a vulnerability profile, not a pass or fail; the knowledge check below is the module that actually tests skill.
- **Interaction assessment.** A yes/no/unsure questionnaire closer to a detection than a survey. Each item shows a technique's name, a one-line description, and a concrete example, and asks whether it happened in a conversation the taker is reviewing. Only the items answered yes get scored. Output is a likelihood score, a tier, the matched techniques, and a reporting flag when the score crosses a threshold.
- **Knowledge.** Graded scenario drills, scored on three dimensions: recognition, countermeasure, and response (including the reporting channel correct for the taker's context). Every item gives feedback, because the evidence favors practice over a one-shot quiz.

Each module emits the same event shape (`schema.py`). The detections and the cross-feed correlation with `insider-access-drift` both operate on that shared event stream. See `docs/scoring.md` for how each module's score is built and why the weights are set where they are, and `docs/configuration.md` for every tunable dial.

## The static page

`web/index.html` is a landing hub with three cards linking to the module pages, `web/self.html`, `web/interaction.html`, and `web/knowledge.html`. Each page runs client-side, no backend, no analytics, no transmission of any kind, and links back to the hub. Answers are scored locally and never leave the browser; in-progress state lives only in `localStorage`, wrapped so the page still works when storage is unavailable. All three share the scoring functions in `web/app.js`.

The self-assessment bank holds 40 items and knowledge holds 30 scenarios; each is larger than what any one session sees. On load, self and knowledge shuffle their bank and draw a subset: self draws about 18 items, stratified across the four psychological classes plus a couple of exposure items; knowledge draws about 9. Each of those two modules scores over exactly the subset it showed, not the full bank, so a retake shows a different set and a different score is expected. Interaction holds 34 items (28 technique questions plus 6 conversational-control patterns) and shows and scores all of them every time, grouped into five collapsible sections (the four psychological classes plus conversational-control patterns) with a dropdown to jump between groups.

The self and interaction pages render a scorecard: an overall tier plus a per-class risk indicator (low, elevated, or high) for ego, reciprocity, social pressure, and cognitive cue, each with a line of countermeasure guidance. Interaction surfaces its reporting flag as the headline risk indicator, above the class breakdown. The knowledge page renders a three-dimension competency scorecard (recognition, countermeasure, response) instead, since a high knowledge score is the good outcome, plus per-item feedback explaining the correct answer on all three dimensions. The reporting-context selector on the interaction and knowledge pages sets which reporting channel the flag and the response answers name.

The page's data is generated from the same taxonomy, banks, and default config the Python package uses (`web/build_data.py`), and a parity test checks the JavaScript and Python scorers agree.

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
