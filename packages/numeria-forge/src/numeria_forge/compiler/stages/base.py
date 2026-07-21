from abc import abstractmethod, ABC
from typing import Protocol

from numeria_forge.compiler.context import CompilerContext


class PipelineStage(ABC):

    @abstractmethod
    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:
        context.manifest = self.loader.load(

            context.source_directory

        )

        return context