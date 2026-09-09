# Configuration

Every dial this tool exposes lives in one place: `elicitation_defense_lab/config.py`. `default_config()` reproduces the default behavior with no arguments, so you only set what you want to change.

## The tunable surface

One `Config` object, five fields, all overridable.

| Dial | Default | Meaning |
| --- | --- | --- |
| `class_weights` | ego 1.0, reciprocity 1.5, social_pressure 1.0, cognitive_cue 1.0 | how much each of the four technique classes counts toward a class or overall score |
| `technique_weights` | each technique's `default_weight` from `taxonomy/techniques.json` | per-technique weight, overriding a specific technique without touching its class |
| `tier_thresholds` | elevated 0.4, high 0.7 | the score cutoffs `tier_for` uses to label a result low, elevated, or high |
| `reporting_threshold` | 0.5 | the interaction score at or above which the module sets `reporting_flag` |
| `knowledge_dimension_weights` | recognition 1.0, countermeasure 1.0, response 1.0 | how the three knowledge sub-dimensions combine into the module's overall score |

Reciprocity's 1.5 is the one evidence-anchored default; see `docs/scoring.md` for why. Every other number here is a documented, provisional judgment call pending the validation study in `docs/validation-research-proposal.md`.

`class_weights` and `technique_weights` feed `weighted_class_scores` in `score/common.py`: a technique's contribution to its class is `hit_score * technique_weight * class_weight`, normalized against the class's ceiling (every technique in the class hitting at 1.0). The self-assessment module does not route through this helper; its class scores are the plain mean of that class's answered Likert items, so `technique_weights` has no effect there.

## Setting the dials

The operator interface is a JSON file passed to the CLI:

```json
{
  "class_weights": { "reciprocity": 1.8, "cognitive_cue": 1.2 },
  "tier_thresholds": { "high": 0.75 },
  "reporting_threshold": 0.6
}
```

```
python -m elicitation_defense_lab self --answers answers.json --config my-config.json
```

Any key you omit keeps its default. `load_config` merges each dict field key by key rather than replacing it wholesale, so a `class_weights` override that touches only `reciprocity` leaves `ego`, `social_pressure`, and `cognitive_cue` at their defaults. An unknown `class_weights` key, or a non-numeric value anywhere, raises `ValueError` rather than silently passing.

From code, if you are importing the package directly:

```python
from elicitation_defense_lab.config import default_config, load_config
from elicitation_defense_lab.score.self_assess import load_bank, score_self
from elicitation_defense_lab.taxonomy import load_taxonomy

config = load_config("my-config.json")  # or default_config()
techniques = load_taxonomy()
bank = load_bank()
result = score_self(answers, config, techniques, bank)
```

## The static page's copy of these dials

`web/build_data.py` copies `taxonomy/techniques.json`, the three banks, and a serialized default `Config` into `web/data/` at build time. The page's JavaScript scorer reads that same data, so the page and the CLI cannot drift on content. The page does not expose a `--config` equivalent; it always runs the shipped defaults. An operator who wants different weights on the page would need to regenerate `web/data/config.json` and rebuild.

Self and knowledge also draw a random subset of their bank per session (self about 18 of 94, balanced forward and reverse per class; knowledge about 9 of 30, with each item's answer-choice positions reshuffled on every render) and score over exactly that subset; interaction shows and scores its full bank of 34 every time, grouped into five collapsible sections. This sampling lives in `web/ui.js` and each page's own script, not in `Config`; it is a page-side presentation choice, not a tunable dial, and the CLI always scores whatever answer set it is given in full.
