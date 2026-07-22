from pathlib import Path

from numeria_forge.diagnostics import Severity
from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import ValidationContext
from numeria_forge.semantics import OrphanedEntityValidator

from .conftest import make_entity, requires_edge


def concept(entity_id: str):
    return make_entity(
        entity_id, "Concept", f"knowledge/concepts/{entity_id}/entity.yaml"
    )


def test_passes_when_every_entity_has_a_relationship(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )

    result = OrphanedEntityValidator().validate(ValidationContext(canon=canon))

    assert result.diagnostics == ()


def test_reports_a_warning_per_orphaned_entity(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    # NUM-CON-000003 has no relationship at all.

    result = OrphanedEntityValidator().validate(ValidationContext(canon=canon))

    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.severity is Severity.WARNING
    assert diagnostic.code == "canon.semantics.orphaned-entity"
    assert "NUM-CON-000003" in diagnostic.message
    # Orphaned is a WARNING, not an ERROR -- it must not fail validation.
    assert result.success


def test_an_empty_canon_reports_nothing(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    result = OrphanedEntityValidator().validate(ValidationContext(canon=canon))

    assert result.diagnostics == ()
