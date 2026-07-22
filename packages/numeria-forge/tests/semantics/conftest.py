from __future__ import annotations

from pathlib import Path

from numeria_forge.domain.canon import Canon, CanonEntity


def make_entity(entity_id: str, entity_type: str, path: str, **data) -> CanonEntity:
    return CanonEntity(
        id=entity_id,
        type=entity_type,
        source_path=Path(path),
        data=data,
    )


ONTOLOGY_WITH_ACYCLIC_REQUIRES = """
version: "1.0.0"
status: CANON

relationship_types:
  REQUIRES:
    source: Concept
    target: Concept
    acyclic: true
  FRIEND_OF:
    source: Character
    target: Character
    symmetric: true
""".strip()


def write_ontology(tmp_path: Path, text: str = ONTOLOGY_WITH_ACYCLIC_REQUIRES) -> Path:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    ontology_path = ontology_dir / "relationship-types.yaml"
    ontology_path.write_text(text, encoding="utf-8")
    return ontology_path


def requires_edge(edge_id: str, source_id: str, target_id: str) -> CanonEntity:
    return make_entity(
        edge_id,
        "REQUIRES",
        f"knowledge/relationships/{edge_id}/entity.yaml",
        source={"id": source_id, "type": "Concept"},
        target={"id": target_id, "type": "Concept"},
    )
