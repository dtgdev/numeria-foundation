from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stages.base import PipelineStage
from numeria_forge.domain.artifacts import create_builtin_registry


class RegisterManifestArtifactsStage(PipelineStage):
    """Build the artifact registry for this compilation."""

    def run(self, context: CompilerContext) -> CompilerContext:
        registry = create_builtin_registry()

        manifest = context.manifest

        if manifest is None:
            raise RuntimeError(
                "Manifest must be loaded before registering artifacts."
            )

        for definition in manifest.artifacts:
            registry.register(definition)

        context.artifact_registry = registry

        return context
