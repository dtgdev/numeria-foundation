from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import CanonLawValidator, Severity

from .conftest import context_for, make_entity


def test_exact_slug_directory_match_passes(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/NUM-CHR-000001-derivative/entity.yaml",
        name="Derivative",
        slug="derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = CanonLawValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_slug_present_but_directory_wrong_fails(empty_canon: Canon) -> None:
    # Canon Law #1: once a slug exists, the directory must match
    # <id>-<slug> exactly -- "starts with the id" is no longer enough.
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/NUM-CHR-000001-extra-suffix/entity.yaml",
        name="Derivative",
        slug="derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = CanonLawValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert (
        "must be named exactly 'NUM-CHR-000001-derivative'"
        in result.diagnostics[0].message
    )


def test_no_slug_falls_back_to_starts_with_check(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/NUM-CHR-000001-anything-else/entity.yaml",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = CanonLawValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_directory_not_starting_with_id_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "knowledge/characters/derivative/entity.yaml",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = CanonLawValidator().validate(context_for(empty_canon))

    assert any(
        d.severity is Severity.ERROR and "must begin with entity id" in d.message
        for d in result.diagnostics
    )


def test_realm_requires_exact_slug_match(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-RLM-000001",
        "Realm",
        "knowledge/realms/NUM-RLM-000001-change/entity.yaml",
        name="Change",
        slug="change",
    )
    empty_canon.entities[entity.id] = entity

    result = CanonLawValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()
