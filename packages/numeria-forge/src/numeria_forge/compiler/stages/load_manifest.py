from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import PipelineStage
from numeria_forge.infrastructure.manifest_loader import ManifestLoader


class LoadManifestStage(PipelineStage):
    """Load the Numeria project manifest."""

    def __init__(
        self,
        loader: ManifestLoader | None = None,
    ) -> None:
        self._loader = loader or ManifestLoader()

    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:
        context.manifest = self._loader.load(
            context.source_directory,
        )
        return context