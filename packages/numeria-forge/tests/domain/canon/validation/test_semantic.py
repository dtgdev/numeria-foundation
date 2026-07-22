from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import CanonSeverity, SemanticValidator

from .conftest import context_for, make_entity


def test_canon_status_passes(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001", "Character", "x/entity.yaml", status="CANON", version="1.0.0"
    )
    empty_canon.entities[entity.id] = entity

    assert SemanticValidator().validate(context_for(empty_canon)).diagnostics == ()


def test_non_canon_status_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001", "Character", "x/entity.yaml", status="draft", version="1.0.0"
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = SemanticValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.ERROR and "status must be 'CANON'" in d.message
        for d in diagnostics
    )


def test_non_semver_version_is_a_warning(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001", "Character", "x/entity.yaml", status="CANON", version="v1"
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = SemanticValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.WARNING
        and "does not look like semantic versioning" in d.message
        for d in diagnostics
    )


def test_missing_prerequisite_is_reported(empty_canon: Canon) -> None:
    relationship = make_entity(
        "NUM-REL-000001",
        "REQUIRES",
        "knowledge/relationships/x/entity.yaml",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000001"},
        target={"id": "NUM-CON-999999"},
    )
    empty_canon.entities[relationship.id] = relationship

    diagnostics = SemanticValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.ERROR
        and d.message == "Missing prerequisite: NUM-CON-999999"
        for d in diagnostics
    )


def test_existing_prerequisite_passes(empty_canon: Canon) -> None:
    target = make_entity(
        "NUM-CON-000002", "Concept", "x/entity.yaml", status="CANON", version="1.0.0"
    )
    relationship = make_entity(
        "NUM-REL-000001",
        "REQUIRES",
        "knowledge/relationships/x/entity.yaml",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000001"},
        target={"id": "NUM-CON-000002"},
    )
    empty_canon.entities[target.id] = target
    empty_canon.entities[relationship.id] = relationship

    diagnostics = SemanticValidator().validate(context_for(empty_canon)).diagnostics

    assert not any("Missing prerequisite" in d.message for d in diagnostics)


def test_non_canon_prerequisite_is_a_warning(empty_canon: Canon) -> None:
    target = make_entity(
        "NUM-CON-000002", "Concept", "x/entity.yaml", status="draft", version="1.0.0"
    )
    relationship = make_entity(
        "NUM-REL-000001",
        "REQUIRES",
        "knowledge/relationships/x/entity.yaml",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000001"},
        target={"id": "NUM-CON-000002"},
    )
    empty_canon.entities[target.id] = target
    empty_canon.entities[relationship.id] = relationship

    diagnostics = SemanticValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.WARNING
        and "exists but is not CANON" in d.message
        for d in diagnostics
    )
