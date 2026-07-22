"""A CanonValidator that checks the dependency graph is a DAG.

Fits the same `CanonValidator` contract as the ten v0.14.0 validators
(`domain.canon.validation`), so it can be added to the validator set
run by `forge validate` / `forge compile` without changing anything
about how they're invoked. Kept in its own `semantics` package rather
than alongside the others because it depends on the graph model
(`SemanticGraph`, `CycleDetector`), which the v0.14.0 validators have
no need for.

Only relationship types the ontology marks `acyclic: true` (today, just
`REQUIRES`) are checked -- most relationship types (`FRIEND_OF`,
`APPEARS_IN`, ...) have no directional dependency meaning, and a cycle
among them is not a defect.

If the ontology file itself is missing or malformed, this validator
reports nothing: `RelationshipValidator` (v0.14.0) already surfaces
that as its own diagnostic, and duplicating it under a second code
would just be noise for the same root cause.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult
from numeria_forge.semantics.cycle_detector import CycleDetector
from numeria_forge.semantics.graph import SemanticGraph
from numeria_forge.semantics.ontology import OntologyError, RelationshipOntology


class DependencyGraphValidator(CanonValidator):
    """Report every cycle found among ontology-declared acyclic relationship types."""

    def __init__(self, ontology: RelationshipOntology | None = None) -> None:
        self._ontology = ontology

    @property
    def name(self) -> str:
        return "canon.semantics.dependency-cycle"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon

        ontology = self._ontology

        if ontology is None:
            try:
                ontology = RelationshipOntology.load_from_knowledge_root(canon.root)
            except OntologyError:
                return ValidationResult(validator=self.name, diagnostics=())

        acyclic_types = ontology.acyclic_type_names()

        if not acyclic_types:
            return ValidationResult(validator=self.name, diagnostics=())

        graph = SemanticGraph.build_from_canon(canon)
        cycles = CycleDetector(graph).find_cycles(types=acyclic_types)

        diagnostics = tuple(
            Diagnostic(
                severity=Severity.ERROR,
                code=self.name,
                message=f"dependency cycle: {cycle}",
            )
            for cycle in cycles
        )

        return ValidationResult(validator=self.name, diagnostics=diagnostics)
