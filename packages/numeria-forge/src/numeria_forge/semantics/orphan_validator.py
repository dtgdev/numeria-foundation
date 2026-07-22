"""A CanonValidator that flags entities touched by zero relationships.

Fits the same `CanonValidator` contract as `DependencyGraphValidator`
(and the ten v0.14.0 validators), so it plugs into `forge validate` /
`forge compile`'s validator set without changing how they're invoked.
Opt-in, not part of the default set, for the same reason
`DependencyGraphValidator` is opt-in: an orphaned entity is not
necessarily a defect (a brand-new Concept genuinely has no
relationships yet until someone authors them), so making this a
default `forge validate` error would produce noise on every real
Canon that's still being written. `CompilationReport`'s graph
statistics (v0.17.0) surface the orphan *count* on every `forge
compile` run regardless of whether this validator is enabled; add
this validator when you want orphans to actually fail validation.

Severity is WARNING, not ERROR -- consistent with "not necessarily
wrong" above.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult
from numeria_forge.semantics.graph import SemanticGraph


class OrphanedEntityValidator(CanonValidator):
    """Report every entity with zero incoming and zero outgoing edges."""

    @property
    def name(self) -> str:
        return "canon.semantics.orphaned-entity"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon
        graph = SemanticGraph.build_from_canon(canon)

        diagnostics = tuple(
            Diagnostic(
                severity=Severity.WARNING,
                code=self.name,
                message=(
                    f"'{node_id}' ({graph.nodes[node_id].type}) has no "
                    "relationships in either direction"
                ),
                location=canon.entities[node_id].source_path
                if node_id in canon.entities
                else None,
            )
            for node_id in graph.orphaned_node_ids()
        )

        return ValidationResult(validator=self.name, diagnostics=diagnostics)
