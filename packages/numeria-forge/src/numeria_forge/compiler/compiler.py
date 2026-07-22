from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage


class Compiler:
    """Numeria Forge compiler.

    Runs an ordered list of :class:`CompilerStage` instances against a
    :class:`CompilerContext`, mutating it in place, and returns that same
    context so callers can inspect artifacts, diagnostics, and derived
    state (``context.success``) after compilation.
    """

    def __init__(self, stages: list[CompilerStage]) -> None:
        self._stages = stages

    @property
    def stage_count(self) -> int:
        return len(self._stages)

    def compile(self, target: CompilerContext | Path) -> CompilerContext:
        context = self._resolve_context(target)

        for stage in self._stages:
            stage.execute(context)

        return context

    @staticmethod
    def _resolve_context(target: CompilerContext | Path) -> CompilerContext:
        if isinstance(target, CompilerContext):
            return target

        package_directory = Path(target)

        return CompilerContext(
            project_root=package_directory,
            source_directory=package_directory,
        )
