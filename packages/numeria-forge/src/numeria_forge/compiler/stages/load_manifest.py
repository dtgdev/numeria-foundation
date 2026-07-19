from numeria_forge.compiler.context import CompilerContext
from numeria_forge.infrastructure.manifest_loader import ManifestLoader


class LoadManifestStage:
    """Load manifest.yaml into the compiler context."""

    def __init__(self, loader: ManifestLoader | None = None) -> None:
        self.loader = loader or ManifestLoader()

    def run(self, context: CompilerContext) -> CompilerContext:
        context.manifest = self.loader.load(context.source_directory)
        return context