from numeria_forge.ai import (
    AIProvider,
    AIProviderRegistry,
    GenerationEngine,
    GenerationResult,
    Prompt,
)


class FakeProvider(AIProvider):
    @property
    def name(self) -> str:
        return "fake"

    def generate(
        self,
        prompt: Prompt,
    ) -> GenerationResult:
        return GenerationResult(
            content=f"Generated: {prompt.input_text}",
            provider=self.name,
            model="fake-model",
        )


def test_generation_engine_uses_registered_provider() -> None:
    registry = AIProviderRegistry()
    registry.register(FakeProvider())

    engine = GenerationEngine(registry)

    result = engine.generate(
        provider="fake",
        prompt=Prompt(
            instructions="Generate a character.",
            input_text="Derivative",
        ),
    )

    assert result.provider == "fake"
    assert result.model == "fake-model"
    assert result.content == "Generated: Derivative"
