import pytest

from numeria_forge.ai import (
    AIProvider,
    AIProviderRegistry,
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
            content="ok",
            provider=self.name,
            model="fake",
        )


def test_register_provider() -> None:
    registry = AIProviderRegistry()

    registry.register(FakeProvider())

    assert registry.names == ("fake",)


def test_duplicate_provider() -> None:
    registry = AIProviderRegistry()

    registry.register(FakeProvider())

    with pytest.raises(ValueError):
        registry.register(FakeProvider())


def test_get_provider() -> None:
    registry = AIProviderRegistry()

    registry.register(FakeProvider())

    assert registry.get("fake").name == "fake"


def test_unknown_provider() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")
