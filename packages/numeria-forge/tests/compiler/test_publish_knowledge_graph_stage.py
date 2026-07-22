from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stages import (
    BuildKnowledgeModelStage,
    DependencyGraphStage,
    LoadCanonStage,
    PublishKnowledgeGraphStage,
)


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _built_context(tmp_path: Path) -> CompilerContext:
    knowledge_root = tmp_path / "knowledge"
    _write_entity(
        knowledge_root / "concepts" / "limit",
        id="CON-LIMIT", type="Concept", status="CANON", version="1.0.0",
        name="Limit",
    )
    (knowledge_root / "ontology").mkdir(parents=True)
    (knowledge_root / "ontology" / "relationship-types.yaml").write_text(
        "version: '1.0.0'\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    context = CompilerContext(
        project_root=tmp_path, build_directory=tmp_path / "build"
    )
    LoadCanonStage(knowledge_root=knowledge_root).execute(context)
    DependencyGraphStage().execute(context)
    BuildKnowledgeModelStage().execute(context)
    return context


def test_requires_knowledge_model_to_have_been_built(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path, build_directory=tmp_path / "build"
    )

    with pytest.raises(RuntimeError, match="BuildKnowledgeModelStage"):
        PublishKnowledgeGraphStage().execute(context)


def test_requires_build_directory(tmp_path: Path) -> None:
    context = _built_context(tmp_path)
    context.build_directory = None

    with pytest.raises(RuntimeError, match="build_directory"):
        PublishKnowledgeGraphStage().execute(context)


def test_writes_all_three_export_formats(tmp_path: Path) -> None:
    context = _built_context(tmp_path)

    PublishKnowledgeGraphStage().execute(context)

    graph_dir = tmp_path / "build" / "graph"
    json_path = graph_dir / "knowledge.json"
    yaml_path = graph_dir / "knowledge.yaml"
    graphml_path = graph_dir / "knowledge.graphml"

    assert json_path.is_file()
    assert yaml_path.is_file()
    assert graphml_path.is_file()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["nodes"] == [{"id": "CON-LIMIT", "type": "Concept"}]

    assert yaml.safe_load(yaml_path.read_text(encoding="utf-8")) == data
    assert "<graphml" in graphml_path.read_text(encoding="utf-8")


def test_records_three_publish_results(tmp_path: Path) -> None:
    context = _built_context(tmp_path)

    PublishKnowledgeGraphStage().execute(context)

    publishers = {result.publisher for result in context.published_assets}
    assert publishers == {"publish-knowledge-graph"}
    assert len(context.published_assets) == 3


def test_overwrites_on_repeated_runs(tmp_path: Path) -> None:
    context = _built_context(tmp_path)

    PublishKnowledgeGraphStage().execute(context)
    PublishKnowledgeGraphStage().execute(context)

    graph_dir = tmp_path / "build" / "graph"
    assert (graph_dir / "knowledge.json").is_file()
    # Second run appended 3 more PublishResults on top of the first
    # run's 3 -- context accumulates across stage executions, same
    # behavior as PublishGeneratedAssetsStage.
    assert len(context.published_assets) == 6
