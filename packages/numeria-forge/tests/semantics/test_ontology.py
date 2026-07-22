from pathlib import Path

import pytest

from numeria_forge.semantics.ontology import OntologyError, RelationshipOntology

from .conftest import ONTOLOGY_WITH_LEARNING_AND_STORY, write_ontology


def test_loads_types_with_source_target_symmetric_and_acyclic(tmp_path: Path) -> None:
    write_ontology(tmp_path)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    requires = ontology.get("REQUIRES")
    assert requires is not None
    assert requires.allowed_source_types == ("Concept",)
    assert requires.allowed_target_types == ("Concept",)
    assert requires.acyclic is True
    assert requires.symmetric is False

    friend_of = ontology.get("FRIEND_OF")
    assert friend_of is not None
    assert friend_of.symmetric is True
    assert friend_of.acyclic is False


def test_acyclic_type_names_returns_only_flagged_types(tmp_path: Path) -> None:
    write_ontology(tmp_path)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    assert ontology.acyclic_type_names() == ("REQUIRES",)


def test_unknown_type_returns_none(tmp_path: Path) -> None:
    write_ontology(tmp_path)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    assert ontology.get("NOT_A_REAL_TYPE") is None
    assert "NOT_A_REAL_TYPE" not in ontology
    assert "REQUIRES" in ontology


def test_missing_ontology_file_raises(tmp_path: Path) -> None:
    with pytest.raises(OntologyError):
        RelationshipOntology.load_from_knowledge_root(tmp_path)


def test_invalid_yaml_raises(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir(parents=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "relationship_types: [this, is, a, list, not, a, mapping]",
        encoding="utf-8",
    )

    with pytest.raises(OntologyError):
        RelationshipOntology.load_from_knowledge_root(tmp_path)


def test_list_source_is_supported(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir(parents=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        """
version: "1.0.0"
status: CANON

relationship_types:
  APPEARS_IN:
    source:
      - Character
      - Event
    target: Book
""".strip(),
        encoding="utf-8",
    )

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)
    appears_in = ontology.get("APPEARS_IN")

    assert appears_in is not None
    assert appears_in.allowed_source_types == ("Character", "Event")
    assert appears_in.allows("Character", "Book") is True
    assert appears_in.allows("Location", "Book") is False


def test_category_traversal_ordered_and_transitive_are_parsed(tmp_path: Path) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    requires = ontology.get("REQUIRES")
    assert requires is not None
    assert requires.category == "learning"
    assert requires.traversal == "learning"
    assert requires.ordered is False

    follows_scene = ontology.get("FOLLOWS_SCENE")
    assert follows_scene is not None
    assert follows_scene.category == "narrative"
    assert follows_scene.traversal == "story"
    assert follows_scene.ordered is True


def test_category_and_traversal_default_to_empty_string(tmp_path: Path) -> None:
    write_ontology(tmp_path)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    friend_of = ontology.get("FRIEND_OF")
    assert friend_of is not None
    assert friend_of.category == ""
    assert friend_of.traversal == ""
    assert friend_of.ordered is False
    assert friend_of.transitive is False


def test_acyclic_type_names_with_no_filter_returns_every_acyclic_type(
    tmp_path: Path,
) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    assert set(ontology.acyclic_type_names()) == {"REQUIRES", "FOLLOWS_SCENE"}


def test_acyclic_type_names_scoped_by_traversal(tmp_path: Path) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)

    ontology = RelationshipOntology.load_from_knowledge_root(tmp_path)

    assert ontology.acyclic_type_names(traversal="learning") == ("REQUIRES",)
    assert ontology.acyclic_type_names(traversal="story") == ("FOLLOWS_SCENE",)
    assert ontology.acyclic_type_names(traversal="does-not-exist") == ()
