from dataclasses import dataclass

from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.extensions.hooks import HookPoint


@dataclass(frozen=True)
class PipelineStep:
    """A compiler stage together with its lifecycle hook points."""

    stage: CompilerStage
    before: HookPoint | None = None
    after: HookPoint | None = None
