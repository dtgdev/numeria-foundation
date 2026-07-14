from pathlib import Path
import sys
import yaml

ROOT = Path("knowledge")
errors = []

entities = {}

for path in ROOT.rglob("entity.yaml"):
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        continue

    entity_id = data.get("id")
    if entity_id:
        entities[entity_id] = (path, data)

# Rule 1: Every canonical entity must have a version.
for entity_id, (path, data) in entities.items():
    if not data.get("version"):
        errors.append(f"{path}: canonical entity {entity_id} is missing version")

# Rule 2: Every Character must have a name and mathematical role/domain.
for entity_id, (path, data) in entities.items():
    if data.get("type") != "Character":
        continue

    if not data.get("name"):
        errors.append(f"{path}: Character {entity_id} is missing name")

    if not data.get("role") and not data.get("mathematical_domain"):
        errors.append(
            f"{path}: Character {entity_id} needs role or mathematical_domain"
        )

# Rule 3: Every Artifact must define purpose, abilities, or educational meaning.
for entity_id, (path, data) in entities.items():
    if data.get("type") != "Artifact":
        continue

    if not any(
        data.get(field)
        for field in ("purpose", "abilities", "educational_meaning")
    ):
        errors.append(
            f"{path}: Artifact {entity_id} needs purpose, abilities, "
            "or educational_meaning"
        )

# Rule 4: Every Book must reference at least one educational concept.
for entity_id, (path, data) in entities.items():
    if data.get("type") != "Book":
        continue

    concepts = (
        data.get("educational_concepts")
        or data.get("educational_focus")
        or []
    )

    if not concepts:
        errors.append(
            f"{path}: Book {entity_id} must define educational concepts"
        )

# Rule 5: Relationship source and target cannot be identical.
for path in Path("knowledge/relationships").rglob("entity.yaml"):
    data = yaml.safe_load(path.read_text()) or {}

    source_id = (data.get("source") or {}).get("id")
    target_id = (data.get("target") or {}).get("id")

    if source_id and source_id == target_id:
        errors.append(
            f"{path}: relationship cannot connect {source_id} to itself"
        )

# Rule 6: FRIEND_OF relationships must be bidirectional.
for path in Path("knowledge/relationships").rglob("entity.yaml"):
    data = yaml.safe_load(path.read_text()) or {}

    if data.get("type") != "FRIEND_OF":
        continue

    properties = data.get("relationship_properties") or {}

    if properties.get("bidirectional") is not True:
        errors.append(
            f"{path}: FRIEND_OF must set "
            "relationship_properties.bidirectional to true"
        )

if errors:
    print("\nCanon business-rule validation failed:\n")

    for error in errors:
        print(f"- {error}")

    sys.exit(1)

print("Canon business-rule validation passed.")
