from collections.abc import Sequence
from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.pipeline_step import PipelineStep
from numeria_forge.compiler.stages import PipelineStage
from numeria_forge.extensions import CompilerHookRegistry


class Compiler:
    """Execute compiler pipeline steps."""

    def __init__(
        self,
        *,
        steps: Sequence[PipelineStep | PipelineStage] | None = None,
        stages: Sequence[PipelineStage] | None = None,
        hook_registry: CompilerHookRegistry | None = None,
    ) -> None:
        if steps is not None and stages is not None:
            raise ValueError(
                "Specify either 'steps' or 'stages', not both."
            )

        if steps is None:
            steps = stages if stages is not None else ()

        self.steps = [
            step
            if isinstance(step, PipelineStep)
            else PipelineStep(stage=step)
            for step in steps
        ]

        self.hook_registry = (
            hook_registry
            if hook_registry is not None
            else CompilerHookRegistry()
        )

    @property
    def stages(self) -> tuple[PipelineStage, ...]:
        """Backward-compatible access to pipeline stages."""

        return tuple(
            step.stage
            for step in self.steps
        )

    def compile(
        self,
        package_directory: Path,
    ) -> CompilerContext:
        context = CompilerContext(
            source_directory=package_directory,
        )

        for step in self.steps:
            if step.before is not None:
                self.hook_registry.run(
                    step.before,
                    context,
                )

            context = step.stage.run(context)

            if step.after is not None:
                self.hook_registry.run(
                    step.after,
                    context,
                )

        return context
