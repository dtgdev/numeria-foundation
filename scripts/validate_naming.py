from pathlib import Path
import re
import sys

import yaml

ROOT = Path("knowledge")

PREFIXES = {
    "Character": "NUM-CHR",
    "Artifact": "NUM-ART",
    "Location": "NUM-LOC",
    "Organization": "NUM-ORG",
    "Book": "NUM-BOOK",
    "Event": "NUM-EVT",
    "Concept": "NUM-CON",
    "LearningObjective": "NUM-LO",
}

errors = []
names = {}

for path in ROOT.rglob("entity.yaml"):
    if "relationships" in path.parts:
        continue

    data = yaml.safe_load(path.read_text()) or {}

    entity_id = data.get("id")
    entity_type = data.get("type")
    entity_name = data.get("name") or data.get("title")

    if not entity_id or not entity_type:
        continue

    expected_prefix = PREFIXES.get(entity_type)

    if expected_prefix and not re.fullmatch(
        rf"{re.escape(expected_prefix)}-\d{{6}}",
        entity_id,
    ):
        errors.append(
            f"{path}: id '{entity_id}' must match "
            f"'{expected_prefix}-######'"
        )

    directory_name = path.parent.name

    if not directory_name.startswith(entity_id):
        errors.append(
            f"{path}: directory '{directory_name}' must begin with "
            f"entity id '{entity_id}'"
        )

    if entity_name:
        normalized_name = entity_name.strip().casefold()
        key = (entity_type, normalized_name)

        if key in names:
            previous_id, previous_path = names[key]

            if previous_id != entity_id:
                errors.append(
                    f"{path}: duplicate {entity_type} name "
                    f"'{entity_name}' also used by "
                    f"{previous_id} in {previous_path}"
                )
        else:
            names[key] = (entity_id, path)

if errors:
    print("\nNaming validation failed:\n")

    for error in errors:
        print(f"- {error}")

    sys.exit(1)

print(
    f"Naming validation passed: "
    f"{len(names)} canonical entity names checked."
)
