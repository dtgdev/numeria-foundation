
"""Forge compiler."""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext

from numeria_forge.compiler.stage import CompilerStage

class Compiler:

    """Execute compiler stages."""

    def __init__(

        self,

        stages: list[CompilerStage],

    ) -> None:

        self._stages = list(stages)

    def compile(

        self,

        context: CompilerContext,

    ) -> CompilerContext:

        for stage in self._stages:

            stage.run(context)

        return context

