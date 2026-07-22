from pathlib import Path

from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import (
    CanonSeverity,
    RelationshipValidator,
)

from .conftest import context_for, make_entity

ONTOLOGY = """
version: 1.0.0
status: CANON

relationship_types:
  FEATURES_CHARACTER:
    source: Scene
    target: Character
""".strip()


def write_ontology(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        ONTOLOGY, encoding="utf-8"
    )


def test_valid_relationship_passes(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    canon.entities["NUM-SCN-000001"] = make_entity(
        "NUM-SCN-000001", "Scene", "knowledge/scenes/x/entity.yaml"
    )
    canon.entities["NUM-CHR-000001"] = make_entity(
        "NUM-CHR-000001", "Character", "knowledge/characters/x/entity.yaml"
    )
    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
        source={"id": "NUM-SCN-000001", "type": "Scene"},
        target={"id": "NUM-CHR-000001", "type": "Character"},
    )

    assert RelationshipValidator().validate(context_for(canon)).diagnostics == ()


def test_unknown_relationship_type_fails(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "SOME_UNKNOWN_TYPE",
        "knowledge/relationships/x/entity.yaml",
        source={"id": "a", "type": "Scene"},
        target={"id": "b", "type": "Character"},
    )

    diagnostics = RelationshipValidator().validate(context_for(canon)).diagnostics

    assert len(diagnostics) == 1
    assert diagnostics[0].severity is CanonSeverity.ERROR
    assert "unknown relationship type" in diagnostics[0].message


def test_missing_endpoint_fails(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
        source={"id": "NUM-SCN-999999", "type": "Scene"},
        target={"id": "NUM-CHR-999999", "type": "Character"},
    )

    diagnostics = RelationshipValidator().validate(context_for(canon)).diagnostics
    messages = [d.message for d in diagnostics]

    assert any("source entity 'NUM-SCN-999999' does not exist" in m for m in messages)
    assert any("target entity 'NUM-CHR-999999' does not exist" in m for m in messages)
    assert all(d.severity is CanonSeverity.ERROR for d in diagnostics)


def test_missing_ontology_file_reports_one_error(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    diagnostics = RelationshipValidator().validate(context_for(canon)).diagnostics

    assert len(diagnostics) == 1
    assert diagnostics[0].severity is CanonSeverity.ERROR
    assert "ontology file not found" in diagnostics[0].message
