from pathlib import Path

import pytest

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import DependencyGraphStage, LoadCanonStage


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def test_requires_loaded_canon(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)

    with pytest.raises(RuntimeError):
        DependencyGraphStage().execute(context)


def test_builds_graph_from_loaded_canon(tmp_path: Path) -> None:
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

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    DependencyGraphStage().execute(context)

    assert context.semantic_graph is not None
    assert len(context.semantic_graph) == 2
    assert context.semantic_graph.edges == ()
