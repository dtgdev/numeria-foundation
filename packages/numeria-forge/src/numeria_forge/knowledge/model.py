"""The Canonical Knowledge Model (v0.16.0): the single semantic
foundation every educational artifact is generated against.

    Canon (entities + relationships)
              |
              v
    RelationshipOntology  (knowledge/ontology/relationship-types.yaml)
              |
              v
    SemanticGraph          (v0.15.0 -- nodes + typed edges)
              |
              v
    CanonicalKnowledgeModel  <-- this module
              |
              v
    KnowledgeQuery           (numeria_forge.knowledge.query)

`CanonicalKnowledgeModel` does not introduce a new entity
representation -- `Character`, `Concept`, `Story`, `Lesson`,
`Assessment`, and every other Canon type already exist as
`CanonEntity` records inside `Canon` (see
`numeria_forge.domain.canon`), and the graph of typed relationships
between them already exists as `SemanticGraph` (see
`numeria_forge.semantics`, v0.15.0). This class is a thin composition
of those two, plus the `RelationshipOntology` that governs which
relationship types are legal between which entity types: it is the
"one object" the compiler, Numeria Studio, and AI generators can hold
onto and query, instead of each needing to know how to assemble a
Canon + SemanticGraph + RelationshipOntology themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from numeria_forge.domain.canon.canon import Canon
from numeria_forge.domain.canon.loader import CanonLoader
from numeria_forge.knowledge.query import KnowledgeQuery
from numeria_forge.semantics.graph import SemanticGraph
from numeria_forge.semantics.ontology import OntologyError, RelationshipOntology


@dataclass(frozen=True, slots=True)
class CanonicalKnowledgeModel:
    """A fully-loaded Canon, its semantic graph, and its governing
    ontology, exposed through a stable :class:`KnowledgeQuery`."""

    canon: Canon
    graph: SemanticGraph
    ontology: RelationshipOntology
    query: KnowledgeQuery

    def __len__(self) -> int:
        return len(self.canon)

    @classmethod
    def build(
        cls, canon: Canon, ontology: RelationshipOntology
    ) -> "CanonicalKnowledgeModel":
        """Build a model from an already-loaded Canon and ontology --
        used by the compiler pipeline, which has already loaded both
        via `LoadCanonStage`/`TopologicalOrderStage`'s ontology
        lookup, so this never re-reads either from disk.
        """

        graph = SemanticGraph.build_from_canon(canon)

        return cls(
            canon=canon,
            graph=graph,
            ontology=ontology,
            query=KnowledgeQuery(canon=canon, graph=graph, ontology=ontology),
        )

    @classmethod
    def build_from_root(
        cls,
        knowledge_root: Path,
        *,
        loader: CanonLoader | None = None,
    ) -> "CanonicalKnowledgeModel":
        """Load a Canon + its ontology from a `knowledge/` directory
        and build a model in one call -- the entry point for
        standalone consumers (Numeria Studio, AI generators, a
        notebook) that want to query the Canon without going through
        `forge compile`'s full pipeline. If the ontology file is
        missing or malformed, falls back to an empty
        `RelationshipOntology` (matching `TopologicalOrderStage`'s
        fail-open behavior) rather than raising -- the model still
        answers structural queries (`get`, `entities_of_type`,
        `related`), it just can't answer ontology-driven ones
        (`prerequisites_of`) until the ontology is fixed.
        """

        canon = (loader or CanonLoader()).load(knowledge_root)

        try:
            ontology = RelationshipOntology.load_from_knowledge_root(knowledge_root)
        except OntologyError:
            ontology = RelationshipOntology(
                path=knowledge_root / "ontology" / "relationship-types.yaml",
                version="",
                status="",
                types={},
            )

        return cls.build(canon, ontology)
