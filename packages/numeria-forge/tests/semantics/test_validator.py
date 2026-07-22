from pathlib import Path

from numeria_forge.diagnostics import Severity
from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import ValidationContext
from numeria_forge.semantics import DependencyGraphValidator

from .conftest import make_entity, requires_edge, write_ontology


def concept(entity_id: str):
    return make_entity(
        entity_id, "Concept", f"knowledge/concepts/{entity_id}/entity.yaml"
    )


def test_clean_dependency_graph_passes(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_cycle_is_reported_as_an_error(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    canon.entities["NUM-REL-000002"] = requires_edge(
        "NUM-REL-000002", "NUM-CON-000002", "NUM-CON-000001"
    )

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))

    assert result.success is False
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.severity is Severity.ERROR
    assert diagnostic.code == "canon.semantics.dependency-cycle"
    assert "NUM-CON-000001" in diagnostic.message
    assert "NUM-CON-000002" in diagnostic.message


def test_non_acyclic_relationship_types_are_not_checked(tmp_path: Path) -> None:
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    # FRIEND_OF is declared but not marked acyclic in the shared fixture
    # ontology -- a cycle here must not be reported.
    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "FRIEND_OF",
        "knowledge/relationships/a/entity.yaml",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000002", "type": "Concept"},
    )
    canon.entities["NUM-REL-000002"] = make_entity(
        "NUM-REL-000002",
        "FRIEND_OF",
        "knowledge/relationships/b/entity.yaml",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_missing_ontology_file_is_silently_skipped(tmp_path: Path) -> None:
    # No ontology file written at all -- RelationshipValidator (v0.14.0)
    # is responsible for surfacing that; this validator should not add
    # a second, duplicate diagnostic for the same root cause.
    canon = Canon(root=tmp_path)
    canon.entities["NUM-CON-000001"] = concept("NUM-CON-000001")

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()
