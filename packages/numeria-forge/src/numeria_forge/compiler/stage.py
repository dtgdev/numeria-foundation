from __future__ import annotations

from abc import ABC, abstractmethod

from numeria_forge.compiler.context import CompilerContext


class CompilerStage(ABC):
    """Base class for compiler stages."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(
        self,
        context: CompilerContext,
    ) -> None:
        ...