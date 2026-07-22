"""Compiler stage: the Canon Loader."""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.domain.canon.loader import CanonLoader


class LoadCanonStage(CompilerStage):
    """Load the full knowledge base into ``context.loaded_canon``."""

    def __init__(
        self,
        knowledge_root: Path | None = None,
        loader: CanonLoader | None = None,
    ) -> None:
        self._knowledge_root = knowledge_root
        self._loader = loader or CanonLoader()

    @property
    def name(self) -> str:
        return "load-canon"

    def execute(self, context: CompilerContext) -> CompilerContext:
        knowledge_root = self._knowledge_root or (
            context.source_directory / "knowledge"
        )

        context.loaded_canon = self._loader.load(knowledge_root)

        return context
