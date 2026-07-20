"""Generation engine for AI-powered content creation."""

from __future__ import annotations

from numeria_forge.ai.prompt import Prompt
from numeria_forge.ai.provider_registry import AIProviderRegistry
from numeria_forge.ai.request import GenerationRequest
from numeria_forge.ai.result import GenerationResult


class GenerationEngine:
    """Coordinate AI content generation using registered providers."""

    def __init__(
        self,
        providers: AIProviderRegistry,
    ) -> None:
        self._providers = providers

    def generate(
        self,
        request: GenerationRequest | None = None,
        *,
        provider: str | None = None,
        prompt: Prompt | None = None,
    ) -> GenerationResult:
        """Generate content from a request or legacy arguments."""

        if request is not None and (
            provider is not None
            or prompt is not None
        ):
            raise ValueError(
                "Specify either 'request' or the legacy "
                "'provider' and 'prompt' arguments, not both."
            )

        if request is None:
            if provider is None or prompt is None:
                raise ValueError(
                    "A GenerationRequest or both 'provider' "
                    "and 'prompt' must be supplied."
                )

            request = GenerationRequest(
                provider=provider,
                prompt=prompt,
            )

        ai_provider = self._providers.get(
            request.provider,
        )

        return ai_provider.generate(
            request.prompt,
        )
