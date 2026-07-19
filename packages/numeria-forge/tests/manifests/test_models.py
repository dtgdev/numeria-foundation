import pytest

from numeria_forge.domain.manifests import (
    EntityDefinition,
    Manifest,
    OutputDefinition,
)


def make_entity() -> EntityDefinition:
    return EntityDefinition(
        type="concept",
        id="numeria:concept:derivative",
        slug="derivative",
        title="Derivative",
    )


def test_manifest_contains_entity_and_outputs() -> None:
    output = OutputDefinition(
        template="concept/README.md.j2",
        destination="README.md",
    )

    manifest = Manifest(
        schema_version="1.0",
        entity=make_entity(),
        outputs=(output,),
    )

    assert manifest.schema_version == "1.0"
    assert manifest.entity.slug == "derivative"
    assert manifest.outputs[0].destination == "README.md"
    assert manifest.outputs[0].required is True


def test_entity_id_must_match_type_and_slug() -> None:
    with pytest.raises(
        ValueError,
        match="must match the entity type and slug",
    ):
        EntityDefinition(
            type="concept",
            id="numeria:concept:integral",
            slug="derivative",
            title="Derivative",
        )


def test_output_destination_cannot_escape_package() -> None:
    with pytest.raises(
        ValueError,
        match="must remain inside the package",
    ):
        OutputDefinition(
            template="concept/README.md.j2",
            destination="../README.md",
        )


def test_manifest_rejects_duplicate_destinations() -> None:
    first = OutputDefinition(
        template="concept/README.md.j2",
        destination="README.md",
    )

    second = OutputDefinition(
        template="concept/summary.md.j2",
        destination="README.md",
    )

    with pytest.raises(
        ValueError,
        match="destinations must be unique",
    ):
        Manifest(
            schema_version="1.0",
            entity=make_entity(),
            outputs=(first, second),
        )
