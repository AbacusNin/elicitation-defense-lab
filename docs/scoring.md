# Scoring

One spine, three paradigms. All three modules score against the same taxonomy of techniques (`taxonomy/techniques.json`) and the same four technique classes: ego, reciprocity, social pressure, and cognitive cue. Each module asks a different question, so each scores differently, but a class score always means the same thing wherever it appears: how much that class of manipulation showed up, weighted.

## Self-assessment: a susceptibility index

The self-assessment asks how a person would react, not what happened to them. Each answered Likert item (0 to 4) is tagged with a technique class or marked as an exposure item. A class's subscore is the plain mean of that class's answered items, already normalized to 0 through 1. Exposure items (role, access, public footprint, travel) average into a separate exposure score the same way.

The overall score is the class-weighted average of the four class subscores, combined in equal measure with the exposure score, then mapped to a tier with `tier_for`. Because items are already scored per person rather than per technique hit, `technique_weights` and `weighted_class_scores` do not apply here. The output is a vulnerability profile across four classes plus exposure, not a pass or fail.

## Interaction assessment: an indicator rubric

The interaction module scores a conversation someone else already had, so it works closer to a detection than a survey. The assessor marks which indicators from the interaction bank were present: specific technique hits, or cross-cutting conversational-control patterns from CDSE's own detection guidance (disproportionate interest, bridging toward a topic, circling back). Each indicator carries a `diagnosticity` weight. The overall score is the diagnosticity of the present indicators divided by the diagnosticity of the whole bank, so marking everything scores 1.0 and marking nothing scores 0.0.

Only the indicators that map to a specific technique feed the four class scores, through `weighted_class_scores`: pattern items and any technique outside the four base classes (composite, or one of the doctrinal-adjacent techniques carrying class `none`) count toward the overall likelihood but not toward a class bucket. When the overall score crosses `reporting_threshold`, the module sets `reporting_flag` and the result carries the list of matched technique ids.

## Knowledge: graded drills

The knowledge module is a competency check, not a self-report. Each item is a scenario graded on three dimensions: recognition (did the taker name the technique), countermeasure (did they pick the taught response), and response (did they pick the reporting channel correct for their context). Each dimension scores 1.0 for the correct choice, 0.5 for a defined partial near-miss, or 0.0 otherwise. The response dimension resolves its correct answer from the item's `report_paths`, keyed by the taker's stated context (dod, federal, cleared_contractor, private_industry) and falling back to `general`.

Per-dimension scores average across all answered items. The overall score is the weighted average of the three dimension scores, using `knowledge_dimension_weights`. Each answered item also produces a technique-class hit (the mean of its three dimension scores) that rolls into the four class scores through `weighted_class_scores`, so a knowledge run yields both a competency profile and a class profile. Every item returns feedback text explaining the correct answer on all three dimensions, because the evidence favors practice with feedback over a one-shot quiz.

## The weight philosophy

Three tiers of confidence sit behind the numbers in `config.py`.

**Reciprocity is evidence-anchored.** Its 1.5 class weight, the heaviest of the four, comes from Van der Kleij et al. (2023, N = 2,426), which found reciprocity, not authority, drove real disclosure of everyday personal information. This is the one weight in the default config backed by a specific effect size rather than expert judgment.

**Prevalence and subtlety are secondary.** A technique's `default_weight` in the taxonomy leans on how often it shows up across the corroborating sources (the FBI brochure, OSAC, NCSC, CDSE, DCSA, and Army FM 34-60) and how hard it is to notice in the moment. The two techniques appearing in only one source, Mirroring and Quote reported facts, carry medium confidence and a lower default weight so a deployment can drop them cleanly without touching the rest of the taxonomy.

**Everything else is a provisional default.** The other three class weights, both tier thresholds, the reporting threshold, and the three knowledge dimension weights are documented expert-judgment starting points, not measured values. `docs/validation-research-proposal.md` describes the study that would replace them with fitted numbers.

## Tiering

`tier_for` in `score/common.py` maps a 0-to-1 score to one of three labels using `config.tier_thresholds`: `high` at or above 0.7, `elevated` at or above 0.4, and `low` below that. The same function tiers all three modules' overall scores, so a tier means the same thing across self-assessment, interaction, and knowledge, even though the score underneath it is built differently in each.
