"""Compiler stage: publish `context.generated_assets` to `build/`.

Distinct from `PublishArtifactsStage`, which publishes
`context.artifacts` (manifest-driven, per-package output) relative to
a package directory. This stage publishes `context.generated_assets`
(foundation-wide, produced by `GenerateMissingAssetsStage`) relative to
`context.build_directory` instead -- the two artifact lists represent
different content and land in different places on disk.

`build/` is treated as a fully disposable, regenerated-every-run
directory (unlike hand-authored `knowledge/` or `packages/` content),
so writes here always overwrite rather than raising on an existing
file.
"""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.infrastructure.repository import RepositoryWriter
from numeria_forge.publishing import PublishResult


class PublishGeneratedAssetsStage(CompilerStage):
    """Write every artifact in `context.generated_assets` under
    `context.build_directory`."""

    def __init__(self, writer: RepositoryWriter | None = None) -> None:
        self._writer = writer or RepositoryWriter()

    @property
    def name(self) -> str:
        return "publish-generated-assets"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.build_directory is None:
            raise RuntimeError(
                "PublishGeneratedAssetsStage requires context.build_directory "
                "to be set."
            )

        for artifact in context.generated_assets:
            destination = context.build_directory / artifact.destination

            self._writer.write(
                destination=destination,
                content=artifact.content,
                overwrite=True,
            )

            context.published_assets.append(
                PublishResult(
                    publisher=self.name,
                    path=destination,
                    media_type=artifact.media_type,
                )
            )

        return context
