"""Project discovery stage."""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage


class ProjectDiscoveryStage(CompilerStage):
    """Ensure the build directory exists."""

    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:

        context.build_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return context
