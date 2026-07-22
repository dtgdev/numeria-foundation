from pathlib import Path

from numeria_forge.domain.canon import Canon
from numeria_forge.semantics import CycleDetector, SemanticGraph

from .conftest import make_entity, requires_edge


def concept(entity_id: str):
    return make_entity(
        entity_id, "Concept", f"knowledge/concepts/{entity_id}/entity.yaml"
    )


def test_no_cycle_in_a_chain(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    canon.entities["NUM-REL-000002"] = requires_edge(
        "NUM-REL-000002", "NUM-CON-000002", "NUM-CON-000003"
    )

    graph = SemanticGraph.build_from_canon(canon)
    cycles = CycleDetector(graph).find_cycles(types=("REQUIRES",))

    assert cycles == ()
    assert CycleDetector(graph).has_cycle(types=("REQUIRES",)) is False


def test_direct_cycle_is_detected(tmp_path: Path) -> None:
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
    cycles = CycleDetector(graph).find_cycles(types=("REQUIRES",))

    assert len(cycles) == 1
    assert set(cycles[0].nodes) == {"NUM-CON-000001", "NUM-CON-000002"}
    assert str(cycles[0]) in (
        "NUM-CON-000001 -> NUM-CON-000002 -> NUM-CON-000001",
        "NUM-CON-000002 -> NUM-CON-000001 -> NUM-CON-000002",
    )


def test_indirect_three_node_cycle_is_detected(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003"):
        canon.entities[entity_id] = concept(entity_id)

    canon.entities["NUM-REL-000001"] = requires_edge(
        "NUM-REL-000001", "NUM-CON-000001", "NUM-CON-000002"
    )
    canon.entities["NUM-REL-000002"] = requires_edge(
        "NUM-REL-000002", "NUM-CON-000002", "NUM-CON-000003"
    )
    canon.entities["NUM-REL-000003"] = requires_edge(
        "NUM-REL-000003", "NUM-CON-000003", "NUM-CON-000001"
    )

    graph = SemanticGraph.build_from_canon(canon)
    detector = CycleDetector(graph)

    assert detector.has_cycle(types=("REQUIRES",)) is True
    cycles = detector.find_cycles(types=("REQUIRES",))
    assert len(cycles) == 1
    assert set(cycles[0].nodes) == {
        "NUM-CON-000001",
        "NUM-CON-000002",
        "NUM-CON-000003",
    }


def test_cycle_outside_requested_types_is_ignored(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)

    for entity_id in ("NUM-CON-000001", "NUM-CON-000002"):
        canon.entities[entity_id] = concept(entity_id)

    # FRIEND_OF cycle -- not in the acyclic type set we ask about.
    canon.entities["NUM-REL-000001"] = make_entity(
        "NUM-REL-000001",
        "FRIEND_OF",
        "knowledge/relationships/a/entity.yaml",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000002", "type": "Concept"},
    )
    canon.entities["NUM-REL-000002"] = make_entity(
        "NUM-REL-000002",
        "FRIEND_OF",
        "knowledge/relationships/b/entity.yaml",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    graph = SemanticGraph.build_from_canon(canon)
    cycles = CycleDetector(graph).find_cycles(types=("REQUIRES",))

    assert cycles == ()
