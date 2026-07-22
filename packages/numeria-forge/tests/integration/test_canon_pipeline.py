"""End-to-end Canon publishing pipeline."""

from pathlib import Path

import yaml

from numeria_forge.domain import CharacterFactory
from numeria_forge.domain import GeneratedCharacter
from numeria_forge.publishing import (
    CharacterYamlPublisher,
    PublishContext,
)


def test_end_to_end_character_pipeline(
    tmp_path: Path,
) -> None:
    generated = GeneratedCharacter(
        name="Derivative",
        mathematical_concept="derivative",
        description="A detective who solves mysteries using change.",
        personality=[
            "curious",
            "brave",
        ],
        superpower="Sees instantaneous change.",
        weakness="Needs enough clues.",
        catchphrase="Every change leaves a clue!",
    )

    character = CharacterFactory().create(
        generated=generated,
        character_id="NUM-CHR-000001",
    )

    publisher = CharacterYamlPublisher()

    result = publisher.publish(
        character,
        PublishContext(
            output_directory=tmp_path,
            metadata={},
        ),
    )

    assert result.path.exists()

    document = yaml.safe_load(
        result.path.read_text(
            encoding="utf-8",
        )
    )

    assert document["id"] == "NUM-CHR-000001"
    assert document["slug"] == "derivative"
    assert document["name"] == "Derivative"
    assert document["schema"] == "numeria.character.v1"
