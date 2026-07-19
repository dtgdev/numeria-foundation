from collections.abc import Sequence
from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stages import PipelineStage


class Compiler:
    """Execute compiler stages in sequence."""

    def __init__(self, stages: Sequence[PipelineStage]) -> None:
        self.stages = list(stages)

    def compile(self, package_directory: Path) -> CompilerContext:
        context = CompilerContext(
            source_directory=package_directory,
        )

        for stage in self.stages:
            context = stage.run(context)

        return context