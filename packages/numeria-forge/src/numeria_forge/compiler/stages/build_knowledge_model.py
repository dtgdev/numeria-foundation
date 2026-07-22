"""Compiler stage: build the Canonical Knowledge Model (v0.16.0).

    Load Canon -> Validate Canon -> Dependency Graph
    -> Topological Ordering -> Build Knowledge Model -> Generation Pipeline -> ...

Reuses `context.loaded_canon` and `context.semantic_graph` rather than
rebuilding either -- this stage's only new work is loading the
ontology (same fail-open behavior as `TopologicalOrderStage`: a
missing/malformed ontology file falls back to an empty
`RelationshipOntology` rather than raising, since
`RelationshipValidator` -- part of `ValidateCanonStage`, earlier in
the pipeline -- already surfaces that as a diagnostic) and wrapping
the three into one `CanonicalKnowledgeModel`.

Runs unconditionally, not gated on `context.success` -- even a Canon
with validation errors or an unresolved dependency cycle still has a
Canon and a graph worth querying (e.g. `forge doctor`-style
diagnostics tooling, or a Studio graph view that wants to render the
Canon *including* its problems).
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.knowledge import CanonicalKnowledgeModel, KnowledgeQuery
from numeria_forge.semantics import OntologyError, RelationshipOntology


class BuildKnowledgeModelStage(CompilerStage):
    """Build `context.knowledge_model` from `context.loaded_canon` and
    `context.semantic_graph`."""

    def __init__(self, ontology_path: Path | None = None) -> None:
        self._ontology_path = ontology_path

    @property
    def name(self) -> str:
        return "build-knowledge-model"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.loaded_canon is None:
            raise RuntimeError(
                "BuildKnowledgeModelStage requires LoadCanonStage to run first."
            )

        if context.semantic_graph is None:
            raise RuntimeError(
                "BuildKnowledgeModelStage requires DependencyGraphStage to "
                "run first."
            )

        ontology_path = self._ontology_path or (
            context.loaded_canon.root / "ontology" / "relationship-types.yaml"
        )

        try:
            ontology = RelationshipOntology.load(ontology_path)
        except OntologyError:
            ontology = RelationshipOntology(
                path=ontology_path, version="", status="", types={}
            )

        context.knowledge_model = CanonicalKnowledgeModel(
            canon=context.loaded_canon,
            graph=context.semantic_graph,
            ontology=ontology,
            query=KnowledgeQuery(
                canon=context.loaded_canon,
                graph=context.semantic_graph,
                ontology=ontology,
            ),
        )

        return context
