"""End-to-end character publishing pipeline."""

from pathlib import Path

import yaml

from pathlib import Path

import yaml

from numeria_forge.domain.generated_character import GeneratedCharacter

from numeria_forge.domain.canon.character_factory import CharacterFactory

from numeria_forge.publishing import (

    CharacterYamlPublisher,

    PublishContext,

)


def test_character_pipeline(tmp_path: Path) -> None:
    generated = GeneratedCharacter(
        name="Derivative",
        mathematical_concept="derivative",
        description="A detective who studies change.",
        personality=(
            "curious",
            "analytical",
        ),
        superpower="Sees invisible rates of change.",
        weakness="Needs enough clues.",
        catchphrase="Every change leaves a clue!",
    )

    character = CharacterFactory().create(
        generated,
        character_id="NUM-CHR-000001",
    )

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

    assert document["id"] == "NUM-CHR-000001"
    assert document["slug"] == "derivative"
    assert document["name"] == "Derivative"
    assert (
        document["mathematical_concept"]
        == "derivative"
    )
    assert document["schema"] == "numeria.character.v1"
