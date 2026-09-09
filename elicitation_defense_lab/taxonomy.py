"""Technique taxonomy: the Technique record and the loader that validates it.

The taxonomy is the shared vocabulary the config and scorers build on, so the
loader enforces the enums and required fields at load time rather than letting
a bad record surface as a KeyError three modules downstream.
"""

import json
from dataclasses import dataclass, fields
from pathlib import Path

FAMILIES = {"elicitation", "interrogation", "se_vector", "collection_method"}
TECHNIQUE_CLASSES = {
    "ego",
    "reciprocity",
    "social_pressure",
    "cognitive_cue",
    "composite",
    "none",
}

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "taxonomy" / "techniques.json"


@dataclass(frozen=True)
class Technique:
    id: str
    name: str
    family: str
    technique_class: str
    definition: str
    mechanism: str
    recognition_cue: str
    countermeasure: str
    sources: list[str]
    confidence: str
    default_weight: float


REQUIRED_FIELDS = [f.name for f in fields(Technique)]


def load_taxonomy(path: str | None = None) -> list[Technique]:
    """Load and validate technique records from a JSON file.

    Raises ValueError on a missing required field, an unknown family or
    technique_class, or an empty sources list. Does not coerce or guess;
    a record either matches the schema or the load fails.
    """
    file_path = Path(path) if path is not None else DEFAULT_PATH
    records = json.loads(file_path.read_text(encoding="utf-8"))

    techniques = []
    for record in records:
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            raise ValueError(f"record {record.get('id', '?')} missing fields: {missing}")

        if record["family"] not in FAMILIES:
            raise ValueError(f"record {record['id']} has unknown family: {record['family']!r}")

        if record["technique_class"] not in TECHNIQUE_CLASSES:
            raise ValueError(
                f"record {record['id']} has unknown technique_class: "
                f"{record['technique_class']!r}"
            )

        if not record["sources"]:
            raise ValueError(f"record {record['id']} has an empty sources list")

        techniques.append(Technique(**record))

    return techniques
