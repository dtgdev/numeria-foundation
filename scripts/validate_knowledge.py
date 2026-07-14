from pathlib import Path
import sys
import yaml

ROOT = Path("knowledge")

PREFIX_BY_TYPE = {
    "Character": "NUM-CHR-",
    "Artifact": "NUM-ART-",
    "Location": "NUM-LOC-",
    "Organization": "NUM-ORG-",
    "Relationship": "NUM-REL-",
    "Book": "NUM-BOOK-",
    "Event": "NUM-EVT-",
    "Lesson": "NUM-LSN-",
    "Concept": "NUM-CON-",
    "Lesson": "NUM-LESSON-",
    "Assessment": "NUM-ASMT-",
}

errors = []
entity_ids = {}

for path in ROOT.rglob("entity.yaml"):
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        continue

    if not isinstance(data, dict):
        errors.append(f"{path}: root must be a mapping")
        continue

    entity_id = data.get("id")
    entity_type = data.get("type")

    if not entity_id:
        errors.append(f"{path}: missing id")
        continue

    if entity_id in entity_ids:
        errors.append(
            f"{path}: duplicate id {entity_id}; already used by {entity_ids[entity_id]}"
        )
    else:
        entity_ids[entity_id] = path

    if not entity_type:
        errors.append(f"{path}: missing type")
        continue

    expected_prefix = PREFIX_BY_TYPE.get(entity_type)
    if expected_prefix and not entity_id.startswith(expected_prefix):
        errors.append(
            f"{path}: id {entity_id} does not match type {entity_type}"
        )

    if data.get("status") != "CANON":
        errors.append(f"{path}: status must be CANON")

for path in ROOT.rglob("entity.yaml"):
    try:
        data = yaml.safe_load(path.read_text())
    except Exception:
        continue

    if not isinstance(data, dict) or data.get("type") not in {
        "LIVES_AT",
        "GUIDED_BY",
        "FRIEND_OF",
        "CARRIES",
        "CREATED",
        "STORED_AT",
        "MEMBER_OF",
        "PROTECTS",
        "APPEARS_IN",
        "LOCATED_IN",
    }:
        continue

    for side in ("source", "target"):
        ref = data.get(side, {})
        ref_id = ref.get("id") if isinstance(ref, dict) else None

        if not ref_id:
            errors.append(f"{path}: missing {side}.id")
        elif ref_id not in entity_ids:
            errors.append(f"{path}: unknown {side} id {ref_id}")

if errors:
    print("Knowledge validation failed:\n")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Knowledge validation passed: {len(entity_ids)} entities checked.")
