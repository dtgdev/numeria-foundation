from pathlib import Path
import yaml
import sys

ontology = yaml.safe_load(
    Path("knowledge/ontology/relationship-types.yaml").read_text()
)

rules = ontology["relationship_types"]

errors = []

for rel_file in Path("knowledge/relationships").rglob("entity.yaml"):

    rel = yaml.safe_load(rel_file.read_text())

    rel_type = rel["type"]

    if rel_type not in rules:
        errors.append(f"{rel_file}: unknown relationship type '{rel_type}'")
        continue

    rule = rules[rel_type]

    source = rel["source"]["type"]
    target = rel["target"]["type"]

    allowed_source = rule["source"]

    if isinstance(allowed_source, str):
        allowed_source = [allowed_source]

    if source not in allowed_source:
        errors.append(
            f"{rel_file}: invalid source type '{source}' for {rel_type}"
        )

    if target != rule["target"]:
        errors.append(
            f"{rel_file}: invalid target type '{target}' for {rel_type}"
        )

if errors:

    print("\nRelationship validation failed:\n")

    for e in errors:
        print("-", e)

    sys.exit(1)

print("Relationship ontology validation passed.")
