"""Integration test for v0.17.0's additions: graph export, graph
statistics, and orphan detection, driven the way `forge compile`
actually runs them -- a real `numeria.yaml` + `knowledge/` tree on
disk, compiled through `FoundationCompiler().compile()`.

Distinct from `tests/knowledge/test_export.py` /
`test_statistics.py` (unit-level, build a `CanonicalKnowledgeModel`
directly) and `tests/compiler/test_publish_knowledge_graph_stage.py`
(the stage in isolation): this proves the whole v0.17.0 slice --
BuildKnowledgeModelStage -> PublishKnowledgeGraphStage -> the
CompilationReport's graph_statistics -- connects end to end.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from numeria_forge.compiler import FoundationCompiler


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _write_relationship(directory: Path, **fields: object) -> None:
    _write_entity(directory, **fields)


def _build_canon_with_one_orphan(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "numeria.yaml").write_text(
        """
schema_version: "1.0"

foundation:
  id: v017-fixture
  name: v0.17 Fixture
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
  - packages/none
""".strip(),
        encoding="utf-8",
    )

    knowledge_root = root / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Function"),
        ("NUM-CON-000002", "Variable"),
        ("NUM-CON-000003", "Isolated"),  # deliberately orphaned
    ):
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id, type="Concept", status="CANON", version="1.0.0",
            name=name,
        )

    _write_relationship(
        knowledge_root / "relationships" / "NUM-REL-000001",
        id="NUM-REL-000001", type="REQUIRES", status="CANON", version="1.0.0",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000002", "type": "Concept"},
    )

    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: '1.0.0'\nstatus: CANON\nrelationship_types:\n"
        "  REQUIRES:\n    source: Concept\n    target: Concept\n"
        "    acyclic: true\n",
        encoding="utf-8",
    )


def test_graph_export_report_and_orphan_detection_through_the_real_pipeline(
    tmp_path: Path,
) -> None:
    _build_canon_with_one_orphan(tmp_path)

    template_root = Path(__file__).resolve().parents[2] / "templates"
    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True

    # 1. build/graph/ export files, matching the in-memory model.
    graph_dir = tmp_path / "build" / "graph"
    json_data = json.loads((graph_dir / "knowledge.json").read_text(encoding="utf-8"))
    yaml_data = yaml.safe_load((graph_dir / "knowledge.yaml").read_text(encoding="utf-8"))
    assert json_data == yaml_data
    assert len(json_data["nodes"]) == 3
    assert len(json_data["edges"]) == 1
    assert "<graphml" in (graph_dir / "knowledge.graphml").read_text(encoding="utf-8")

    # 2. CompilationReport.graph_statistics, both via .to_dict() and
    # the human-readable summary.
    stats = result.report.graph_statistics
    assert stats is not None
    assert stats.node_count == 3
    assert stats.edge_count == 1
    assert stats.orphaned_node_count == 1
    assert stats.acyclic_relationship_types == ("REQUIRES",)
    assert "Knowledge graph: 3 node(s), 1 edge(s), 1 orphaned entity." in (
        result.report.format_human_readable()
    )

    # 3. The orphan is queryable directly off the first-class
    # knowledge_model too, not just the report's summary count.
    orphans = result.knowledge_model.query.orphaned_entities()
    assert [e.id for e in orphans] == ["NUM-CON-000003"]
