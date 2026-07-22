"""Compiler stage: topologically order the dependency graph.

Restricted to whichever relationship types the ontology marks
`acyclic: true` (`REQUIRES`, as of v0.15.0). Two deliberate fail-open
behaviors, matching `DependencyGraphValidator`
(`numeria_forge.semantics.validator`):

* A missing or malformed ontology file is not re-reported here --
  `RelationshipValidator` (run as part of `ValidateCanonStage`, earlier
  in the pipeline) already surfaces that as its own diagnostic.
* No `acyclic` relationship types declared means nothing to order;
  `context.topological_order` is left empty, not an error.

A genuine cycle, however, **is** this stage's problem: it appends an
ERROR diagnostic to `context.diagnostics`, which is what actually
blocks `FoundationCompiler` from proceeding to package generation (via
the same `context.success` gate already used after Canon validation).
This means dependency-cycle detection is part of every `forge compile`
run unconditionally -- independent of whether
`DependencyGraphValidator` has been added to the Canon Validation
Engine's validator set (see `docs/architecture/SEMANTIC_LAYER.md` for
why that validator is opt-in rather than a default).
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.diagnostics import Diagnostic
from numeria_forge.diagnostics import Severity as DiagnosticSeverity
from numeria_forge.semantics import OntologyError, RelationshipOntology, topological_sort
from numeria_forge.semantics.topo_sort import TopologicalSortError


class TopologicalOrderStage(CompilerStage):
    """Compute `context.topological_order` from `context.semantic_graph`."""

    def __init__(self, ontology_path: Path | None = None) -> None:
        self._ontology_path = ontology_path

    @property
    def name(self) -> str:
        return "topological-order"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.loaded_canon is None:
            raise RuntimeError(
                "TopologicalOrderStage requires LoadCanonStage to run first."
            )

        if context.semantic_graph is None:
            raise RuntimeError(
                "TopologicalOrderStage requires DependencyGraphStage to run first."
            )

        ontology_path = self._ontology_path or (
            context.loaded_canon.root / "ontology" / "relationship-types.yaml"
        )

        try:
            ontology = RelationshipOntology.load(ontology_path)
        except OntologyError:
            context.topological_order = ()
            return context

        acyclic_types = ontology.acyclic_type_names()

        if not acyclic_types:
            context.topological_order = ()
            return context

        try:
            context.topological_order = topological_sort(
                context.semantic_graph, types=acyclic_types
            )
        except TopologicalSortError as exc:
            for cycle in exc.cycles:
                context.diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        code="canon.semantics.dependency-cycle",
                        message=f"dependency cycle: {cycle}",
                    )
                )

            context.topological_order = ()

        return context
