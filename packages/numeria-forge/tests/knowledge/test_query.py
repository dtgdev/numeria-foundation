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


def test_learning_path_is_prerequisites_first_ending_with_the_target(
    model,
) -> None:
    # Kahn's algorithm's exact tie-break order between two
    # independent siblings (Variable and Constant, neither requiring
    # the other) is an implementation detail, not a contract -- so
    # this asserts the invariants a learning path actually promises,
    # rather than one specific total order among ties.
    path = [e.id for e in model.query.learning_path("CON-DERIVATIVE")]

    assert path[-1] == "CON-DERIVATIVE"
    assert set(path) == {
        "CON-CONSTANT", "CON-VARIABLE", "CON-FUNCTION", "CON-LIMIT",
        "CON-DERIVATIVE",
    }
    # Every direct REQUIRES edge must be respected: prerequisite
    # before dependent.
    assert path.index("CON-LIMIT") < path.index("CON-DERIVATIVE")
    assert path.index("CON-FUNCTION") < path.index("CON-LIMIT")
    assert path.index("CON-VARIABLE") < path.index("CON-FUNCTION")
    assert path.index("CON-CONSTANT") < path.index("CON-FUNCTION")


def test_learning_path_for_a_leaf_concept_is_just_itself(model) -> None:
    path = model.query.learning_path("CON-VARIABLE")

    assert [e.id for e in path] == ["CON-VARIABLE"]


def test_learning_path_for_an_intermediate_concept_stops_there(model) -> None:
    path = [e.id for e in model.query.learning_path("CON-LIMIT")]

    assert path[-1] == "CON-LIMIT"
    assert set(path) == {"CON-CONSTANT", "CON-VARIABLE", "CON-FUNCTION", "CON-LIMIT"}
    assert "CON-DERIVATIVE" not in path
    assert path.index("CON-FUNCTION") < path.index("CON-LIMIT")
    assert path.index("CON-VARIABLE") < path.index("CON-FUNCTION")
    assert path.index("CON-CONSTANT") < path.index("CON-FUNCTION")


def test_learning_path_for_an_unknown_id_is_empty(model) -> None:
    assert model.query.learning_path("does-not-exist") == ()


