import pytest

from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.extensions import (
    Extension,
    ExtensionContext,
    ExtensionManager,
    ForgeRegistries,
)


class ExampleExtension(Extension):
    @property
    def name(self) -> str:
        return "example"

    def register(
        self,
        context: ExtensionContext,
    ) -> None:
        context.register_artifact(
            ArtifactDefinition(
                name="example_card",
                template="example/CARD.md.j2",
                default_destination="EXAMPLE_CARD.md",
                media_type="text/markdown",
            )
        )


def create_context() -> ExtensionContext:
    return ExtensionContext(
        registries=ForgeRegistries(),
    )


def test_manager_registers_extension() -> None:
    manager = ExtensionManager()

    manager.register(
        ExampleExtension(),
        create_context(),
    )

    assert manager.names == ("example",)
    assert len(manager.extensions) == 1


def test_manager_rejects_duplicate_names() -> None:
    manager = ExtensionManager()

    manager.register(
        ExampleExtension(),
        create_context(),
    )

    with pytest.raises(ValueError):
        manager.register(
            ExampleExtension(),
            create_context(),
        )
