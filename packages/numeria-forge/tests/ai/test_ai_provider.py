import pytest

from numeria_forge.ai import (
    AIProvider,
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


def test_provider_generates_content() -> None:
    provider = FakeProvider()

    result = provider.generate(
        Prompt(
            instructions="Create a Numeria character.",
            input_text="Derivative",
        )
    )

    assert result.content == "Generated: Derivative"
    assert result.provider == "fake"
    assert result.model == "fake-model"


def test_prompt_rejects_empty_instructions() -> None:
    with pytest.raises(
        ValueError,
        match="instructions must not be empty",
    ):
        Prompt(
            instructions="   ",
        )


def test_generation_result_rejects_empty_content() -> None:
    with pytest.raises(
        ValueError,
        match="content must not be empty",
    ):
        GenerationResult(
            content="",
            provider="fake",
            model="fake-model",
        )


def test_generation_result_rejects_empty_provider() -> None:
    with pytest.raises(
        ValueError,
        match="provider must not be empty",
    ):
        GenerationResult(
            content="Generated content",
            provider="",
            model="fake-model",
        )


def test_generation_result_rejects_empty_model() -> None:
    with pytest.raises(
        ValueError,
        match="model must not be empty",
    ):
        GenerationResult(
            content="Generated content",
            provider="fake",
            model="",
        )
