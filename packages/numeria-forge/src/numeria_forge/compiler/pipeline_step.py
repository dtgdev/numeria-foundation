from dataclasses import dataclass

from numeria_forge.compiler.stages.base import PipelineStage
from numeria_forge.extensions.hooks import HookPoint


@dataclass(frozen=True)
class PipelineStep:
    """A compiler stage together with its lifecycle hook points."""

    stage: PipelineStage
    before: HookPoint | None = None
    after: HookPoint | None = None
