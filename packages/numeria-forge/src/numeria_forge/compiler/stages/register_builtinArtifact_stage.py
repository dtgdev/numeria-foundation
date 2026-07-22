from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.domain.artifacts import create_builtin_registry


class RegisterBuiltinArtifactsStage(CompilerStage):
    """Register the built-in artifact definitions."""

    @property
    def name(self) -> str:
        return "register-builtin-artifacts"

    def execute(self, context: CompilerContext) -> CompilerContext:
        context.artifact_registry = create_builtin_registry()
        return context
