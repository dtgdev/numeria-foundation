from __future__ import annotations

from numeria_forge.knowledge.statistics import GraphStatistics


def test_from_model_counts_nodes_edges_and_orphans(model) -> None:
    stats = GraphStatistics.from_model(model)

    assert stats.node_count == len(model.graph)
    assert stats.edge_count == len(model.graph.edges)
    assert stats.orphaned_node_count == len(model.graph.orphaned_node_ids())
    assert stats.acyclic_relationship_types == ("REQUIRES",)


def test_edge_type_counts_sums_correctly(model) -> None:
    stats = GraphStatistics.from_model(model)

    assert sum(stats.edge_type_counts.values()) == stats.edge_count
    # The fixture Canon has 4 REQUIRES edges (Function->Variable,
    # Function->Constant, Limit->Function, Derivative->Limit).
    assert stats.edge_type_counts["REQUIRES"] == 4


def test_to_dict_is_json_shaped(model) -> None:
    stats = GraphStatistics.from_model(model)
    data = stats.to_dict()

    assert data["node_count"] == stats.node_count
    assert data["acyclic_relationship_types"] == ["REQUIRES"]
    assert isinstance(data["edge_type_counts"], dict)


def test_default_construction_is_all_zero() -> None:
    stats = GraphStatistics()

    assert stats.node_count == 0
    assert stats.edge_count == 0
    assert stats.edge_type_counts == {}
    assert stats.orphaned_node_count == 0
    assert stats.acyclic_relationship_types == ()
