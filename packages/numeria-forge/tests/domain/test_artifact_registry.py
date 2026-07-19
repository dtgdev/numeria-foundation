from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.domain.artifacts.registry import ArtifactRegistry

import pytest


def test_register_definition() -> None:
    registry = ArtifactRegistry()

    definition = ArtifactDefinition(
        name="readme",
        template="concept/README.md.j2",
        media_type="text/markdown",
        default_destination="README.md",
    )

    registry.register(definition)

    assert registry.lookup("readme") is definition


def test_duplicate_registration_raises() -> None:
    registry = ArtifactRegistry()

    definition = ArtifactDefinition(
        name="readme",
        template="concept/README.md.j2",
        media_type="text/markdown",
        default_destination="README.md",
    )

    registry.register(definition)

    with pytest.raises(ValueError):
        registry.register(definition)


def test_unknown_artifact_raises() -> None:
    registry = ArtifactRegistry()

    with pytest.raises(KeyError):
        registry.lookup("does-not-exist")