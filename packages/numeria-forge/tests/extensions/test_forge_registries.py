from pathlib import Path

from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.extensions import ForgeRegistries


def test_forge_registries_create_default_registries() -> None:
    registries = ForgeRegistries()

    assert registries.templates.roots == ()

    registries.artifacts.register(
        ArtifactDefinition(
            name="custom_card",
            template="custom/CARD.md.j2",
            default_destination="CUSTOM_CARD.md",
            media_type="text/markdown",
        )
    )

    definition = registries.artifacts.lookup(
        "custom_card"
    )

    assert definition.name == "custom_card"


def test_forge_registries_instances_are_isolated() -> None:
    first = ForgeRegistries()
    second = ForgeRegistries()

    first.templates.register(
        Path("templates/first")
    )

    assert first.templates.roots == (
        Path("templates/first"),
    )
    assert second.templates.roots == ()