def test_learning_path_is_empty_when_ontology_declares_no_acyclic_type(
    tmp_path,
) -> None:
    from numeria_forge.knowledge import CanonicalKnowledgeModel

    root = tmp_path / "knowledge"
    (root / "concepts" / "a").mkdir(parents=True)
    (root / "concepts" / "a" / "entity.yaml").write_text(
        "id: CON-A\ntype: Concept\nstatus: CANON\nversion: '1.0.0'\nname: A\n",
        encoding="utf-8",
    )
    (root / "ontology").mkdir(parents=True)
    (root / "ontology" / "relationship-types.yaml").write_text(
        "version: '1.0.0'\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    no_ontology_model = CanonicalKnowledgeModel.build_from_root(root)

    # No acyclic type declared -- learning_path can't order anything,
    # but a lone node with no prerequisites is still just itself.
    assert [e.id for e in no_ontology_model.query.learning_path("CON-A")] == ["CON-A"]


def test_learning_path_is_empty_on_a_genuine_cycle(model) -> None:
    import dataclasses

    from numeria_forge.knowledge.query import KnowledgeQuery
    from numeria_forge.semantics.edge import GraphEdge

    # Force a REQUIRES cycle: Variable now (incorrectly) requires
    # Derivative, closing a loop back through the existing chain.
    cyclic_edges = model.graph.edges + (
        GraphEdge(
            id="REL-CYCLE", type="REQUIRES",
            source_id="CON-VARIABLE", target_id="CON-DERIVATIVE",
        ),
    )
    cyclic_graph = dataclasses.replace(model.graph, edges=cyclic_edges)
    query = KnowledgeQuery(canon=model.canon, graph=cyclic_graph, ontology=model.ontology)

    assert query.learning_path("CON-DERIVATIVE") == ()


def test_traverse_respects_max_depth(model) -> None:
    one_hop = model.query.traverse(
        "CON-DERIVATIVE", types=("REQUIRES",), max_depth=1
    )
    assert one_hop == ("CON-LIMIT",)

    two_hops = model.query.traverse(
        "CON-DERIVATIVE", types=("REQUIRES",), max_depth=2
    )
    assert two_hops == ("CON-LIMIT", "CON-FUNCTION")


def test_orphaned_entities_finds_untouched_nodes(model) -> None:
    # The fixture Canon connects every entity to at least one
    # relationship, so orphaned_entities() is empty by default; add
    # one deliberately unconnected Concept and confirm it's found.
    import dataclasses

    from numeria_forge.domain.canon.entity import CanonEntity
    from numeria_forge.semantics.node import GraphNode
    from pathlib import Path

    lonely = CanonEntity(
        id="CON-LONELY", type="Concept",
        source_path=Path("knowledge/concepts/lonely/entity.yaml"),
        data={"id": "CON-LONELY", "type": "Concept", "name": "Lonely"},
    )
    canon = dataclasses.replace(
        model.canon, entities={**model.canon.entities, "CON-LONELY": lonely}
    )
    graph = dataclasses.replace(
        model.graph,
        nodes={**model.graph.nodes, "CON-LONELY": GraphNode(id="CON-LONELY", type="Concept")},
    )
    query = KnowledgeQuery(canon=canon, graph=graph, ontology=model.ontology)

    orphans = query.orphaned_entities()

    assert [e.id for e in orphans] == ["CON-LONELY"]


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


def test_story_path_is_earliest_first_ending_with_the_target(model) -> None:
    path = model.query.story_path("SCN-CLIMAX")

    assert [e.id for e in path] == ["SCN-OPENING", "SCN-MIDDLE", "SCN-CLIMAX"]


def test_story_path_for_the_opening_scene_is_just_itself(model) -> None:
    path = model.query.story_path("SCN-OPENING")

    assert [e.id for e in path] == ["SCN-OPENING"]


def test_story_path_for_an_unknown_id_is_empty(model) -> None:
    assert model.query.story_path("SCN-DOES-NOT-EXIST") == ()


def test_learning_path_and_story_path_stay_scoped_to_their_own_traversal(model) -> None:
    # Both REQUIRES (traversal="learning") and FOLLOWS_SCENE
    # (traversal="story") are acyclic in this fixture's ontology at
    # the same time. Before v0.19.0's traversal scoping, both
    # `.learning_path` and `.story_path` were driven by *every*
    # acyclic-declared type combined, which would mix Concepts and
    # Scenes into one meaningless topological order. Confirm each
    # stays scoped to only its own relationship type.
    learning = model.query.learning_path("CON-DERIVATIVE")
    story = model.query.story_path("SCN-CLIMAX")

    assert all(e.type == "Concept" for e in learning)
    assert all(e.type == "Scene" for e in story)

    # And the unscoped combination is still available for consumers
    # that genuinely want it (DependencyGraphValidator's cycle check).
    assert set(model.ontology.acyclic_type_names()) == {"REQUIRES", "FOLLOWS_SCENE"}
    assert model.ontology.acyclic_type_names(traversal="learning") == ("REQUIRES",)
    assert model.ontology.acyclic_type_names(traversal="story") == ("FOLLOWS_SCENE",)


def test_prerequisites_of_does_not_cross_into_the_story_traversal(model) -> None:
    # CON-DERIVATIVE and SCN-* are disjoint node sets, but this proves
    # prerequisites_of() only ever considers REQUIRES, never
    # FOLLOWS_SCENE, even though both are acyclic in this fixture.
    prerequisites = model.query.prerequisites_of("CON-DERIVATIVE")

    assert all(e.type == "Concept" for e in prerequisites)
