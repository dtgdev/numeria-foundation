
"""Compiler stage abstraction."""

from __future__ import annotations

from abc import ABC

from abc import abstractmethod

from numeria_forge.compiler.context import CompilerContext

class CompilerStage(ABC):

    """A single stage in the compiler pipeline."""

    @property

    @abstractmethod

    def name(self) -> str:

        ...

    @abstractmethod

    def run(

        self,

        context: CompilerContext,

    ) -> None:

        """Execute the stage."""

