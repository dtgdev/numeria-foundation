from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import (
    CanonSeverity,
    EntitySchemaValidator,
)

from .conftest import context_for, make_entity


def test_all_required_fields_present_passes(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "x/entity.yaml",
        id="NUM-CHR-000001",
        name="Derivative",
        type="Character",
        status="CANON",
        version="1.0.0",
    )
    empty_canon.entities[entity.id] = entity

    assert EntitySchemaValidator().validate(context_for(empty_canon)).diagnostics == ()


def test_missing_required_field_fails(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-CHR-000001",
        "Character",
        "x/entity.yaml",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        # name intentionally omitted
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = EntitySchemaValidator().validate(context_for(empty_canon)).diagnostics

    assert len(diagnostics) == 1
    assert diagnostics[0].severity is CanonSeverity.ERROR
    assert "missing required field 'name'" in diagnostics[0].message


def test_unmodeled_type_falls_back_to_baseline_fields(empty_canon: Canon) -> None:
    # As of v0.14, types with no entry in REQUIRED_FIELDS_BY_TYPE are no
    # longer skipped -- they're checked against the baseline
    # (id, type, status, version).
    entity = make_entity(
        "NUM-XYZ-000001",
        "SomethingUnmodeled",
        "x/entity.yaml",
        id="NUM-XYZ-000001",
        type="SomethingUnmodeled",
        # status/version intentionally omitted
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = EntitySchemaValidator().validate(context_for(empty_canon)).diagnostics
    missing_fields = {
        d.message.split("'")[1] for d in diagnostics
    }

    assert "status" in missing_fields
    assert "version" in missing_fields


def test_realm_requires_slug_from_day_one(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-RLM-000001",
        "Realm",
        "x/entity.yaml",
        id="NUM-RLM-000001",
        type="Realm",
        status="CANON",
        version="1.0.0",
        name="Change",
        # slug intentionally omitted
    )
    empty_canon.entities[entity.id] = entity

    diagnostics = EntitySchemaValidator().validate(context_for(empty_canon)).diagnostics

    assert any("missing required field 'slug'" in d.message for d in diagnostics)


def test_relationship_entities_are_not_checked(empty_canon: Canon) -> None:
    entity = make_entity(
        "NUM-REL-000001",
        "FEATURES_CHARACTER",
        "knowledge/relationships/x/entity.yaml",
    )
    empty_canon.entities[entity.id] = entity

    assert EntitySchemaValidator().validate(context_for(empty_canon)).diagnostics == ()
