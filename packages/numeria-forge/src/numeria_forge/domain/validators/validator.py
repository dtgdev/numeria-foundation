from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    """Stable interface for Forge validators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique validator name."""

    @abstractmethod
    def validate(self, value: Any) -> tuple[str, ...]:
        """Return validation error messages for the supplied value."""
