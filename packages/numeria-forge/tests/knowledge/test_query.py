from __future__ import annotations

from numeria_forge.knowledge.query import KnowledgeQuery


def test_get_returns_the_full_entity(model) -> None:
    entity = model.query.get("CON-DERIVATIVE")

    assert entity is not None
    assert entity.get("name") == "Derivative"


def test_get_returns_none_for_an_unknown_id(model) -> None:
    assert model.query.get("does-not-exist") is None


def test_entities_of_type_returns_every_concept(model) -> None:
    concepts = model.query.entities_of_type("Concept")

    assert {c.id for c in concepts} == {
        "CON-VARIABLE", "CON-CONSTANT", "CON-FUNCTION", "CON-LIMIT",
        "CON-DERIVATIVE",
    }


def test_related_outgoing_finds_the_represented_by_character(model) -> None:
    characters = model.query.related("CON-DERIVATIVE", "REPRESENTED_BY")

    assert [c.id for c in characters] == ["CHR-DETECTIVE"]


def test_related_incoming_finds_the_lesson_that_teaches_a_concept(model) -> None:
    lessons = model.query.related(
        "CON-DERIVATIVE", "TEACHES_CONCEPT", direction="incoming"
    )

    assert [l.id for l in lessons] == ["LESSON-INTRO"]


def test_related_returns_empty_tuple_for_no_match(model) -> None:
    assert model.query.related("CON-VARIABLE", "REPRESENTED_BY") == ()


def test_prerequisites_of_derivative_matches_the_full_requires_chain(model) -> None:
    prereqs = model.query.prerequisites_of("CON-DERIVATIVE")

    # Nearest first: Limit, then Function, then Function's own two
    # prerequisites (order among siblings is alphabetical by id --
    # CON-CONSTANT sorts before CON-VARIABLE).
    assert [p.id for p in prereqs] == [
        "CON-LIMIT", "CON-FUNCTION", "CON-CONSTANT", "CON-VARIABLE",
    ]


def test_prerequisites_of_a_leaf_concept_is_empty(model) -> None:
    assert model.query.prerequisites_of("CON-VARIABLE") == ()


def test_prerequisites_of_an_unknown_id_is_empty(model) -> None:
    assert model.query.prerequisites_of("does-not-exist") == ()


def test_traverse_respects_max_depth(model) -> None:
    one_hop = model.query.traverse(
        "CON-DERIVATIVE", types=("REQUIRES",), max_depth=1
    )
    assert one_hop == ("CON-LIMIT",)

    two_hops = model.query.traverse(
        "CON-DERIVATIVE", types=("REQUIRES",), max_depth=2
    )
    assert two_hops == ("CON-LIMIT", "CON-FUNCTION")


def test_traverse_is_cycle_safe_even_without_an_acyclic_declaration(model) -> None:
    # Build a graph with a genuine cycle among a *non*-acyclic
    # relationship type and confirm traverse() still terminates,
    # visiting each node exactly once.
    import dataclasses

    from numeria_forge.semantics.edge import GraphEdge

    cyclic_edges = model.graph.edges + (
        GraphEdge(id="X1", type="SEE_ALSO", source_id="CON-LIMIT", target_id="CON-DERIVATIVE"),
    )
    cyclic_graph = dataclasses.replace(model.graph, edges=cyclic_edges)
    query = KnowledgeQuery(
        canon=model.canon, graph=cyclic_graph, ontology=model.ontology
    )

    visited = query.traverse("CON-DERIVATIVE", types=("REQUIRES", "SEE_ALSO"))

    assert len(visited) == len(set(visited))  # no duplicates, no infinite loop
    assert "CON-DERIVATIVE" not in visited  # start node itself excluded
