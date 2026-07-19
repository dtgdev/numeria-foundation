from numeria_forge.compiler.context import CompilerContext
from numeria_forge.infrastructure.repository import RepositoryWriter


class PublishArtifactsStage:
    """Publish compiler artifacts to the repository."""

    def __init__(self, writer: RepositoryWriter) -> None:
        self.writer = writer

    def run(self, context: CompilerContext) -> CompilerContext:
        for artifact in context.artifacts:
            self.writer.write(
                artifact.destination,
                artifact.content,
            )

        return context