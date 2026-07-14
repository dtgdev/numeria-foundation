from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from app.models import CanonEntity, CanonGraph, CanonRelationship, CanonSummary


def repository_root() -> Path:
    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "knowledge").is_dir():
            return parent

    raise RuntimeError(
        "Unable to locate repository root containing knowledge/."
    )


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a YAML mapping.")

    return data


def load_canon() -> CanonGraph:
    root = repository_root()
    knowledge_root = root / "knowledge"

    entities: list[CanonEntity] = []
    relationships: list[CanonRelationship] = []

    for path in sorted(knowledge_root.rglob("entity.yaml")):
        data = load_yaml(path)
        entity_id = data.get("id")
        entity_type = data.get("type")

        if not entity_id or not entity_type:
            continue

        relative_path = str(path.relative_to(root))

        if "relationships" in path.parts:
            source = data.get("source") or {}
            target = data.get("target") or {}

            if not isinstance(source, dict) or not isinstance(target, dict):
                continue

            source_id = source.get("id")
            target_id = target.get("id")

            if not source_id or not target_id:
                continue

            relationships.append(
                CanonRelationship(
                    id=str(entity_id),
                    type=str(entity_type),
                    source=str(source_id),
                    target=str(target_id),
                    path=relative_path,
                    data=data,
                )
            )
            continue

        name = data.get("name") or data.get("title") or entity_id

        entities.append(
            CanonEntity(
                id=str(entity_id),
                type=str(entity_type),
                name=str(name),
                path=relative_path,
                data=data,
            )
        )

    summary = CanonSummary(
        entities=len(entities),
        relationships=len(relationships),
        entity_types=dict(
            sorted(Counter(entity.type for entity in entities).items())
        ),
        relationship_types=dict(
            sorted(
                Counter(
                    relationship.type for relationship in relationships
                ).items()
            )
        ),
    )

    return CanonGraph(
        entities=entities,
        relationships=relationships,
        summary=summary,
    )
