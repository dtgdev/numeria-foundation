"""End-to-end publishing pipeline test."""

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
        description="A detective who solves mysteries by studying change.",
        personality=(
            "curious",
            "observant",
            "persistent",
        ),
        superpower="Sees how everything changes.",
        weakness="Needs enough clues before drawing conclusions.",
        catchphrase="Every change leaves a clue!",
        learning_objectives=(
            "Understand derivatives.",
            "Recognize rates of change.",
        ),
        age_range="8-12",
        tags=(
            "calculus",
            "change",
        ),
        metadata={
            "source": "integration-test",
        },
    )


def test_publish_character_pipeline(
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

    assert result.publisher == "character-yaml"

    output_file = (
        tmp_path
        / "derivative"
        / "character.yaml"
    )

    assert output_file.exists()

    document = yaml.safe_load(
        output_file.read_text(
            encoding="utf-8",
        )
    )

    assert document["schema"] == "numeria.character.v1"
    assert document["id"] == character.id
    assert document["slug"] == character.slug
    assert document["name"] == character.name
    assert document["realm"] == character.realm
    assert document["mathematical_concept"] == (
        character.mathematical_concept
    )
    assert document["superpower"] == (
        character.superpower
    )
    assert document["weakness"] == (
        character.weakness
    )
    assert document["catchphrase"] == (
        character.catchphrase
    )
    assert document["metadata"]["source"] == (
        "integration-test"
    )
