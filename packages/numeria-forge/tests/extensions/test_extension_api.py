from pathlib import Path

from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.extensions import (
    Extension,
    ExtensionContext,
    ForgeRegistries,
)


class ExampleExtension(Extension):
    @property
    def name(self) -> str:
        return "example"

    def register(self, context: ExtensionContext) -> None:
        context.register_artifact(
            ArtifactDefinition(
                name="example_card",
                template="example/CARD.md.j2",
                default_destination="EXAMPLE_CARD.md",
                media_type="text/markdown",
            )
        )

        context.register_template_root(
            Path("/templates/example")
        )


def test_extension_registers_capabilities() -> None:
    context = ExtensionContext(
        registries=ForgeRegistries(),
    )

    ExampleExtension().register(context)

    assert context.registries.templates.roots == (
        Path("/templates/example"),
    )

    definition = context.registries.artifacts.lookup(
        "example_card"
    )

    assert definition.name == "example_card"
