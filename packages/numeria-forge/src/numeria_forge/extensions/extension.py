from abc import ABC, abstractmethod

from numeria_forge.extensions.context import ExtensionContext


class Extension(ABC):
    """Stable public interface implemented by Forge extensions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique extension name."""

    @abstractmethod
    def register(self, context: ExtensionContext) -> None:
        """Register capabilities with Numeria Forge."""
