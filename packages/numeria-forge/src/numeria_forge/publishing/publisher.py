"""Base publisher contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from numeria_forge.publishing.context import PublishContext
from numeria_forge.publishing.result import PublishResult


T = TypeVar("T")


class Publisher(ABC, Generic[T]):
    """Publish a domain object into an external representation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique publisher name."""

    @abstractmethod
    def publish(
        self,
        value: T,
        context: PublishContext,
    ) -> PublishResult:
        """Publish a domain object."""
