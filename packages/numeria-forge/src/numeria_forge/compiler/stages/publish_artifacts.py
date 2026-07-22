"""Compiler stage: publish rendered artifacts to disk.

`RenderTemplatesStage` only produces `Artifact`s in memory
(`context.artifacts`); nothing wrote them to disk until this stage
runs. Each `Artifact.destination` is a *relative* path (e.g.
`"README.md"`) -- this stage resolves it against a base directory
(the package directory being compiled, by default) before writing, so
output lands next to the `manifest.yaml` it came from rather than
wherever the process happened to be run from.
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.infrastructure.repository import RepositoryWriter


class PublishArtifactsStage(CompilerStage):
    """Publish compiler artifacts to disk, relative to a base directory."""

    def __init__(
        self,
        writer: RepositoryWriter | None = None,
        output_directory: Path | None = None,
        overwrite: bool = True,
    ) -> None:
        self.writer = writer or RepositoryWriter()
        self._output_directory = output_directory
        self._overwrite = overwrite

    @property
    def name(self) -> str:
        return "publish-artifacts"

    def execute(self, context: CompilerContext) -> CompilerContext:
        base_directory = (
            self._output_directory
            or context.output_directory
            or context.source_directory
            or context.project_root
        )

        for artifact in context.artifacts:
            destination = base_directory / artifact.destination

            self.writer.write(
                destination=destination,
                content=artifact.content,
                overwrite=self._overwrite,
            )

        return context
