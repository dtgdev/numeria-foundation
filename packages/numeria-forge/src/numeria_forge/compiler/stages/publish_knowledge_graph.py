"""Compiler stage: export `context.knowledge_model`'s graph to disk.

    Build Knowledge Model -> Publish Knowledge Graph (this stage)
    -> Generate Missing Assets -> ...

Writes `build/graph/knowledge.json`, `knowledge.yaml`, and
`knowledge.graphml` (v0.17.0) -- the same underlying graph in three
machine-readable formats (`numeria_forge.knowledge.export`), for
whatever downstream tooling wants it: a Studio graph view, an offline
graph-analysis tool (GraphML), a script that just wants JSON.

Requires `context.knowledge_model` (raises `RuntimeError` otherwise --
run `BuildKnowledgeModelStage` first). Runs unconditionally, same
reasoning as `BuildKnowledgeModelStage` itself: a Canon with
validation errors or a dependency cycle still has a graph worth
exporting for inspection. `build/` is fully disposable, regenerated
every run, so writes always overwrite.
"""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.infrastructure.repository import RepositoryWriter
from numeria_forge.knowledge import export
from numeria_forge.publishing import PublishResult


class PublishKnowledgeGraphStage(CompilerStage):
    """Write `context.knowledge_model`'s graph to `build/graph/`."""

    def __init__(self, writer: RepositoryWriter | None = None) -> None:
        self._writer = writer or RepositoryWriter()

    @property
    def name(self) -> str:
        return "publish-knowledge-graph"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.knowledge_model is None:
            raise RuntimeError(
                "PublishKnowledgeGraphStage requires BuildKnowledgeModelStage "
                "to run first."
            )

        if context.build_directory is None:
            raise RuntimeError(
                "PublishKnowledgeGraphStage requires context.build_directory "
                "to be set."
            )

        graph_directory = context.build_directory / "graph"
        model = context.knowledge_model

        for filename, content, media_type in (
            ("knowledge.json", export.to_json(model), "application/json"),
            ("knowledge.yaml", export.to_yaml(model), "application/yaml"),
            ("knowledge.graphml", export.to_graphml(model), "application/xml"),
        ):
            destination = graph_directory / filename

            self._writer.write(destination=destination, content=content, overwrite=True)

            context.published_assets.append(
                PublishResult(
                    publisher=self.name, path=destination, media_type=media_type
                )
            )

        return context
