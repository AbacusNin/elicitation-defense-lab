# Validation research proposal

This describes how `elicitation-defense-lab` could become a validated instrument. It is a proposal, not a result. Nothing in this document has been run. `docs/limitations.md` states the current, unvalidated posture; this is the path away from it.

## Hypothesis

The self-assessment module's susceptibility score predicts real disclosure behavior. A person who scores higher on the self-assessment, particularly on the reciprocity and cognitive-cue class subscores, discloses more sensitive information when actually exposed to a matched elicitation attempt than a person who scores lower.

A secondary hypothesis: performance on the knowledge module's recognition and countermeasure dimensions predicts the same behavioral outcome independently of the self-assessment score, since stated attitude and demonstrated competency are not the same construct.

## Method

**Sample.** A cohort large enough to power a correlation and a reliability analysis, drawn from a population with plausible elicitation exposure (a security-cleared or corporate population, or a general population if the study is run as an awareness-training pilot rather than a targeted assessment). Sample size depends on the expected effect size; Van der Kleij et al. (2023) worked with N = 2,426 for a comparable reciprocity effect, which is a reasonable reference point for powering this study rather than a target to match exactly.

**Administer the instrument.** Participants complete the self-assessment and knowledge modules. Timestamped, versioned responses are recorded against the instrument version in `schema.py` (`instrument_version`), so a later re-analysis can tell which version of the item bank produced which scores.

**Internal reliability.** Compute Cronbach's alpha (or an equivalent internal-consistency measure) per technique class subscore and for the exposure score. A class with items that do not cohere statistically is a signal that the class needs revision, regardless of how well-cited its individual items are.

**Construct validity.** Correlate the self-assessment's class subscores against the reference instruments it draws structure from: HAIS-Q and SeBIS, administered alongside it to the same sample. Convergent validity would show the reciprocity and cognitive-cue subscores correlating with the phishing-susceptibility constructs those instruments measure, since both are downstream of the same underlying influence mechanisms even though the channel differs.

**Behavioral criterion.** The hypothesis needs a real outcome, something beyond another questionnaire. A simulated elicitation exercise, run separately from and after the self-assessment (so scoring the assessment cannot bias performance in the exercise), gives a disclosure-behavior outcome: how much sensitive information a trained confederate using a scripted, IRB-approved elicitation scenario is able to draw out of each participant. The self-assessment's overall score and class subscores are then correlated against that behavioral outcome. This is the step that would let the tool claim predictive validity rather than face validity.

**Knowledge module analysis.** Separately, correlate knowledge-module recognition and countermeasure scores against the same behavioral criterion, testing whether demonstrated competency predicts resistance independently of self-reported attitude.

## Consent and privacy

Every element of this design requires informed consent, IRB or equivalent ethics review before any data collection, and a data handling plan that treats participant responses as sensitive research data, not product telemetry. Specific requirements:

- Participants consent separately to the self-assessment, the knowledge module, and the simulated elicitation exercise, since the third involves being intentionally deceived within a controlled and later fully debriefed protocol.
- The simulated elicitation exercise requires ethics review beyond a standard survey, given the deception involved; it follows the same disclosure and debriefing norms as published research using confederate-run social engineering scenarios.
- Response data is anonymized or pseudonymized at collection, separate from any identity that would let a result be tied back to a specific person's employment record or security clearance.
- No participant's individual score is shared with their employer or chain of command as part of the study. Aggregate findings are what get published or used to revise the instrument.
- Data retention and deletion follow whatever ethics board approves the protocol, not this repository's own defaults.

## The option to seed from consented page data

The static page (`web/index.html`) runs entirely client-side today and transmits nothing; see `docs/limitations.md`. A future version of the page could offer an explicit, separate opt-in for a taker to contribute their anonymized responses to this validation research. That is a real option worth keeping open, since it would give the study a much larger and more naturally recruited sample than a standalone research cohort. It is not part of phase 1. Building it would mean adding a backend, a consent flow distinct from the page's current no-transmission default, and a privacy design reviewed on its own terms before any data collection starts. Nothing in the current build collects, stores, or transmits page responses anywhere.
