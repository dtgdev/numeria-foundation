"""The in-memory dependency graph built from a loaded Canon.

No graph database is needed -- just a graph model. `SemanticGraph` is a
read-only view over a `Canon`: one `GraphNode` per non-relationship
entity, one `GraphEdge` per relationship entity. `CycleDetector` and
`topological_sort` (siblings in this package) both operate on this
graph rather than walking `Canon` directly, so they don't need to know
anything about YAML, entity files, or the Canon Validation Engine.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from numeria_forge.domain.canon.canon import Canon
from numeria_forge.semantics.edge import GraphEdge
from numeria_forge.semantics.node import GraphNode


@dataclass(frozen=True, slots=True)
class SemanticGraph:
    """A directed graph of canonical entities connected by relationships."""

    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: tuple[GraphEdge, ...] = ()

    def __len__(self) -> int:
        return len(self.nodes)

    def __contains__(self, node_id: object) -> bool:
        return node_id in self.nodes

    def edges_of_type(self, *type_names: str) -> tuple[GraphEdge, ...]:
        wanted = set(type_names)

        return tuple(edge for edge in self.edges if edge.type in wanted)

    def outgoing(
        self, node_id: str, *, types: Iterable[str] | None = None
    ) -> tuple[GraphEdge, ...]:
        wanted = set(types) if types is not None else None

        return tuple(
            edge
            for edge in self.edges
            if edge.source_id == node_id and (wanted is None or edge.type in wanted)
        )

    def adjacency(
        self, *, types: Iterable[str] | None = None
    ) -> dict[str, tuple[str, ...]]:
        """Build `{node_id: (neighbor_id, ...)}` for the given edge types
        (or every edge type if `types` is omitted). Only includes edges
        whose source and target both resolve to a known node -- a
        dangling reference is a Canon Validation Engine concern
        (`RelationshipValidator`), not a graph-traversal concern.
        """

        wanted = set(types) if types is not None else None
        adjacency: dict[str, list[str]] = defaultdict(list)

        for edge in self.edges:
            if wanted is not None and edge.type not in wanted:
                continue

            if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
                continue

            adjacency[edge.source_id].append(edge.target_id)

        return {node_id: tuple(targets) for node_id, targets in adjacency.items()}

    @classmethod
    def build_from_canon(cls, canon: Canon) -> "SemanticGraph":
        nodes = {
            entity.id: GraphNode(id=entity.id, type=entity.type)
            for entity in canon.non_relationships()
        }

        edges: list[GraphEdge] = []

        for relationship in canon.relationships():
            source = relationship.get("source") or {}
            target = relationship.get("target") or {}
            source_id = source.get("id")
            target_id = target.get("id")

            if not source_id or not target_id:
                # Malformed relationship -- the Canon Validation Engine's
                # RelationshipValidator is what reports this as a
                # diagnostic. The graph simply skips edges it can't
                # anchor at both ends rather than guessing.
                continue

            edges.append(
                GraphEdge(
                    id=relationship.id,
                    type=relationship.type,
                    source_id=source_id,
                    target_id=target_id,
                    description=relationship.get("description"),
                    metadata=relationship.get("relationship_properties") or {},
                    source_path=relationship.source_path,
                )
            )

        return cls(nodes=nodes, edges=tuple(edges))
