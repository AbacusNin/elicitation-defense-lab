"""Generate tests/fixtures/parity_cases.json from the Python scorers.

Each case is {module, input, expected}. The Python scorers produce `expected`
here; tests/parity/run_js.mjs runs the same `input` through the JavaScript
scorers, and test_parity.py checks the two agree. `expected` carries the full
scorer result (overall_score, tier, class_scores, and whichever of
dimension_scores / matched_techniques / reporting_flag / exposure_score the
module returns), not just overall_score and tier, so the JS class-score path
(weightedClassScores) is checked along with everything else. Inputs are built
to exercise the paths that matter for parity: empty runs, reverse and exposure
self-items, composite and pattern interaction indicators that affect the
overall score but not the class buckets, and every report-path context in the
knowledge check.
"""

import json
from pathlib import Path

from elicitation_defense_lab.config import default_config
from elicitation_defense_lab.score.interaction import load_bank as load_interaction_bank
from elicitation_defense_lab.score.interaction import score_interaction
from elicitation_defense_lab.score.knowledge import load_bank as load_knowledge_bank
from elicitation_defense_lab.score.knowledge import score_knowledge
from elicitation_defense_lab.score.self_assess import load_bank as load_self_bank
from elicitation_defense_lab.score.self_assess import score_self
from elicitation_defense_lab.taxonomy import load_taxonomy

OUT = Path(__file__).resolve().parent / "parity_cases.json"


def slim(result: dict) -> dict:
    """Keep the comparable fields; drop the bulky knowledge feedback text."""
    return {k: v for k, v in result.items() if k != "feedback"}


def all_correct_knowledge(bank: list[dict], context: str) -> dict:
    answers = {}
    for item in bank:
        report = item["report_paths"].get(context, item["report_paths"]["general"])
        answers[item["id"]] = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": item["correct"]["countermeasure"],
            "response": report,
        }
    return answers


def all_partial_knowledge(bank: list[dict]) -> dict:
    answers = {}
    for item in bank:
        answers[item["id"]] = {
            "recognition": item["partial"]["recognition"],
            "countermeasure": item["partial"]["countermeasure"],
            "response": "resp_ignore_it",
        }
    return answers


def mixed_knowledge(bank: list[dict], context: str) -> dict:
    """Correct recognition and response, a wrong countermeasure (neither correct nor partial)."""
    answers = {}
    for item in bank:
        wrong_cm = next(
            c["id"]
            for c in reversed(item["choices"]["countermeasure"])
            if c["id"] != item["correct"]["countermeasure"]
            and c["id"] != item.get("partial", {}).get("countermeasure")
        )
        report = item["report_paths"].get(context, item["report_paths"]["general"])
        answers[item["id"]] = {
            "recognition": item["correct"]["recognition"],
            "countermeasure": wrong_cm,
            "response": report,
        }
    return answers


def build() -> None:
    config = default_config()
    techniques = load_taxonomy()
    self_bank = load_self_bank()
    interaction_bank = load_interaction_bank()
    knowledge_bank = load_knowledge_bank()

    cases = []

    def add_self(answers):
        result = score_self(answers, config, techniques, self_bank)
        cases.append({"module": "self", "input": {"answers": answers}, "expected": slim(result)})

    def add_interaction(present):
        result = score_interaction(present, config, techniques, interaction_bank)
        cases.append(
            {"module": "interaction", "input": {"present": present}, "expected": slim(result)}
        )

    def add_knowledge(answers, context):
        result = score_knowledge(answers, config, techniques, knowledge_bank, context)
        cases.append(
            {
                "module": "knowledge",
                "input": {"answers": answers, "context": context},
                "expected": slim(result),
            }
        )

    # self-assessment
    add_self({})
    add_self({item["id"]: 2 for item in self_bank})
    add_self({item["id"]: 4 for item in self_bank})
    add_self({item["id"]: 0 for item in self_bank})
    add_self(
        {
            "ego_flattery_pull": 4,
            "ego_let_challenge_pass": 0,  # reverse item
            "recip_confide_for_confide": 3,
            "sp_uncomfortable_declining": 1,
            "cc_fill_assumed_gaps": 4,
            "exposure_public_footprint": 4,
            "exposure_travel_network_caution": 1,  # reverse exposure item
            "not_a_real_item": 2,  # unknown id, ignored
        }
    )

    # interaction
    add_interaction([])
    add_interaction([item["id"] for item in interaction_bank])
    add_interaction(["ind_a1_flattery"])
    add_interaction(["ind_a28_scharff"])  # composite class: overall > 0 but class buckets stay 0
    add_interaction(["pattern_topic_bridging", "pattern_question_density"])
    add_interaction(["ind_a1_flattery", "ind_a8_quid_pro_quo", "nope", "pattern_reformulation"])

    # knowledge, across every report-path context and an unknown one
    add_knowledge({}, "general")
    add_knowledge(all_correct_knowledge(knowledge_bank, "general"), "general")
    add_knowledge(all_correct_knowledge(knowledge_bank, "dod"), "dod")
    add_knowledge(all_correct_knowledge(knowledge_bank, "federal"), "federal")
    add_knowledge(all_correct_knowledge(knowledge_bank, "cleared_contractor"), "cleared_contractor")
    add_knowledge(all_partial_knowledge(knowledge_bank), "private_industry")
    add_knowledge(mixed_knowledge(knowledge_bank, "general"), "general")
    add_knowledge(all_correct_knowledge(knowledge_bank, "student"), "student")  # unknown -> general
    add_knowledge(
        {
            item["id"]: {
                "recognition": item["correct"]["recognition"],
                "countermeasure": item["correct"]["countermeasure"],
                "response": item["report_paths"]["general"],
            }
            for item in knowledge_bank[:3]
        },
        "general",
    )

    OUT.write_text(json.dumps(cases, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"wrote {OUT}")
