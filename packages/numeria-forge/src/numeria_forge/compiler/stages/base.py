from typing import Protocol

from numeria_forge.compiler.context import CompilerContext


class PipelineStage(Protocol):
    """A single compiler pipeline stage."""

    def run(self, context: CompilerContext) -> CompilerContext:
        ...