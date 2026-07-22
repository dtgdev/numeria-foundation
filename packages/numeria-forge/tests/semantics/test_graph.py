from pathlib import Path

from numeria_forge.domain.canon import Canon
from numeria_forge.semantics import SemanticGraph

from .conftest import make_entity, requires_edge


def build_canon(tmp_path: Path) -> Canon:
    canon = Canon(root=tmp_path)

    canon.entities["NUM-CON-000001"] = make_entity(
        "NUM-CON-000001", "Concept", "knowledge/concepts/a/entity.yaml", name="A"
    )
    canon.entities["NUM-CON-000002"] = make_entity(
        "NUM-CON-000002", "Concept", "knowledge/concepts/b/entity.yaml", name="B"
    )
    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )

    return canon


def test_build_from_canon_creates_one_node_per_non_relationship_entity(
    tmp_path: Path,
) -> None:
    canon = build_canon(tmp_path)

    graph = SemanticGraph.build_from_canon(canon)

    assert len(graph) == 2
    assert "NUM-CON-000001" in graph
    assert "NUM-CON-000002" in graph
    assert "NUM-REL-000001" not in graph


def test_build_from_canon_creates_one_edge_per_relationship(tmp_path: Path) -> None:
    canon = build_canon(tmp_path)

    graph = SemanticGraph.build_from_canon(canon)

    assert len(graph.edges) == 1
    edge = graph.edges[0]
    assert edge.id == "NUM-REL-000001"
    assert edge.type == "REQUIRES"
    assert edge.source_id == "NUM-CON-000001"
    assert edge.target_id == "NUM-CON-000002"


def test_edges_with_missing_endpoints_are_skipped(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)
    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "REQUIRES",
        "knowledge/relationships/a/entity.yaml",
        source={},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    graph = SemanticGraph.build_from_canon(canon)

    assert graph.edges == ()


def test_outgoing_filters_by_type(tmp_path: Path) -> None:
    canon = build_canon(tmp_path)
    canon.entities["NUM-REL-000002"] = make_entity(
        "NUM-REL-000002",
        "FRIEND_OF",
        "knowledge/relationships/b/entity.yaml",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000002", "type": "Concept"},
    )

    graph = SemanticGraph.build_from_canon(canon)

    all_edges = graph.outgoing("NUM-CON-000001")
    assert len(all_edges) == 2

    requires_only = graph.outgoing("NUM-CON-000001", types=("REQUIRES",))
    assert len(requires_only) == 1
    assert requires_only[0].type == "REQUIRES"


def test_adjacency_only_includes_edges_with_known_endpoints(tmp_path: Path) -> None:
    canon = build_canon(tmp_path)

    graph = SemanticGraph.build_from_canon(canon)
    adjacency = graph.adjacency()

    assert adjacency == {"NUM-CON-000001": ("NUM-CON-000002",)}
