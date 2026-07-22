from pathlib import Path

import pytest

from numeria_forge.domain.canon import Canon
from numeria_forge.semantics import SemanticGraph, TopologicalSortError, topological_sort

from .conftest import make_entity, requires_edge


def concept(entity_id: str):
    return make_entity(
        entity_id, "Concept", f"knowledge/concepts/{entity_id}/entity.yaml"
    )


def test_orders_a_chain_correctly(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003"):
        canon.entities[entity_id] = concept(entity_id)

    # NUM-CON-000001 REQUIRES NUM-CON-000002 REQUIRES NUM-CON-000003
    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    canon.entities["NUM-REL-000002"] = requires_edge(
        "NUM-REL-000002", "NUM-CON-000002", "NUM-CON-000003"
    )

    graph = SemanticGraph.build_from_canon(canon)
    order = topological_sort(graph, types=("REQUIRES",))

    assert len(order) == 3
    assert order.index("NUM-CON-000001") < order.index("NUM-CON-000002")
    assert order.index("NUM-CON-000002") < order.index("NUM-CON-000003")


def test_isolated_nodes_are_included(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    graph = SemanticGraph.build_from_canon(canon)
    order = topological_sort(graph, types=("REQUIRES",))

    assert set(order) == {"NUM-CON-000001", "NUM-CON-000002"}


def test_result_is_deterministic(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000003", "NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    graph = SemanticGraph.build_from_canon(canon)

    order_a = topological_sort(graph, types=("REQUIRES",))
    order_b = topological_sort(graph, types=("REQUIRES",))

    assert order_a == order_b == ("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003")


def test_cycle_raises_with_the_cycle_attached(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    canon.entities["NUM-REL-000002"] = requires_edge(
        "NUM-REL-000002", "NUM-CON-000002", "NUM-CON-000001"
    )

    graph = SemanticGraph.build_from_canon(canon)

    with pytest.raises(TopologicalSortError) as excinfo:
        topological_sort(graph, types=("REQUIRES",))

    assert len(excinfo.value.cycles) == 1
    assert set(excinfo.value.cycles[0].nodes) == {"NUM-CON-000001", "NUM-CON-000002"}
