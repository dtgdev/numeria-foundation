"""Integration test: the full lifecycle from a raw Canon on disk, through
`forge compile`'s real pipeline, to a working `KnowledgeQuery`.

Distinct from the unit-level tests elsewhere:

- `tests/knowledge/test_model.py` / `test_query.py` build a
  `CanonicalKnowledgeModel` directly (`CanonicalKnowledgeModel.build_from_root`),
  bypassing the compiler entirely.
- `tests/compiler/test_build_knowledge_model_stage.py` exercises
  `BuildKnowledgeModelStage` in isolation against a hand-built
  `CompilerContext`.

This test instead drives the whole thing the way `forge compile`
actually does -- `FoundationCompiler().compile(root)` against a real
`numeria.yaml` + `knowledge/` tree on disk -- and then asks real
questions of `result.knowledge_model.query`, proving every layer
(Canon load -> Validate -> Dependency Graph -> Topological Order ->
Build Knowledge Model) actually connects end to end.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.compiler import FoundationCompiler


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _write_relationship(
    directory: Path,
    *,
    rel_id: str,
    rel_type: str,
    source_id: str,
    source_type: str,
    target_id: str,
    target_type: str,
) -> None:
    _write_entity(
        directory,
        id=rel_id,
        type=rel_type,
        status="CANON",
        version="1.0.0",
        source={"id": source_id, "type": source_type},
        target={"id": target_id, "type": target_type},
    )


def _write_numeria_yaml(root: Path) -> None:
    (root / "numeria.yaml").write_text(
        """
schema_version: "1.0"

foundation:
  id: knowledge-model-lifecycle
  name: Knowledge Model Lifecycle Fixture
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
  - packages/none
""".strip(),
        encoding="utf-8",
    )


def _build_small_canon(root: Path) -> None:
    """Function -> {Variable, Constant}, Limit -> Function,
    Derivative -> Limit (REQUIRES); a Character REPRESENTED_BY
    Derivative; a Lesson TEACHES_CONCEPT Derivative -- small enough to
    read at a glance, rich enough to exercise every KnowledgeQuery
    method against a real, multi-hop chain."""

    root.mkdir(parents=True, exist_ok=True)
    _write_numeria_yaml(root)

    knowledge_root = root / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Variable"),
        ("NUM-CON-000002", "Constant"),
        ("NUM-CON-000003", "Function"),
        ("NUM-CON-000004", "Limit"),
        ("NUM-CON-000005", "Derivative"),
    ):
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id, type="Concept", status="CANON", version="1.0.0",
            name=name,
        )

    _write_entity(
        knowledge_root / "characters" / "NUM-CHR-000001-detective",
        id="NUM-CHR-000001", type="Character", status="CANON", version="1.0.0",
        name="Detective Derivative", role="Detective of Change",
    )
    _write_entity(
        knowledge_root / "lessons" / "NUM-LESSON-000001",
        id="NUM-LESSON-000001", type="Lesson", status="CANON", version="1.0.0",
        name="Intro to Derivatives", grade_band="6-8",
        primary_concept="derivative", primary_learning_objective="rate of change",
    )

    relationships = [
        ("NUM-REL-000001", "REQUIRES", "NUM-CON-000003", "Concept", "NUM-CON-000001", "Concept"),
        ("NUM-REL-000002", "REQUIRES", "NUM-CON-000003", "Concept", "NUM-CON-000002", "Concept"),
        ("NUM-REL-000003", "REQUIRES", "NUM-CON-000004", "Concept", "NUM-CON-000003", "Concept"),
        ("NUM-REL-000004", "REQUIRES", "NUM-CON-000005", "Concept", "NUM-CON-000004", "Concept"),
        ("NUM-REL-000005", "REPRESENTED_BY", "NUM-CON-000005", "Concept", "NUM-CHR-000001", "Character"),
        ("NUM-REL-000006", "TEACHES_CONCEPT", "NUM-LESSON-000001", "Lesson", "NUM-CON-000005", "Concept"),
    ]

    for rel_id, rel_type, source_id, source_type, target_id, target_type in relationships:
        _write_relationship(
            knowledge_root / "relationships" / rel_id,
            rel_id=rel_id, rel_type=rel_type,
            source_id=source_id, source_type=source_type,
            target_id=target_id, target_type=target_type,
        )

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
    category: learning
    traversal: learning
  REPRESENTED_BY:
    source: Concept
    target: Character
  TEACHES_CONCEPT:
    source: Lesson
    target: Concept
""".strip(),
        encoding="utf-8",
    )


