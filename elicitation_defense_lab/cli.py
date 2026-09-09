"""Command-line entry point: run a scoring module and emit its event.

Ties the three scorers to the event schema. Each module has its own answer
shape (self and knowledge take an id-keyed object, interaction takes a list
of present ids), so this module's job is picking the right loader and scorer
for --module and mapping its result onto build_event's kwargs.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from elicitation_defense_lab.config import default_config, load_config
from elicitation_defense_lab.schema import build_event
from elicitation_defense_lab.score.interaction import load_bank as load_interaction_bank
from elicitation_defense_lab.score.interaction import score_interaction
from elicitation_defense_lab.score.knowledge import load_bank as load_knowledge_bank
from elicitation_defense_lab.score.knowledge import score_knowledge
from elicitation_defense_lab.score.self_assess import load_bank as load_self_bank
from elicitation_defense_lab.score.self_assess import score_self
from elicitation_defense_lab.taxonomy import load_taxonomy


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="elicitation-defense-lab")
    parser.add_argument("module", choices=["self", "interaction", "knowledge"])
    parser.add_argument("--answers", required=True)
    parser.add_argument("--config")
    parser.add_argument("--context", default="general")
    parser.add_argument("--out")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    config = load_config(args.config) if args.config else default_config()
    techniques = load_taxonomy()
    raw_answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))

    if args.module == "self":
        bank = load_self_bank()
        result = score_self(raw_answers, config, techniques, bank)
    elif args.module == "interaction":
        present = list(raw_answers) if isinstance(raw_answers, dict) else raw_answers
        bank = load_interaction_bank()
        result = score_interaction(present, config, techniques, bank)
    else:
        bank = load_knowledge_bank()
        result = score_knowledge(raw_answers, config, techniques, bank, args.context)

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    event = build_event(
        args.module,
        tier=result["tier"],
        overall_score=result["overall_score"],
        class_scores=result["class_scores"],
        timestamp=timestamp,
        context=args.context,
        dimension_scores=result.get("dimension_scores"),
        matched_techniques=result.get("matched_techniques"),
        reporting_flag=result.get("reporting_flag"),
    )

    output = json.dumps(event, indent=2)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0
