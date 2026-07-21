"""End-to-end compilation test for a canonical character."""

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
        mathematical_concept="Derivative",
        realm="Realm of Change",
        description="A detective who discovers how things change.",
        personality=("curious", "observant"),
        superpower="Sees rates of change.",
        weakness="Needs enough clues.",
        catchphrase="Every change leaves a clue!",
        learning_objectives=(
            "Understand derivatives.",
        ),
        age_range="8-12",
        tags=("calculus",),
        metadata={"origin": "numeria"},
    )


def test_compile_character(tmp_path: Path) -> None:

    publisher = CharacterYamlPublisher()

    context = PublishContext(
        output_directory=tmp_path / "canon" / "characters",
        metadata={},
    )

    result = publisher.publish(
        make_character(),
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

    assert document["name"] == "Derivative"

    assert document["slug"] == "derivative"

    assert (
        tmp_path
        / "canon"
        / "characters"
        / "derivative"
        / "character.yaml"
    ) == result.path
