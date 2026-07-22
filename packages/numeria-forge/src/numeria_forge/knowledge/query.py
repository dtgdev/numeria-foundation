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
from numeria_forge.semantics.topo_sort import TopologicalSortError, topological_sort

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

    def learning_path(self, entity_id: str) -> tuple[CanonEntity, ...]:
        """The ordered sequence of entities to learn, prerequisites
        first, ending with ``entity_id`` itself (v0.18.0 -- "Learning
        Graph"). Where `prerequisites_of` gives the unordered
        transitive closure ("everything needed before X"), this gives
        the specific sequence to learn them in.

        A thin wrapper over `_ordered_path` scoped to `traversal:
        "learning"` (today: just `REQUIRES`) -- see `_ordered_path`
        for the algorithm and `_ordered_path`'s and
        `RelationshipOntology.acyclic_type_names`'s docstrings for why
        this is scoped by traversal rather than using every
        `acyclic`-declared type combined (v0.19.0 added a second
        acyclic, ordered relationship type, `FOLLOWS_SCENE`, for
        `.story_path` -- without this scoping the two would be
        combined into one meaningless topological order).
        """

        return self._ordered_path(entity_id, traversal="learning")

    def story_path(self, scene_id: str) -> tuple[CanonEntity, ...]:
        """The ordered reading sequence of Scenes, earliest first,
        ending with ``scene_id`` itself (v0.19.0 -- "Views over One
        Canon"). The narrative counterpart of `.learning_path`: same
        algorithm, scoped to `traversal: "story"` (today: just
        `FOLLOWS_SCENE`) instead of `"learning"`. Not a second graph
        engine -- `FOLLOWS_SCENE` is walked through the same
        `SemanticGraph` every other relationship type is, just via a
        different named, ontology-declared view. See
        `docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md`.

        Returns an empty tuple if ``scene_id`` is unknown, if no
        relationship type is declared `acyclic` with `traversal:
        "story"` (nothing to order), or if the Scene graph actually
        contains a cycle.
        """

        return self._ordered_path(scene_id, traversal="story")

    def prerequisites_of(self, entity_id: str) -> tuple[CanonEntity, ...]:
        """Every entity ``entity_id`` transitively requires, nearest
        first -- "everything needed before X". Driven entirely by
        whichever relationship types the ontology marks `acyclic:
        true` *and* `traversal: "learning"` (`REQUIRES`, as of
        v0.15.0/v0.16.0); if none are declared, this returns an empty
        tuple rather than guessing.
        """

        return self._predecessors(entity_id, traversal="learning")

    def _predecessors(
        self, entity_id: str, *, traversal: str
    ) -> tuple[CanonEntity, ...]:
        """Everything `entity_id` transitively points at via
        outgoing, acyclic, `traversal`-scoped relationship types,
        nearest first. The shared implementation behind
        `prerequisites_of` (`traversal="learning"`); `.story_path`
        uses this internally too, to find every scene a given scene
        transitively follows.
        """

        acyclic_types = self.ontology.acyclic_type_names(traversal=traversal)

        if not acyclic_types:
            return ()

        ids = self.traverse(entity_id, types=acyclic_types, direction="outgoing")

        return tuple(
            entity
            for entity in (self.get(entity_id) for entity_id in ids)
            if entity is not None
        )

    def _ordered_path(
        self, entity_id: str, *, traversal: str
    ) -> tuple[CanonEntity, ...]:
        """The shared algorithm behind `.learning_path` and
        `.story_path`: a `traversal`-scoped topological order,
        reversed into "earliest first" order (see `.learning_path`'s
        original docstring for why the reversal is needed), then
        filtered down to just `entity_id`'s own transitive
        predecessors plus itself, preserving their relative order.
        """

        if entity_id not in self.graph.nodes:
            return ()

        acyclic_types = self.ontology.acyclic_type_names(traversal=traversal)

        if not acyclic_types:
            entity = self.get(entity_id)
            return (entity,) if entity is not None else ()

        relevant_ids = {entity_id} | {
            predecessor.id
            for predecessor in self._predecessors(entity_id, traversal=traversal)
        }

        try:
            whole_graph_order = topological_sort(self.graph, types=acyclic_types)
        except TopologicalSortError:
            return ()

        ordered = tuple(reversed(whole_graph_order))
        filtered_ids = (node_id for node_id in ordered if node_id in relevant_ids)

        return tuple(
            entity
            for entity in (self.get(node_id) for node_id in filtered_ids)
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
