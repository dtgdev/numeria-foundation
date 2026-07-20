"""Character generator."""

from numeria_forge.ai import (
    GenerationEngine,
    GenerationRequest,
)

from numeria_forge.domain import GeneratedCharacter

from numeria_forge.generators.character.prompt_builder import (
    CharacterPromptBuilder,
)


class CharacterGenerator:

    def __init__(
        self,
        engine: GenerationEngine,
    ) -> None:
        self._engine = engine
        self._builder = CharacterPromptBuilder()

    def generate(
        self,
        *,
        provider: str,
        concept: str,
    ) -> GeneratedCharacter:

        prompt = self._builder.build(concept)

        result = self._engine.generate(
            GenerationRequest(
                provider=provider,
                prompt=prompt,
            )
        )

        return GeneratedCharacter(
            name=concept,
            mathematical_concept=concept,
            description=result.content,
            personality="Unknown",
            superpower="Unknown",
            weakness="Unknown",
            catchphrase="Unknown",
        )
