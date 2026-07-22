from pathlib import Path

from numeria_forge.diagnostics import Severity
from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.validation import ValidationContext
from numeria_forge.semantics import StoryValidator

from .conftest import ONTOLOGY_WITH_LEARNING_AND_STORY, follows_scene_edge, make_entity, write_ontology


def scene(entity_id: str):
    return make_entity(
        entity_id, "Scene", f"knowledge/scenes/{entity_id}/entity.yaml"
    )


def test_a_clean_linear_chain_passes(tmp_path: Path) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)
    canon = Canon(root=tmp_path)

    for entity_id in ("SCN-A", "SCN-B", "SCN-C"):
        canon.entities[entity_id] = scene(entity_id)

    canon.entities["REL-1"] = follows_scene_edge("REL-1", "SCN-B", "SCN-A")
    canon.entities["REL-2"] = follows_scene_edge("REL-2", "SCN-C", "SCN-B")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_a_two_cycle_has_no_beginning_and_no_ending(tmp_path: Path) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)
    canon = Canon(root=tmp_path)

    for entity_id in ("SCN-A", "SCN-B"):
        canon.entities[entity_id] = scene(entity_id)

    canon.entities["REL-1"] = follows_scene_edge("REL-1", "SCN-A", "SCN-B")
    canon.entities["REL-2"] = follows_scene_edge("REL-2", "SCN-B", "SCN-A")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    # WARNING, not ERROR -- the cycle itself is DependencyGraphValidator's
    # job to fail the build; this validator only flags the missing
    # beginning/ending structure.
    assert result.success
    messages = [d.message for d in result.diagnostics]
    assert len(messages) == 2
    assert any("no beginning" in m for m in messages)
    assert any("no ending" in m for m in messages)
    assert all(d.severity is Severity.WARNING for d in result.diagnostics)


def test_two_separate_clean_chains_both_pass(tmp_path: Path) -> None:
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)
    canon = Canon(root=tmp_path)

    for entity_id in ("SCN-A", "SCN-B", "SCN-X", "SCN-Y"):
        canon.entities[entity_id] = scene(entity_id)

    canon.entities["REL-1"] = follows_scene_edge("REL-1", "SCN-B", "SCN-A")
    canon.entities["REL-2"] = follows_scene_edge("REL-2", "SCN-Y", "SCN-X")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_scenes_untouched_by_follows_scene_are_out_of_scope(tmp_path: Path) -> None:
    # A lone Scene with no FOLLOWS_SCENE edge at all is not part of any
    # component this validator considers -- OrphanedEntityValidator's
    # job, not this one's.
    write_ontology(tmp_path, ONTOLOGY_WITH_LEARNING_AND_STORY)
    canon = Canon(root=tmp_path)
    canon.entities["SCN-LONELY"] = scene("SCN-LONELY")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_missing_ontology_file_is_silently_skipped(tmp_path: Path) -> None:
    canon = Canon(root=tmp_path)
    canon.entities["SCN-A"] = scene("SCN-A")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_an_ontology_with_no_story_traversal_type_reports_nothing(
    tmp_path: Path,
) -> None:
    # The default shared fixture ontology only declares REQUIRES
    # (traversal="learning") -- no traversal="story" type at all.
    write_ontology(tmp_path)
    canon = Canon(root=tmp_path)
    canon.entities["SCN-A"] = scene("SCN-A")

    result = StoryValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()
