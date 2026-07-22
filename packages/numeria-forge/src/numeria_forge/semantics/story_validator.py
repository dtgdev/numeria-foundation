"""A CanonValidator that checks narrative (`traversal: "story"`)
relationship types form structurally sound story sequences.

Fits the same `CanonValidator` contract as `DependencyGraphValidator`
and `OrphanedEntityValidator`, so it plugs into `forge validate` /
`forge compile`'s validator set without changing how they're invoked.
Opt-in, not part of the default set -- same reasoning as the other two
semantics validators: a story mid-authoring genuinely can lack a
beginning or an ending for a while, so this being a default `forge
validate` error would produce noise on every real Canon that's still
being written.

Does not hardcode `FOLLOWS_SCENE` -- like `RelationshipValidator`
(v0.14.0) and `DependencyGraphValidator` (v0.15.0), it asks the
ontology which relationship types are declared `acyclic: true` *and*
`traversal: "story"` (v0.19.0), so a second narrative-ordering
relationship type introduced later is covered automatically without
touching this file.

Cycle detection for these same relationship types is already covered
by `DependencyGraphValidator`, which checks every `acyclic`-declared
type combined (not just this validator's `traversal: "story"` subset)
-- this validator does not duplicate that check.

Scope, honestly stated: this checks that every group of Scenes
connected by a story-traversal relationship type has at least one
Scene with no outgoing edge of that type (a "beginning" -- follows
nothing) and at least one Scene with no incoming edge of that type (an
"ending" -- nothing follows it). It does *not* check "every character
is reachable" or "required artifacts exist" from the original v0.19
vision sketch -- both of those need a first-class notion of "which
Scenes belong to this story," which the Canon does not have yet
(`FOLLOWS_SCENE` today only expresses pairwise scene order, not story
membership boundaries; see `docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md`).
Deferred rather than guessed at, the same way ADR-0007 deferred
learner state rather than build something half-specified.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult
from numeria_forge.semantics.graph import SemanticGraph
from numeria_forge.semantics.ontology import OntologyError, RelationshipOntology


class StoryValidator(CanonValidator):
    """Report every story-traversal component missing a beginning or an ending."""

    def __init__(self, ontology: RelationshipOntology | None = None) -> None:
        self._ontology = ontology

    @property
    def name(self) -> str:
        return "canon.semantics.story-structure"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon

        ontology = self._ontology

        if ontology is None:
            try:
                ontology = RelationshipOntology.load_from_knowledge_root(canon.root)
            except OntologyError:
                return ValidationResult(validator=self.name, diagnostics=())

        story_types = ontology.acyclic_type_names(traversal="story")

        if not story_types:
            return ValidationResult(validator=self.name, diagnostics=())

        graph = SemanticGraph.build_from_canon(canon)
        components = self._components(graph, story_types)

        diagnostics: list[Diagnostic] = []

        for component in components:
            beginnings = {
                node_id
                for node_id in component
                if not graph.outgoing(node_id, types=story_types)
            }
            endings = {
                node_id
                for node_id in component
                if not graph.incoming(node_id, types=story_types)
            }

            if not beginnings:
                diagnostics.append(
                    self._diagnostic(
                        canon,
                        component,
                        "has no beginning (every scene follows another -- "
                        "likely a cycle; see DependencyGraphValidator)",
                    )
                )

            if not endings:
                diagnostics.append(
                    self._diagnostic(
                        canon,
                        component,
                        "has no ending (every scene is followed by another -- "
                        "likely a cycle; see DependencyGraphValidator)",
                    )
                )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))

    def _diagnostic(self, canon, component: frozenset[str], detail: str) -> Diagnostic:
        anchor = min(component)

        return Diagnostic(
            severity=Severity.WARNING,
            code=self.name,
            message=f"story component {sorted(component)} {detail}",
            location=canon.entities[anchor].source_path
            if anchor in canon.entities
            else None,
        )

    @staticmethod
    def _components(
        graph: SemanticGraph, types: tuple[str, ...]
    ) -> tuple[frozenset[str], ...]:
        """Weakly-connected components of the subgraph touched by
        ``types`` -- nodes never touched by any of these relationship
        types are not part of any component (out of scope for this
        validator; see `OrphanedEntityValidator` for untouched nodes
        generally).
        """

        adjacency: dict[str, set[str]] = {}

        for edge in graph.edges_of_type(*types):
            adjacency.setdefault(edge.source_id, set()).add(edge.target_id)
            adjacency.setdefault(edge.target_id, set()).add(edge.source_id)

        seen: set[str] = set()
        components: list[frozenset[str]] = []

        for start in sorted(adjacency):
            if start in seen:
                continue

            component: set[str] = set()
            frontier = [start]

            while frontier:
                node_id = frontier.pop()

                if node_id in component:
                    continue

                component.add(node_id)
                frontier.extend(adjacency.get(node_id, ()))

            seen |= component
            components.append(frozenset(component))

        return tuple(components)
