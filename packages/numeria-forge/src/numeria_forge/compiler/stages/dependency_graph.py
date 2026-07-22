"""Compiler stage: build the semantic dependency graph.

Part of the v0.15.0 Semantic Layer's integration into the compiler
pipeline:

    Load Canon -> Validate Canon -> Dependency Graph
    -> Topological Ordering -> Generation Pipeline -> ...

This stage does not itself validate anything -- it just builds
`context.semantic_graph` from the already-loaded Canon, one `GraphNode`
per non-relationship entity and one `GraphEdge` per relationship
entity (see `numeria_forge.semantics.SemanticGraph`). Cycle detection
happens in the next stage, `TopologicalOrderStage`.
"""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.semantics import SemanticGraph


class DependencyGraphStage(CompilerStage):
    """Build `context.semantic_graph` from `context.loaded_canon`."""

    @property
    def name(self) -> str:
        return "dependency-graph"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.loaded_canon is None:
            raise RuntimeError(
                "DependencyGraphStage requires LoadCanonStage to run first."
            )

        context.semantic_graph = SemanticGraph.build_from_canon(context.loaded_canon)

        return context
