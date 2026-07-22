"""The Semantic Layer (v0.15.0): typed relationships as a dependency graph.

Where v0.14.0's Canon Validation Engine answers "is this Canon
structurally valid" (every entity well-formed, identities consistent,
references resolvable), this package answers "does this Canon's web of
relationships form a coherent, orderable graph" -- specifically: no
relationship type that's supposed to express a strict dependency order
(`REQUIRES`, today) actually forms a cycle.

    Canon (entities + relationships)
              |
              v
    RelationshipOntology  (knowledge/ontology/relationship-types.yaml,
                            typed: source/target types, symmetric, acyclic)
              |
              v
    SemanticGraph  (GraphNode per entity, GraphEdge per relationship)
              |
       +------+------+
       |             |
       v             v
  CycleDetector  topological_sort
       |
       v
  DependencyGraphValidator  (a CanonValidator; plugs into
                              forge validate / forge compile)

See `docs/architecture/SEMANTIC_LAYER.md` for the full write-up.
"""

from numeria_forge.semantics.cycle_detector import Cycle, CycleDetector
from numeria_forge.semantics.edge import GraphEdge
from numeria_forge.semantics.graph import SemanticGraph
from numeria_forge.semantics.node import GraphNode
from numeria_forge.semantics.ontology import (
    OntologyError,
    RelationshipOntology,
    RelationshipTypeDefinition,
)
from numeria_forge.semantics.orphan_validator import OrphanedEntityValidator
from numeria_forge.semantics.topo_sort import TopologicalSortError, topological_sort
from numeria_forge.semantics.validator import DependencyGraphValidator

__all__ = [
    "Cycle",
    "CycleDetector",
    "DependencyGraphValidator",
    "GraphEdge",
    "GraphNode",
    "OntologyError",
    "OrphanedEntityValidator",
    "RelationshipOntology",
    "RelationshipTypeDefinition",
    "SemanticGraph",
    "TopologicalSortError",
    "topological_sort",
]
