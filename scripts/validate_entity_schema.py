from pathlib import Path
import sys
import yaml

ROOT = Path("knowledge")

REQUIRED_FIELDS = {
    "Character": ["id", "name", "type", "status", "version"],
    "Artifact": ["id", "name", "type", "status", "version"],
    "Location": ["id", "name", "type", "status", "version"],
    "Organization": ["id", "name", "type", "status", "version"],
    "Book": ["id", "title", "type", "status", "version"],
    "Event": ["id", "name", "type", "status", "version"],
    "Concept": ["id", "name", "type", "status", "version"],
    "LearningObjective": [
        "id",
        "name",
        "type",
        "status",
        "version",
        "objective",
        "grade_band",
    ],
    "Scene": ["id", "name", "type", "status", "version"],
    "Lesson": [
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "primary_concept",
        "primary_learning_objective",
    ],
    "Assessment": [
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "assessment_type",
        "learning_objective",
        "success_criteria",
    ],
    "Activity": [
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "activity_type",
        "learning_objective",
        "instructions",
    ],
    "LearningJourney": [
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "steps",
        "primary_concept",
        "primary_learning_objective",
    ],
}

errors = []
checked = 0

for path in ROOT.rglob("entity.yaml"):
    if "relationships" in path.parts:
        continue

    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        continue

    entity_type = data.get("type")

    if entity_type not in REQUIRED_FIELDS:
        continue

    checked += 1

    for field in REQUIRED_FIELDS[entity_type]:
        value = data.get(field)

        if value is None or value == "" or value == []:
            errors.append(
                f"{path}: {entity_type} is missing required field '{field}'"
            )

if errors:
    print("\nEntity schema validation failed:\n")

    for error in errors:
        print(f"- {error}")

    sys.exit(1)

print(f"Entity schema validation passed: {checked} entities checked.")
