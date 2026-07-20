"""AI generation result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Provider-neutral result returned by an AI provider."""

    content: str
    provider: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError(
                "Generation result content must not be empty."
            )

        if not self.provider.strip():
            raise ValueError(
                "Generation result provider must not be empty."
            )

        if not self.model.strip():
            raise ValueError(
                "Generation result model must not be empty."
            )
