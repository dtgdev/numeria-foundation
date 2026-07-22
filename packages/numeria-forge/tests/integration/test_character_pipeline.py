
"""End-to-end canonical character publishing pipeline."""

from pathlib import Path

import yaml

from numeria_forge.domain import Character

from numeria_forge.publishing import (

    CharacterYamlPublisher,

    PublishContext,

)

def test_character_pipeline(tmp_path: Path) -> None:

    """A canonical Character should publish to character.yaml."""

    character = Character(

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

        weakness="Needs enough clues.",

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

    publisher = CharacterYamlPublisher()

    context = PublishContext(

        output_directory=tmp_path,

        metadata={},

    )

    result = publisher.publish(

        character,

        context,

    )

    expected = (

        tmp_path

        / "derivative"

        / "character.yaml"

    )

    assert result.path == expected

    assert expected.exists()

    document = yaml.safe_load(

        expected.read_text(

            encoding="utf-8"

        )

    )

    assert document["schema"] == "numeria.character.v1"

    assert document["id"] == "NUM-CHR-000001"

    assert document["slug"] == "derivative"

    assert document["name"] == "Derivative"

    assert document["title"] == "The Detective of Change"

