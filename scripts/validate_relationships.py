from pathlib import Path
import sys
import yaml

ROOT = Path("knowledge")

ontology = yaml.safe_load(
    Path("knowledge/ontology/relationship-types.yaml").read_text()
) or {}

rules = ontology.get("relationship_types", {})
errors = []
entities = {}

# Load all canonical entities by ID.
for entity_file in ROOT.rglob("entity.yaml"):
    data = yaml.safe_load(entity_file.read_text()) or {}

    entity_id = data.get("id")
    entity_type = data.get("type")

    if entity_id and entity_type and entity_file.parent.parent.name != "relationships":
        entities[entity_id] = {
            "type": entity_type,
            "path": entity_file,
        }

# Validate every relationship.
for rel_file in Path("knowledge/relationships").rglob("entity.yaml"):
    rel = yaml.safe_load(rel_file.read_text()) or {}

    rel_type = rel.get("type")

    if rel_type not in rules:
        errors.append(
            f"{rel_file}: unknown relationship type '{rel_type}'"
        )
        continue

    rule = rules[rel_type]

    source = rel.get("source") or {}
    target = rel.get("target") or {}

    source_id = source.get("id")
    target_id = target.get("id")

    source_type = source.get("type")
    target_type = target.get("type")

    allowed_source = rule.get("source")
    allowed_target = rule.get("target")

    if isinstance(allowed_source, str):
        allowed_source = [allowed_source]

    if isinstance(allowed_target, str):
        allowed_target = [allowed_target]

    if source_type not in allowed_source:
        errors.append(
            f"{rel_file}: invalid source type '{source_type}' "
            f"for {rel_type}; expected one of {allowed_source}"
        )

    if target_type not in allowed_target:
        errors.append(
            f"{rel_file}: invalid target type '{target_type}' "
            f"for {rel_type}; expected one of {allowed_target}"
        )

    if source_id not in entities:
        errors.append(
            f"{rel_file}: source entity '{source_id}' does not exist"
        )
    else:
        actual_source_type = entities[source_id]["type"]

        if source_type != actual_source_type:
            errors.append(
                f"{rel_file}: source '{source_id}' is declared as "
                f"'{source_type}' but actual type is "
                f"'{actual_source_type}'"
            )

    if target_id not in entities:
        errors.append(
            f"{rel_file}: target entity '{target_id}' does not exist"
        )
    else:
        actual_target_type = entities[target_id]["type"]

        if target_type != actual_target_type:
            errors.append(
                f"{rel_file}: target '{target_id}' is declared as "
                f"'{target_type}' but actual type is "
                f"'{actual_target_type}'"
            )

if errors:
    print("\nRelationship ontology validation failed:\n")

    for error in errors:
        print(f"- {error}")

    sys.exit(1)

print(
    f"Relationship ontology validation passed: "
    f"{len(entities)} referenced entities available."
)
