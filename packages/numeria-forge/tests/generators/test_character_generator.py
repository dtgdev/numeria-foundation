from numeria_forge.ai import (
    AIProvider,
    AIProviderRegistry,
    GenerationEngine,
    GenerationResult,
    Prompt,
)
from numeria_forge.generators.character import CharacterGenerator


class FakeProvider(AIProvider):
    @property
    def name(self) -> str:
        return "fake"

    def generate(
        self,
        prompt: Prompt,
    ) -> GenerationResult:
        return GenerationResult(
            content=(
                f"Generated character for {prompt.input_text}"
            ),
            provider=self.name,
            model="fake-model",
        )


def test_character_generator_returns_domain_object() -> None:
    registry = AIProviderRegistry()
    registry.register(FakeProvider())

    generator = CharacterGenerator(
        GenerationEngine(registry),
    )

    character = generator.generate(
        provider="fake",
        concept="Derivative",
    )

    assert character.name == "Derivative"
    assert (
        character.mathematical_concept
        == "Derivative"
    )
    assert "Derivative" in character.description
    assert character.personality == "Unknown"
