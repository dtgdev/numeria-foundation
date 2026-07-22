"""Integration test: the Derivative learning journey, end to end.

Mirrors the real Canon's Constant/Variable -> Function -> Limit ->
Derivative REQUIRES chain (see `knowledge/relationships/` in the real
repo), driven the way `forge compile` / `forge learn` actually run it
-- a real `numeria.yaml` + `knowledge/` tree on disk, compiled through
`FoundationCompiler().compile()`, then `learning_path()` called
against the resulting `result.knowledge_model.query`.

Distinct from `tests/knowledge/test_query.py` (unit-level, a synthetic
fixture Canon, direct `CanonicalKnowledgeModel.build_from_root` calls)
and `tests/test_cli_learn.py` (CLI-level, via `CliRunner`): this is
the only test that exercises `learning_path()` through the actual
compiler pipeline, matching v0.16's `test_knowledge_model.py` /
v0.17's `test_knowledge_graph_export.py` in scope and intent.
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


def _write_numeria_yaml(root: Path) -> None:
    (root / "numeria.yaml").write_text(
        """
schema_version: "1.0"

foundation:
  id: derivative-learning-journey
  name: Derivative Learning Journey Fixture
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
  - packages/none
""".strip(),
        encoding="utf-8",
    )


def _build_derivative_journey(root: Path) -> None:
    """Constant, Variable -> Function -> Limit -> Derivative, plus a
    Character representing Derivative and a Lesson teaching it --
    the same shape as the real Canon's actual chain."""

    root.mkdir(parents=True, exist_ok=True)
    _write_numeria_yaml(root)

    knowledge_root = root / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Constant"),
        ("NUM-CON-000002", "Variable"),
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

    relationships = (
        ("NUM-REL-000001", "REQUIRES", "NUM-CON-000003", "Concept", "NUM-CON-000001", "Concept"),
        ("NUM-REL-000002", "REQUIRES", "NUM-CON-000003", "Concept", "NUM-CON-000002", "Concept"),
        ("NUM-REL-000003", "REQUIRES", "NUM-CON-000004", "Concept", "NUM-CON-000003", "Concept"),
        ("NUM-REL-000004", "REQUIRES", "NUM-CON-000005", "Concept", "NUM-CON-000004", "Concept"),
        ("NUM-REL-000005", "REPRESENTED_BY", "NUM-CON-000005", "Concept", "NUM-CHR-000001", "Character"),
        ("NUM-REL-000006", "TEACHES_CONCEPT", "NUM-LESSON-000001", "Lesson", "NUM-CON-000005", "Concept"),
    )

    for rel_id, rel_type, source_id, source_type, target_id, target_type in relationships:
        _write_entity(
            knowledge_root / "relationships" / rel_id,
            id=rel_id, type=rel_type, status="CANON", version="1.0.0",
            source={"id": source_id, "type": source_type},
            target={"id": target_id, "type": target_type},
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
  REPRESENTED_BY:
    source: Concept
    target: Character
  TEACHES_CONCEPT:
    source: Lesson
    target: Concept
""".strip(),
        encoding="utf-8",
    )


def test_derivative_learning_journey_end_to_end(tmp_path: Path) -> None:
    _build_derivative_journey(tmp_path)

    template_root = Path(__file__).resolve().parents[2] / "templates"
    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True
    assert result.knowledge_model is not None

    query = result.knowledge_model.query

    # The full learning path to Derivative, in order, ending with it.
    path = [entity.id for entity in query.learning_path("NUM-CON-000005")]
    assert path[-1] == "NUM-CON-000005"
    assert set(path) == {
        "NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003", "NUM-CON-000004",
        "NUM-CON-000005",
    }
    assert path.index("NUM-CON-000004") < path.index("NUM-CON-000005")  # Limit before Derivative
    assert path.index("NUM-CON-000003") < path.index("NUM-CON-000004")  # Function before Limit
    assert path.index("NUM-CON-000001") < path.index("NUM-CON-000003")  # Constant before Function
    assert path.index("NUM-CON-000002") < path.index("NUM-CON-000003")  # Variable before Function

    # A shorter path to an intermediate concept stops there.
    limit_path = [entity.id for entity in query.learning_path("NUM-CON-000004")]
    assert limit_path[-1] == "NUM-CON-000004"
    assert "NUM-CON-000005" not in limit_path

    # A leaf concept's path is just itself.
    assert [e.id for e in query.learning_path("NUM-CON-000001")] == ["NUM-CON-000001"]

    # learning_path() composes correctly with the rest of the query
    # API on the same model -- this isn't an isolated code path.
    prereqs = {e.id for e in query.prerequisites_of("NUM-CON-000005")}
    assert prereqs == set(path[:-1])

    represented_by = query.related("NUM-CON-000005", "REPRESENTED_BY")
    assert [e.id for e in represented_by] == ["NUM-CHR-000001"]

    taught_by = query.related(
        "NUM-CON-000005", "TEACHES_CONCEPT", direction="incoming"
    )
    assert [e.id for e in taught_by] == ["NUM-LESSON-000001"]


def test_derivative_learning_journey_is_deterministic(tmp_path: Path) -> None:
    """Same Canon compiled twice must produce the exact same learning
    path (Compiler Law #1) -- not just the same set of entities, the
    same order."""

    _build_derivative_journey(tmp_path)

    template_root = Path(__file__).resolve().parents[2] / "templates"
    first = FoundationCompiler(template_root=template_root).compile(tmp_path)
    second = FoundationCompiler(template_root=template_root).compile(tmp_path)

    first_path = [e.id for e in first.knowledge_model.query.learning_path("NUM-CON-000005")]
    second_path = [e.id for e in second.knowledge_model.query.learning_path("NUM-CON-000005")]

    assert first_path == second_path
