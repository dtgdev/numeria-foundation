"""Provider-neutral AI generation request models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from numeria_forge.ai.prompt import Prompt


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Describe a single AI generation request."""

    provider: str
    prompt: Prompt
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError(
                "Generation request provider must not be empty."
            )

        if (
            self.temperature is not None
            and not 0.0 <= self.temperature <= 2.0
        ):
            raise ValueError(
                "Generation request temperature must be "
                "between 0.0 and 2.0."
            )

        if (
            self.max_tokens is not None
            and self.max_tokens <= 0
        ):
            raise ValueError(
                "Generation request max_tokens must be "
                "greater than zero."
            )
