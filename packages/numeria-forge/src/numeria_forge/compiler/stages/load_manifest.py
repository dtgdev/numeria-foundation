from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.infrastructure.manifest_loader import ManifestLoader


class LoadManifestStage(CompilerStage):
    """Load the Numeria project manifest."""

    def __init__(self, loader: ManifestLoader | None = None) -> None:
        self._loader = loader or ManifestLoader()

    @property
    def name(self) -> str:
        return "load-manifest"

    def execute(self, context: CompilerContext) -> CompilerContext:
        context.manifest = self._loader.load(context.source_directory)
        return context
