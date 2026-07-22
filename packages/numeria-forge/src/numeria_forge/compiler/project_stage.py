"""Project discovery stage."""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage


class ProjectDiscoveryStage(CompilerStage):
    """Ensure the build directory exists."""

    @property
    def name(self) -> str:
        return "project-discovery"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.build_directory is None:
            raise RuntimeError(
                "ProjectDiscoveryStage requires context.build_directory "
                "to be set."
            )

        context.build_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return context
