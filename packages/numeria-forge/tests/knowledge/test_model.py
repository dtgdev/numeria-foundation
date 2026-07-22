from __future__ import annotations

from pathlib import Path

from numeria_forge.knowledge import CanonicalKnowledgeModel
from numeria_forge.knowledge.query import KnowledgeQuery


def test_build_from_root_loads_canon_graph_and_ontology(model) -> None:
    # Canon.entities includes relationship entities too (18 = 10
    # non-relationship entities + 8 relationships, since v0.19.0 added
    # a 3-scene FOLLOWS_SCENE chain alongside the original 7 + 6); the
    # graph only gets a node per non-relationship entity.
    assert len(model.canon) == 18
    assert len(model.graph) == 10
    assert "REQUIRES" in model.ontology
    assert "FOLLOWS_SCENE" in model.ontology
    assert isinstance(model.query, KnowledgeQuery)


def test_build_from_root_is_fail_open_on_a_missing_ontology(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    root.mkdir(parents=True)
    # No ontology/ subdirectory at all.

    model = CanonicalKnowledgeModel.build_from_root(root)

    assert model.ontology.types == {}
    assert model.query.prerequisites_of("anything") == ()


def test_len_reflects_canon_size(model) -> None:
    assert len(model) == len(model.canon)


def test_build_reuses_an_already_loaded_canon_and_ontology(model) -> None:
    # CanonicalKnowledgeModel.build() (not build_from_root) is what the
    # compiler pipeline uses -- it must not re-read anything from disk.
    rebuilt = CanonicalKnowledgeModel.build(model.canon, model.ontology)

    assert rebuilt.canon is model.canon
    assert rebuilt.ontology is model.ontology
    assert len(rebuilt.graph) == len(model.graph)
