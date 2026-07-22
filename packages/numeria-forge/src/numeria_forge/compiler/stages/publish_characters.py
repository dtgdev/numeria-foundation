"""Publish canonical character assets."""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.publishing import (
    CharacterYamlPublisher,
    PublishContext,
)


class PublishCharactersStage(
    CompilerStage,
):
    """Publish every canonical character."""

    def __init__(self) -> None:
        self._publisher = CharacterYamlPublisher()

    @property
    def name(self) -> str:
        return "publish-characters"

    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:

        publish_context = PublishContext(
            output_directory=context.output_directory,
            metadata=context.metadata,
        )

        for character in context.characters:

            result = self._publisher.publish(
                character,
                publish_context,
            )

            context.published_assets.append(result)

        return context
