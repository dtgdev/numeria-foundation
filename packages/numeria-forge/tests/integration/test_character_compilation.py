"""End-to-end compilation test for canonical characters."""

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
        description="A detective who solves mysteries using change.",
        personality=(
            "curious",
            "observant",
        ),
        superpower="Sees rates of change.",
        weakness="Needs enough evidence.",
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
            "origin": "numeria",
        },
    )


def test_character_compilation_pipeline(
    tmp_path: Path,
) -> None:
    """
    Verify the complete publishing pipeline.

    Character
        ↓
    Serializer
        ↓
    Publisher
        ↓
    character.yaml
    """

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

    expected_file = (
        tmp_path
        / "derivative"
        / "character.yaml"
    )

    assert expected_file.exists()

    document = yaml.safe_load(
        expected_file.read_text(
            encoding="utf-8",
        )
    )

    assert document == {
        "schema": "numeria.character.v1",
        "id": "NUM-CHR-000001",
        "version": "1.0.0",
        "status": "draft",
        "name": "Derivative",
        "title": "The Detective of Change",
        "slug": "derivative",
        "realm": "Realm of Change",
        "mathematical_concept": "derivative",
        "description": "A detective who solves mysteries using change.",
        "personality": [
            "curious",
            "observant",
        ],
        "superpower": "Sees rates of change.",
        "weakness": "Needs enough evidence.",
        "catchphrase": "Every change leaves a clue!",
        "learning_objectives": [
            "Understand derivatives.",
            "Recognize rates of change.",
        ],
        "age_range": "8-12",
        "tags": [
            "calculus",
            "change",
        ],
        "metadata": {
            "origin": "numeria",
        },
    }