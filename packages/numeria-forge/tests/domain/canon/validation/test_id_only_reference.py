from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import (
    IdOnlyReferenceValidator,
    Severity,
)

from .conftest import context_for, make_entity


def test_id_reference_passes(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
        source={"id": "NUM-SCN-000001", "type": "Scene"},
        target={"id": "NUM-CHR-000001", "type": "Character"},
    )
    empty_canon.entities[entity.id] = entity

    result = IdOnlyReferenceValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_path_reference_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
        source={"id": "NUM-SCN-000001", "type": "Scene"},
        target={
            "id": "knowledge/characters/NUM-CHR-000001-derivative",
            "type": "Character",
        },
    )
    empty_canon.entities[entity.id] = entity

    result = IdOnlyReferenceValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert "Canon Law #3" in result.diagnostics[0].message
    assert "target" in result.diagnostics[0].message


def test_own_top_level_id_is_not_flagged_as_a_reference(empty_canon: Canon) -> None:
    # An entity's own id/type at the root is its identity, not a
    # reference to something else -- must not be flagged.
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "x/entity.yaml",
        id="NUM-CHR-000001",
        type="Character",
        name="Derivative",
    )
    empty_canon.entities[entity.id] = entity

    result = IdOnlyReferenceValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_source_documents_paths_are_not_flagged(empty_canon: Canon) -> None:
    # source_documents legitimately holds paths to supporting docs, not
    # references to other canonical entities -- must not be flagged.
    entity = make_entity(
        "NUM-WLD-000001",
        "World",
        "knowledge/world/NUM-WLD-000001-world/entity.yaml",
        source_documents=[
            "knowledge/world/NUM-WLD-000001-world/WORLD_ATLAS.md",
        ],
    )
    empty_canon.entities[entity.id] = entity

    result = IdOnlyReferenceValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()