def test_full_lifecycle_from_canon_to_knowledge_model_query(tmp_path: Path) -> None:
    _build_small_canon(tmp_path)

    template_root = Path(__file__).resolve().parents[2] / "templates"
    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True
    assert result.knowledge_model is not None

    query = result.knowledge_model.query

    # entities_of_type
    concepts = query.entities_of_type("Concept")
    assert {c.id for c in concepts} == {
        "NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003",
        "NUM-CON-000004", "NUM-CON-000005",
    }

    # related(), outgoing: the Character representing Derivative
    represented_by = query.related("NUM-CON-000005", "REPRESENTED_BY")
    assert [e.id for e in represented_by] == ["NUM-CHR-000001"]

    # related(), incoming: the Lesson teaching Derivative
    taught_by = query.related(
        "NUM-CON-000005", "TEACHES_CONCEPT", direction="incoming"
    )
    assert [e.id for e in taught_by] == ["NUM-LESSON-000001"]

    # prerequisites_of: the full multi-hop REQUIRES chain, nearest first
    prereqs = query.prerequisites_of("NUM-CON-000005")
    assert [e.id for e in prereqs] == [
        "NUM-CON-000004",  # Limit
        "NUM-CON-000003",  # Function
        "NUM-CON-000001",  # Variable
        "NUM-CON-000002",  # Constant
    ]

    # traverse: depth-limited walk over the same chain
    one_hop = query.traverse("NUM-CON-000005", types=("REQUIRES",), max_depth=1)
    assert one_hop == ("NUM-CON-000004",)

    # get(): the full entity backing a graph node id
    entity = query.get("NUM-CON-000005")
    assert entity is not None
    assert entity.get("name") == "Derivative"

    # The same model is reachable both ways -- .knowledge_model is a
    # first-class property, not a substitute for context access.
    assert result.knowledge_model is result.context.knowledge_model


def test_knowledge_model_is_still_populated_and_query_safe_on_a_cyclic_canon(
    tmp_path: Path,
) -> None:
    """A Canon with a genuine dependency cycle fails compilation (the
    same `context.success` gate as always), but BuildKnowledgeModelStage
    still runs -- the graph and Canon are still worth querying even
    when invalid -- and querying it must not hang."""

    tmp_path.mkdir(parents=True, exist_ok=True)
    _write_numeria_yaml(tmp_path)

    knowledge_root = tmp_path / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Limit"),
        ("NUM-CON-000002", "Derivative"),
    ):
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id, type="Concept", status="CANON", version="1.0.0",
            name=name,
        )

    _write_relationship(
        knowledge_root / "relationships" / "NUM-REL-000001",
        rel_id="NUM-REL-000001", rel_type="REQUIRES",
        source_id="NUM-CON-000002", source_type="Concept",
        target_id="NUM-CON-000001", target_type="Concept",
    )
    _write_relationship(
        knowledge_root / "relationships" / "NUM-REL-000002",
        rel_id="NUM-REL-000002", rel_type="REQUIRES",
        source_id="NUM-CON-000001", source_type="Concept",
        target_id="NUM-CON-000002", target_type="Concept",
    )

    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types:\n"
        "  REQUIRES:\n    source: Concept\n    target: Concept\n"
        "    acyclic: true\n",
        encoding="utf-8",
    )

    result = FoundationCompiler().compile(tmp_path)

    assert result.success is False
    assert result.knowledge_model is not None

    # traverse() must terminate despite the cycle -- it guards on
    # "already visited", independent of the ontology's acyclic flag.
    visited = result.knowledge_model.query.traverse(
        "NUM-CON-000002", types=("REQUIRES",)
    )
    assert set(visited) == {"NUM-CON-000001"}
