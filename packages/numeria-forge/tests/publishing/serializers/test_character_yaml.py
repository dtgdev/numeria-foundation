"""Tests for CharacterYamlSerializer."""

import pytest

from numeria_forge.domain import Character
from numeria_forge.publishing import CharacterYamlSerializer


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
        personality=("curious", "observant"),
        superpower="Sees rates of change.",
        weakness="Cannot solve a mystery without enough information.",
        catchphrase="Every change leaves a clue!",
        learning_objectives=(
            "Understand rate of change.",
            "Recognize derivatives in motion and growth.",
        ),
        age_range="8-12",
        tags=("calculus", "change"),
        metadata={"origin": "numeria"},
    )


def test_serializer_returns_canonical_document() -> None:
    serializer = CharacterYamlSerializer()

    document = serializer.to_dict(make_character())

    assert document["schema"] == "numeria.character.v1"
    assert document["id"] == "NUM-CHR-000001"
    assert document["slug"] == "derivative"
    assert document["name"] == "Derivative"
    assert document["personality"] == [
        "curious",
        "observant",
    ]
    assert document["learning_objectives"] == [
        "Understand rate of change.",
        "Recognize derivatives in motion and growth.",
    ]
    assert document["metadata"] == {
        "origin": "numeria",
    }


def test_serializer_rejects_non_character() -> None:
    serializer = CharacterYamlSerializer()

    with pytest.raises(
        TypeError,
        match="requires a Character",
    ):
        serializer.to_dict("Derivative")  # type: ignore[arg-type]
