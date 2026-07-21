"""Compiler stage contract."""

from typing import Protocol

from numeria_forge.compiler.context import CompilerContext


class CompilerStage(Protocol):
    """Contract implemented by compiler stages."""

    @property
    def name(self) -> str:
        """Return the stable stage name."""

    def run(
        self,
        context: CompilerContext,
    ) -> CompilerContext:
        """Execute the stage."""
