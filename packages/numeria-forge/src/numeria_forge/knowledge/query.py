"""The stable query API over a :class:`CanonicalKnowledgeModel`.

Everything here is a thin, read-only wrapper around
`numeria_forge.semantics.SemanticGraph` and `numeria_forge.domain.canon.Canon`
-- no new storage, no second copy of entity content. The point of this
module is not new data, it's a *stable surface*: the compiler, Numeria
Studio, AI generators, and anything else that needs to ask "what does
this entity connect to" should go through `KnowledgeQuery` rather than
walking `SemanticGraph`/`Canon` directly, so that surface can stay
stable even if the underlying graph representation changes later.

Traversal order is deterministic (neighbors visited in sorted id
order at each BFS level), matching Compiler Law #1
(`governance/COMPILER_LAWS.md`) -- anything built on top of this API
(e.g. assembling AI context, or a Studio graph view) inherits that
determinism for free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from numeria_forge.domain.canon.canon import Canon
from numeria_forge.domain.canon.entity import CanonEntity
from numeria_forge.semantics.graph import SemanticGraph
from numeria_forge.semantics.ontology import RelationshipOntology

Direction = str  # "outgoing" | "incoming"


@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    """Query operations over one loaded Canon + its semantic graph."""

    canon: Canon
    graph: SemanticGraph
    ontology: RelationshipOntology

    def get(self, entity_id: str) -> CanonEntity | None:
        """The full entity behind a graph node id, or None if unknown."""

        return self.canon.entities.get(entity_id)

    def entities_of_type(self, entity_type: str) -> tuple[CanonEntity, ...]:
        return self.canon.by_type(entity_type)

    def related(
        self,
        entity_id: str,
        relationship_type: str,
        *,
        direction: Direction = "outgoing",
    ) -> tuple[CanonEntity, ...]:
        """Entities directly connected to ``entity_id`` by one
        relationship type, in a given direction. E.g.
        ``related("NUM-LESSON-000001", "TEACHES_CONCEPT")`` -- the
        Concepts a Lesson teaches; ``related(concept_id,
        "TEACHES_CONCEPT", direction="incoming")`` -- the Lessons that
        teach a Concept.
        """

        edges = self._edges(entity_id, (relationship_type,), direction)
        neighbor_ids = sorted(self._neighbor_id(edge, direction) for edge in edges)

        return tuple(
            entity
            for entity in (self.get(neighbor_id) for neighbor_id in neighbor_ids)
            if entity is not None
        )

    def traverse(
        self,
        start_id: str,
        *,
        types: Iterable[str] | None = None,
        direction: Direction = "outgoing",
        max_depth: int | None = None,
    ) -> tuple[str, ...]:
        """Breadth-first walk from ``start_id`` over the given
        relationship types (or every type, if omitted), returning the
        entity ids visited in traversal order (nearest first). The
        starting node itself is not included. Safe against cycles --
        already-visited nodes are never re-queued -- regardless of
        whether the relationship types involved are declared
        `acyclic` in the ontology, so this never hangs even on a
        malformed Canon.
        """

        if start_id not in self.graph.nodes:
            return ()

        visited = {start_id}
        order: list[str] = []
        frontier = [start_id]
        depth = 0

        while frontier and (max_depth is None or depth < max_depth):
            next_frontier: list[str] = []

            for node_id in frontier:
                edges = self._edges(node_id, types, direction)
                neighbor_ids = sorted(
                    {self._neighbor_id(edge, direction) for edge in edges}
                )

                for neighbor_id in neighbor_ids:
                    if neighbor_id in visited:
                        continue

                    visited.add(neighbor_id)
                    order.append(neighbor_id)
                    next_frontier.append(neighbor_id)

            frontier = next_frontier
            depth += 1

        return tuple(order)

    def orphaned_entities(self) -> tuple[CanonEntity, ...]:
        """Every entity touched by zero relationships, in either
        direction (v0.17.0 semantic integrity check). Not necessarily
        wrong -- a brand-new Concept with no relationships authored
        yet is orphaned by definition -- but worth surfacing. See
        `OrphanedEntityValidator` (numeria_forge.semantics) for an
        opt-in `forge validate` check built on this same method, and
        `CompilationReport`'s graph statistics for the count on every
        `forge compile` run.
        """

        ids = self.graph.orphaned_node_ids()

        return tuple(
            entity
            for entity in (self.get(entity_id) for entity_id in ids)
            if entity is not None
        )

    def prerequisites_of(self, entity_id: str) -> tuple[CanonEntity, ...]:
        """Every entity ``entity_id`` transitively requires, nearest
        first -- "everything needed before X". Driven entirely by
        whichever relationship types the ontology marks `acyclic:
        true` (`REQUIRES`, as of v0.15.0/v0.16.0); if none are
        declared, this returns an empty tuple rather than guessing.
        """

        acyclic_types = self.ontology.acyclic_type_names()

        if not acyclic_types:
            return ()

        ids = self.traverse(entity_id, types=acyclic_types, direction="outgoing")

        return tuple(
            entity
            for entity in (self.get(entity_id) for entity_id in ids)
            if entity is not None
        )

    def _edges(self, node_id, types, direction):
        if direction == "outgoing":
            return self.graph.outgoing(node_id, types=types)

        if direction == "incoming":
            return self.graph.incoming(node_id, types=types)

        raise ValueError(
            f"direction must be 'outgoing' or 'incoming', got {direction!r}"
        )

    @staticmethod
    def _neighbor_id(edge, direction):
        return edge.target_id if direction == "outgoing" else edge.source_id
