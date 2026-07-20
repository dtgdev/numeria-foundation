"""Provider-neutral AI generation interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from numeria_forge.ai.prompt import Prompt
from numeria_forge.ai.result import GenerationResult


class AIProvider(ABC):
    """Base interface implemented by AI generation providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider's stable identifier."""

    @abstractmethod
    def generate(
        self,
        prompt: Prompt,
    ) -> GenerationResult:
        """Generate content from a prompt."""
