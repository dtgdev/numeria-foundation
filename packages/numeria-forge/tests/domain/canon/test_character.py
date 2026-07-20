import pytest

from numeria_forge.domain import Character


def create_character(
    **overrides: object,
) -> Character:
    values = {
        "id": "NUM-CHR-000001",
        "slug": "derivative",
        "version": "1.0.0",
        "name": "Derivative",
        "title": "Detective of Change",
        "mathematical_concept": "Derivative",
        "realm": "Calculus",
        "description": (
            "A curious explorer who investigates change."
        ),
        "personality": (
            "Curious",
            "Brave",
            "Observant",
        ),
        "superpower": (
            "Reveals instantaneous rates of change."
        ),
        "weakness": (
            "Needs enough information to detect change."
        ),
        "catchphrase": (
            "Every change leaves a clue!"
        ),
    }

    values.update(overrides)

    return Character(**values)  # type: ignore[arg-type]


def test_character_accepts_valid_canon() -> None:
    character = create_character()

    assert character.id == "NUM-CHR-000001"
    assert character.slug == "derivative"
    assert character.status == "draft"


def test_character_rejects_invalid_id() -> None:
    with pytest.raises(
        ValueError,
        match="Character id",
    ):
        create_character(
            id="derivative",
        )


def test_character_requires_personality() -> None:
    with pytest.raises(
        ValueError,
        match="personality",
    ):
        create_character(
            personality=(),
        )


def test_character_rejects_invalid_status() -> None:
    with pytest.raises(
        ValueError,
        match="Character status",
    ):
        create_character(
            status="unknown",
        )
