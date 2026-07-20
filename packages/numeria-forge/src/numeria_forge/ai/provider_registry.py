"""Registry for AI generation providers."""

from __future__ import annotations

from numeria_forge.ai.provider import AIProvider


class AIProviderRegistry:
    """Registry of available AI providers."""

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    def register(
        self,
        provider: AIProvider,
    ) -> None:
        if provider.name in self._providers:
            raise ValueError(
                f"Provider '{provider.name}' is already registered."
            )

        self._providers[provider.name] = provider

    def get(
        self,
        name: str,
    ) -> AIProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown AI provider '{name}'."
            ) from exc

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    @property
    def providers(self) -> tuple[AIProvider, ...]:
        return tuple(
            self._providers[name]
            for name in sorted(self._providers)
        )
