from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import (
    CanonRulesValidator,
    CanonSeverity,
)

from .conftest import context_for, make_entity


def test_missing_version_fails(empty_canon: Canon) -> None:
    entity = make_entity("NUM-CHR-000001", "Character", "x/entity.yaml")
    empty_canon.entities[entity.id] = entity

    diagnostics = CanonRulesValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.ERROR and "missing version" in d.message
        for d in diagnostics
    )


def test_character_needs_role_or_domain(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "x/entity.yaml",
        version="1.0.0",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = CanonRulesValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.ERROR
        and "needs role or mathematical_domain" in d.message
        for d in diagnostics
    )


def test_artifact_missing_purpose_is_a_warning(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-ART-000001", "Artifact", "x/entity.yaml", version="1.0.0"
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = CanonRulesValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.WARNING
        and "needs purpose, abilities" in d.message
        for d in diagnostics
    )


def test_self_relationship_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FRIEND_OF",
        "knowledge/relationships/x/entity.yaml",
        version="1.0.0",
        source={"id": "NUM-CHR-000001"},
        target={"id": "NUM-CHR-000001"},
        relationship_properties={"bidirectional": True},
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = CanonRulesValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.ERROR and "cannot connect" in d.message
        for d in diagnostics
    )


def test_friend_of_not_bidirectional_is_a_warning(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FRIEND_OF",
        "knowledge/relationships/x/entity.yaml",
        version="1.0.0",
        source={"id": "NUM-CHR-000001"},
        target={"id": "NUM-CHR-000002"},
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = CanonRulesValidator().validate(context_for(empty_canon)).diagnostics

    assert any(
        d.severity is CanonSeverity.WARNING
        and "must set relationship_properties.bidirectional" in d.message
        for d in diagnostics
    )
