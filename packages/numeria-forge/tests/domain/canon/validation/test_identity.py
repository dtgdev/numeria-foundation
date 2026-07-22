from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import (
    IdentityValidator,
    Severity,
)

from .conftest import context_for, make_entity


def test_valid_id_passes(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/NUM-CHR-000001-derivative/entity.yaml",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = IdentityValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_id_not_matching_prefix_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-XXX-000001",
        "Character",
        "knowledge/characters/NUM-XXX-000001-derivative/entity.yaml",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = IdentityValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert "must match 'NUM-CHR-######'" in result.diagnostics[0].message


def test_duplicate_display_name_is_a_warning(empty_canon: Canon) -> None:
    first = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/NUM-CHR-000001-derivative/entity.yaml",
        name="Derivative",
    )
    second = make_entity(
        "NUM-CHR-000002",
        "Character",
        "knowledge/characters/NUM-CHR-000002-derivative/entity.yaml",
        name="derivative",
    )
    empty_canon.entities[first.id] = first
    empty_canon.entities[second.id] = second

    result = IdentityValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.WARNING
    assert "duplicate Character name" in result.diagnostics[0].message


def test_relationship_uses_relationship_prefix(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/NUM-REL-000001-a-features-b/entity.yaml",
    )
    empty_canon.entities[entity.id] = entity

    result = IdentityValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_realm_type_is_recognized(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-RLM-000001",
        "Realm",
        "knowledge/realms/NUM-RLM-000001-change/entity.yaml",
        name="Change",
        slug="change",
    )
    empty_canon.entities[entity.id] = entity

    result = IdentityValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()
