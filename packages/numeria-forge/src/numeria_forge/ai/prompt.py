"""Prompt models used by AI generation providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Prompt:
    """A provider-neutral AI generation prompt."""

    instructions: str
    input_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.instructions.strip():
            raise ValueError(
                "Prompt instructions must not be empty."
            )
