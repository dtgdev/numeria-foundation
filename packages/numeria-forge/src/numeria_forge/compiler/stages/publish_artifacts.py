from numeria_forge.compiler.context import CompilerContext
from numeria_forge.infrastructure.repository import RepositoryWriter


class PublishArtifactsStage:
    """Publish compiler artifacts to the repository."""

    def __init__(self, writer: RepositoryWriter) -> None:
        self.writer = writer

    def execute(
        self,
        context: CompilerContext,
    ) -> CompilerContext:
        for artifact in context.rendered_artifacts:
            self.writer.write(
                destination=artifact.destination,
                content=artifact.content,
            )

        return context