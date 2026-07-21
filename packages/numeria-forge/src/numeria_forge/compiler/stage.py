"""Compiler stage interface."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from numeria_forge.compiler.context import CompilerContext


class CompilerStage(ABC):
    """Base class for all compiler stages."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stage name."""

    @abstractmethod
    def execute(

            self,

            context: CompilerContext,

    ) -> CompilerContext:
        ...
