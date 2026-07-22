from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.result import CompilerResult
from numeria_forge.compiler.stage import CompilerStage


class Compiler:
    """Numeria Forge compiler."""

    def __init__(
        self,
        stages: list[CompilerStage],
    ) -> None:
        self._stages = stages

    def compile(
        self,
        context: CompilerContext,
    ) -> CompilerResult:

        for stage in self._stages:
            stage.execute(context)

        success = not any(
            d.severity.lower() == "error"
            for d in context.diagnostics
        )

        return CompilerResult(
            success=success,
            diagnostics=context.diagnostics,
        )