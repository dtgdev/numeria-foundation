"""End-to-end test for the Character publishing pipeline."""

from pathlib import Path

import yaml

from numeria_forge.domain import Character
from numeria_forge.publishing import (
    CharacterYamlPublisher,
    PublishContext,
)


def make_character() -> Character:
    return Character(
        id="NUM-CHR-000001",
        slug="derivative",
        version="1.0.0",
        status="draft",
        name="Derivative",
        title="The Detective of Change",
        mathematical_concept="derivative",
        realm="Realm of Change",
        description="A detective who solves the mysteries of change.",
        personality=(
            "curious",
            "observant",
            "brave",
        ),
        superpower="Sees how everything changes.",
        weakness="Needs enough clues before reaching a conclusion.",
        catchphrase="Every change leaves a clue!",
        learning_objectives=(
            "Understand rates of change.",
            "Recognize derivatives in real life.",
        ),
        age_range="8-12",
        tags=(
            "calculus",
            "change",
        ),
        metadata={
            "created_by": "integration-test",
        },
    )


def test_character_publish_pipeline(
    tmp_path: Path,
) -> None:
    character = make_character()

    publisher = CharacterYamlPublisher()

    context = PublishContext(
        output_directory=tmp_path,
        metadata={},
    )

    result = publisher.publish(
        character,
        context,
    )

    assert result.path.exists()

    document = yaml.safe_load(
        result.path.read_text(
            encoding="utf-8",
        )
    )

    assert document["schema"] == "numeria.character.v1"
    assert document["id"] == "NUM-CHR-000001"
    assert document["slug"] == "derivative"
    assert document["name"] == "Derivative"
    assert document["title"] == "The Detective of Change"
    assert (
        document["mathematical_concept"]
        == "derivative"
    )
    assert document["realm"] == "Realm of Change"
    assert document["personality"] == [
        "curious",
        "observant",
        "brave",
    ]
    assert document["learning_objectives"] == [
        "Understand rates of change.",
        "Recognize derivatives in real life.",
    ]
