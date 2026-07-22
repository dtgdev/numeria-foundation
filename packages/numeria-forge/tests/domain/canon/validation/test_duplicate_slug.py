from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import DuplicateSlugValidator, Severity

from .conftest import context_for, make_entity


def test_unique_slugs_pass(empty_canon: Canon) -> None:
    a = make_entity(
        "NUM-CHR-000001", "Character", "x/entity.yaml", slug="derivative"
    )
    b = make_entity(
        "NUM-CON-000001", "Concept", "y/entity.yaml", slug="derivative"
    )
    empty_canon.entities[a.id] = a
    empty_canon.entities[b.id] = b

    # Same slug is fine across *different* types (e.g. a Concept and the
    # Character that embodies it).
    result = DuplicateSlugValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_duplicate_slug_within_type_fails(empty_canon: Canon) -> None:
    a = make_entity(
        "NUM-CHR-000001", "Character", "x/entity.yaml", slug="derivative"
    )
    b = make_entity(
        "NUM-CHR-000002", "Character", "y/entity.yaml", slug="Derivative"
    )
    empty_canon.entities[a.id] = a
    empty_canon.entities[b.id] = b

    result = DuplicateSlugValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert "duplicate Character slug" in result.diagnostics[0].message


def test_missing_slug_is_skipped(empty_canon: Canon) -> None:
    entity = make_entity("NUM-CHR-000001", "Character", "x/entity.yaml")
    empty_canon.entities[entity.id] = entity

    result = DuplicateSlugValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_relationships_are_not_checked(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
        slug="anything",
    )
    empty_canon.entities[entity.id] = entity

    result = DuplicateSlugValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()
