from numeria_forge.domain.artifacts import (
    ArtifactDefinition,
    create_builtin_registry,
)
from numeria_forge.extensions import Extension, ExtensionContext


class ExampleExtension(Extension):
    @property
    def name(self) -> str:
        return "example"

    def register(self, context: ExtensionContext) -> None:
        context.artifact_registry.register(
            ArtifactDefinition(
                name="example_card",
                template="example/CARD.md.j2",
                default_destination="EXAMPLE_CARD.md",
                media_type="text/markdown",
            )
        )


def test_extension_exposes_name() -> None:
    extension = ExampleExtension()

    assert extension.name == "example"


def test_extension_registers_capabilities() -> None:
    registry = create_builtin_registry()

    context = ExtensionContext(
        artifact_registry=registry,
    )

    ExampleExtension().register(context)

    definition = registry.lookup("example_card")

    assert definition.name == "example_card"
    assert definition.template == "example/CARD.md.j2"
    assert definition.default_destination == "EXAMPLE_CARD.md"
    assert definition.media_type == "text/markdown"
