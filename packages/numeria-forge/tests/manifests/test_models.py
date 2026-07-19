import pytest

from numeria_forge.domain.manifests.models import (
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


def test_output_definition_contains_template_and_destination() -> None:
    output = OutputDefinition(
        template="concept/README.md.j2",
        destination="README.md",
    )

    assert output.template == "concept/README.md.j2"
    assert output.artifact is None
    assert output.destination == "README.md"


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


def test_output_rejects_empty_template() -> None:
    with pytest.raises(ValueError, match="template cannot be empty"):
        OutputDefinition(
            template="",
            destination="README.md",
        )


def test_output_rejects_empty_destination() -> None:
    with pytest.raises(ValueError, match="destination cannot be empty"):
        OutputDefinition(
            template="concept/README.md.j2",
            destination="",
        )


def test_output_rejects_absolute_destination() -> None:
    with pytest.raises(
        ValueError,
        match="must remain inside the package",
    ):
        OutputDefinition(
            template="concept/README.md.j2",
            destination="/README.md",
        )


def test_output_rejects_parent_directory_destination() -> None:
    with pytest.raises(
        ValueError,
        match="must remain inside the package",
    ):
        OutputDefinition(
            template="concept/README.md.j2",
            destination="../README.md",
        )


def test_entity_rejects_empty_fields() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        EntityDefinition(
            type="concept",
            id="numeria:concept:derivative",
            slug="",
            title="Derivative",
        )


def test_entity_id_must_match_type_and_slug() -> None:
    with pytest.raises(
        ValueError,
        match="must match the entity type and slug",
    ):
        EntityDefinition(
            type="concept",
            id="numeria:concept:limit",
            slug="derivative",
            title="Derivative",
        )


def test_manifest_rejects_empty_schema_version() -> None:
    with pytest.raises(
        ValueError,
        match="schema version cannot be empty",
    ):
        Manifest(
            schema_version="",
            entity=make_entity(),
        )


def test_manifest_rejects_duplicate_destinations() -> None:
    first = OutputDefinition(
        template="concept/README.md.j2",
        destination="README.md",
    )

    second = OutputDefinition(
        template="concept/lesson.md.j2",
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


def test_output_accepts_artifact_without_destination() -> None:
    output = OutputDefinition(
        artifact="readme",
    )

    manifest = Manifest(
        schema_version="1.0",
        entity=make_entity(),
        outputs=(output,),
    )

    assert manifest.outputs[0].artifact == "readme"
    assert manifest.outputs[0].template is None
    assert manifest.outputs[0].destination is None


def test_output_rejects_template_and_artifact_together() -> None:
    with pytest.raises(ValueError, match="Exactly one"):
        OutputDefinition(
            template="concept/README.md.j2",
            artifact="readme",
            destination="README.md",
        )


def test_output_requires_template_or_artifact() -> None:
    with pytest.raises(ValueError, match="Exactly one"):
        OutputDefinition(
            destination="README.md",
        )


def test_output_rejects_empty_artifact_name() -> None:
    with pytest.raises(ValueError, match="Artifact name cannot be empty"):
        OutputDefinition(
            artifact="",
        )