"""Tests for CharacterYamlPublisher."""

from pathlib import Path

import pytest
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
        description="A detective who discovers how things change.",
        personality=(
            "curious",
            "observant",
        ),
        superpower="Sees rates of change.",
        weakness="Cannot solve a mystery without enough information.",
        catchphrase="Every change leaves a clue!",
        learning_objectives=(
            "Understand rate of change.",
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


def test_publisher_writes_character_yaml(
    tmp_path: Path,
) -> None:
    publisher = CharacterYamlPublisher()

    context = PublishContext(
        output_directory=tmp_path,
        metadata={},
    )

    result = publisher.publish(
        make_character(),
        context,
    )

    expected_path = (
        tmp_path
        / "derivative"
        / "character.yaml"
    )

    assert result.publisher == "character-yaml"
    assert result.path == expected_path
    assert result.media_type == "application/yaml"

    assert expected_path.exists()

    document = yaml.safe_load(
        expected_path.read_text(
            encoding="utf-8",
        )
    )

    assert document["schema"] == "numeria.character.v1"
    assert document["id"] == "NUM-CHR-000001"
    assert document["name"] == "Derivative"


def test_publisher_rejects_non_character(
    tmp_path: Path,
) -> None:
    publisher = CharacterYamlPublisher()

    context = PublishContext(
        output_directory=tmp_path,
        metadata={},
    )

    with pytest.raises(
        TypeError,
        match="requires a Character",
    ):
        publisher.publish(
            "Derivative",  # type: ignore[arg-type]
            context,
        )
