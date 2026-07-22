"""Golden integration test for the v0.15.0 Semantic Layer.

Builds a small Concept dependency chain on disk (Limit -> Derivative ->
Chain Rule, expressed as REQUIRES relationships), then exercises the
whole pipeline end to end: CanonLoader -> RelationshipOntology ->
SemanticGraph -> CycleDetector / topological_sort ->
DependencyGraphValidator. A companion test introduces a genuine cycle
and confirms every layer reports it.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.domain.canon import CanonLoader
from numeria_forge.domain.canon.validation import ValidationContext
from numeria_forge.semantics import (
    CycleDetector,
    DependencyGraphValidator,
    RelationshipOntology,
    SemanticGraph,
    TopologicalSortError,
    topological_sort,
)


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _write_ontology(knowledge_root: Path) -> None:
    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        """
version: "1.0.0"
status: CANON

relationship_types:
  REQUIRES:
    source: Concept
    target: Concept
    acyclic: true
""".strip(),
        encoding="utf-8",
    )


def build_concept_chain(knowledge_root: Path) -> None:
    """Limit -> Derivative -> Chain Rule, each REQUIRES the previous."""

    concepts = [
        ("NUM-CON-000001", "limit", "Limit"),
        ("NUM-CON-000002", "derivative", "Derivative"),
        ("NUM-CON-000003", "chain-rule", "Chain Rule"),
    ]

    for entity_id, slug, name in concepts:
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{slug}",
            id=entity_id,
            type="Concept",
            status="CANON",
            version="1.0.0",
            name=name,
            slug=slug,
        )

    requires_pairs = [
        ("NUM-REL-000001", "NUM-CON-000002", "NUM-CON-000001"),  # Derivative requires Limit
        ("NUM-REL-000002", "NUM-CON-000003", "NUM-CON-000002"),  # Chain Rule requires Derivative
    ]

    for edge_id, source_id, target_id in requires_pairs:
        _write_entity(
            knowledge_root / "relationships" / edge_id,
            id=edge_id,
            type="REQUIRES",
            status="CANON",
            version="1.0.0",
            source={"id": source_id, "type": "Concept"},
            target={"id": target_id, "type": "Concept"},
        )

    _write_ontology(knowledge_root)


def test_concept_chain_has_no_cycles_and_sorts_correctly(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    build_concept_chain(knowledge_root)

    canon = CanonLoader().load(knowledge_root)
    assert canon.load_errors == []

    ontology = RelationshipOntology.load_from_knowledge_root(knowledge_root)
    assert ontology.acyclic_type_names() == ("REQUIRES",)

    graph = SemanticGraph.build_from_canon(canon)
    assert len(graph) == 3
    assert len(graph.edges) == 2

    detector = CycleDetector(graph)
    assert detector.has_cycle(types=ontology.acyclic_type_names()) is False

    order = topological_sort(graph, types=ontology.acyclic_type_names())
    # Chain Rule requires Derivative requires Limit -- Chain Rule's edge
    # points at Derivative, Derivative's edge points at Limit, so
    # (source before target) puts Chain Rule first, Limit last.
    assert order.index("NUM-CON-000003") < order.index("NUM-CON-000002")
    assert order.index("NUM-CON-000002") < order.index("NUM-CON-000001")

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))
    assert result.success
    assert result.diagnostics == ()


def test_concept_chain_with_a_cycle_is_caught_at_every_layer(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    build_concept_chain(knowledge_root)

    # Introduce a cycle: Limit now also (incorrectly) REQUIRES Chain Rule.
    _write_entity(
        knowledge_root / "relationships" / "NUM-REL-000003",
        id="NUM-REL-000003",
        type="REQUIRES",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000003", "type": "Concept"},
    )

    canon = CanonLoader().load(knowledge_root)
    ontology = RelationshipOntology.load_from_knowledge_root(knowledge_root)
    graph = SemanticGraph.build_from_canon(canon)

    detector = CycleDetector(graph)
    assert detector.has_cycle(types=ontology.acyclic_type_names()) is True
    cycles = detector.find_cycles(types=ontology.acyclic_type_names())
    assert len(cycles) == 1
    assert set(cycles[0].nodes) == {
        "NUM-CON-000001",
        "NUM-CON-000002",
        "NUM-CON-000003",
    }

    try:
        topological_sort(graph, types=ontology.acyclic_type_names())
        raised = False
    except TopologicalSortError:
        raised = True

    assert raised

    result = DependencyGraphValidator().validate(ValidationContext(canon=canon))
    assert result.success is False
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == "canon.semantics.dependency-cycle"
