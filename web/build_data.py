"""Copy the taxonomy and item banks into web/data/ and freeze the default config.

The static page and its parity harness both read from web/data/ so the JavaScript
scorers work off the exact same technique weights, tier thresholds, and banks the
Python scorers use. config.json is serialized from default_config() rather than
retyped in JS, so the two implementations cannot drift on the numbers.
"""

import json
from dataclasses import asdict
from pathlib import Path

from elicitation_defense_lab.config import default_config

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY = ROOT / "taxonomy"
OUT = Path(__file__).resolve().parent / "data"

BANKS = ("self_assessment.json", "interaction.json", "knowledge.json")


def build() -> None:
    OUT.mkdir(exist_ok=True)

    (OUT / "techniques.json").write_text(
        (TAXONOMY / "techniques.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    for bank in BANKS:
        (OUT / bank).write_text(
            (TAXONOMY / "banks" / bank).read_text(encoding="utf-8"), encoding="utf-8"
        )

    config = asdict(default_config())
    (OUT / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"wrote data to {OUT}")
