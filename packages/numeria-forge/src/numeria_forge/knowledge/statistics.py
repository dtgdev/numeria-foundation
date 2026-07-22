"""Graph statistics for a `CanonicalKnowledgeModel` (v0.17.0).

Surfaced on `CompilationReport` so every `forge compile` run reports
"graph statistics and semantic validation results" (v0.17.0 success
criteria) without requiring `--json` or a separate command: node/edge
counts, a per-relationship-type edge breakdown, the orphaned-entity
count (see `SemanticGraph.orphaned_node_ids`), and which relationship
types the ontology declares `acyclic` (the ones dependency-cycle
detection actually checks).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GraphStatistics:
    node_count: int = 0
    edge_count: int = 0
    edge_type_counts: dict[str, int] = field(default_factory=dict)
    orphaned_node_count: int = 0
    acyclic_relationship_types: tuple[str, ...] = ()

    @classmethod
    def from_model(cls, model) -> "GraphStatistics":
        graph = model.graph
        edge_type_counts: dict[str, int] = {}

        for edge in sorted(graph.edges, key=lambda e: e.type):
            edge_type_counts[edge.type] = edge_type_counts.get(edge.type, 0) + 1

        return cls(
            node_count=len(graph),
            edge_count=len(graph.edges),
            edge_type_counts=edge_type_counts,
            orphaned_node_count=len(graph.orphaned_node_ids()),
            acyclic_relationship_types=model.ontology.acyclic_type_names(),
        )

    def to_dict(self) -> dict:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "edge_type_counts": dict(self.edge_type_counts),
            "orphaned_node_count": self.orphaned_node_count,
            "acyclic_relationship_types": list(self.acyclic_relationship_types),
        }
