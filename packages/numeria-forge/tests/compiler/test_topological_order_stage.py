from pathlib import Path

import pytest
import yaml

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import DependencyGraphStage, LoadCanonStage
from numeria_forge.compiler.stages.topological_order import TopologicalOrderStage


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def write_ontology(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
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


def write_concepts_and_requires(tmp_path: Path, cyclic: bool) -> None:
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001-limit",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Limit",
    )
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000002-derivative",
        id="NUM-CON-000002",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
    )

    write_entity(
        tmp_path / "relationships" / "NUM-REL-000001",
        id="NUM-REL-000001",
        type="REQUIRES",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    if cyclic:
        write_entity(
            tmp_path / "relationships" / "NUM-REL-000002",
            id="NUM-REL-000002",
            type="REQUIRES",
            status="CANON",
            version="1.0.0",
            source={"id": "NUM-CON-000001", "type": "Concept"},
            target={"id": "NUM-CON-000002", "type": "Concept"},
        )

    write_ontology(tmp_path)


def _prepare_context(tmp_path: Path) -> CompilerContext:
    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    DependencyGraphStage().execute(context)
    return context


def test_requires_dependency_graph_stage_first(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)

    with pytest.raises(RuntimeError):
        TopologicalOrderStage().execute(context)


def test_orders_a_clean_dependency_chain(tmp_path: Path) -> None:
    write_concepts_and_requires(tmp_path, cyclic=False)
    context = _prepare_context(tmp_path)

    TopologicalOrderStage().execute(context)

    assert context.diagnostics == []
    assert set(context.topological_order) == {"NUM-CON-000001", "NUM-CON-000002"}
    assert context.topological_order.index(
        "NUM-CON-000002"
    ) < context.topological_order.index("NUM-CON-000001")


def test_cycle_records_an_error_diagnostic(tmp_path: Path) -> None:
    write_concepts_and_requires(tmp_path, cyclic=True)
    context = _prepare_context(tmp_path)

    TopologicalOrderStage().execute(context)

    assert context.success is False
    assert context.topological_order == ()
    codes = {d.code for d in context.diagnostics}
    assert "canon.semantics.dependency-cycle" in codes


def test_missing_ontology_file_leaves_empty_order(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001-limit",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Limit",
    )
    context = _prepare_context(tmp_path)

    TopologicalOrderStage().execute(context)

    assert context.diagnostics == []
    assert context.topological_order == ()
