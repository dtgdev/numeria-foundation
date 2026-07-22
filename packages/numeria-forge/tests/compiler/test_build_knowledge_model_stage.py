from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stages import (
    BuildKnowledgeModelStage,
    DependencyGraphStage,
    LoadCanonStage,
)
from numeria_forge.knowledge import CanonicalKnowledgeModel


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _context_with_loaded_canon(tmp_path: Path) -> CompilerContext:
    knowledge_root = tmp_path / "knowledge"
    _write_entity(
        knowledge_root / "concepts" / "limit",
        id="CON-LIMIT", type="Concept", status="CANON", version="1.0.0",
        name="Limit",
    )
    (knowledge_root / "ontology").mkdir(parents=True)
    (knowledge_root / "ontology" / "relationship-types.yaml").write_text(
        "version: '1.0.0'\nstatus: CANON\nrelationship_types:\n"
        "  REQUIRES:\n    source: Concept\n    target: Concept\n    acyclic: true\n",
        encoding="utf-8",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=knowledge_root).execute(context)
    return context


def test_requires_load_canon_stage_to_have_run(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)

    with pytest.raises(RuntimeError, match="LoadCanonStage"):
        BuildKnowledgeModelStage().execute(context)


def test_requires_dependency_graph_stage_to_have_run(tmp_path: Path) -> None:
    context = _context_with_loaded_canon(tmp_path)

    with pytest.raises(RuntimeError, match="DependencyGraphStage"):
        BuildKnowledgeModelStage().execute(context)


def test_builds_a_knowledge_model_reusing_the_existing_canon_and_graph(
    tmp_path: Path,
) -> None:
    context = _context_with_loaded_canon(tmp_path)
    DependencyGraphStage().execute(context)

    BuildKnowledgeModelStage().execute(context)

    assert isinstance(context.knowledge_model, CanonicalKnowledgeModel)
    assert context.knowledge_model.canon is context.loaded_canon
    assert context.knowledge_model.graph is context.semantic_graph
    assert "REQUIRES" in context.knowledge_model.ontology


def test_is_fail_open_on_a_missing_ontology_file(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    _write_entity(
        knowledge_root / "concepts" / "limit",
        id="CON-LIMIT", type="Concept", status="CANON", version="1.0.0",
        name="Limit",
    )
    # Deliberately no ontology/ directory.

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=knowledge_root).execute(context)
    DependencyGraphStage().execute(context)

    BuildKnowledgeModelStage().execute(context)

    assert context.knowledge_model.ontology.types == {}
