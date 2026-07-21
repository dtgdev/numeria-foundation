from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import PipelineStage
from numeria_forge.domain.artifacts import create_builtin_registry


class RegisterBuiltinArtifactsStage(PipelineStage):
    """Register the built-in artifact definitions."""

    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:
        registry = create_builtin_registry()

        context = context.with_artifact_registry(
            registry
        )

        return context