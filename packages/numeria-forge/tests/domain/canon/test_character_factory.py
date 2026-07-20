from numeria_forge.domain import (
    CharacterFactory,
    GeneratedCharacter,
)


def test_factory_creates_canonical_character() -> None:
    generated = GeneratedCharacter(
        name="Derivative",
        mathematical_concept="Derivative",
        description=(
            "A young explorer who detects change."
        ),
        personality=(
            "Curious, Brave, Observant"
        ),
        superpower=(
            "Reveals instantaneous rates of change."
        ),
        weakness=(
            "Needs enough information."
        ),
        catchphrase=(
            "Every change leaves a clue!"
        ),
    )

    character = CharacterFactory().create(
        generated,
        character_id="NUM-CHR-000001",
        title="Detective of Change",
        realm="Calculus",
        learning_objectives=(
            "Explain rate of change.",
            "Recognize changing quantities.",
        ),
        tags=(
            "calculus",
            "change",
        ),
    )

    assert character.id == "NUM-CHR-000001"
    assert character.slug == "derivative"
    assert character.title == "Detective of Change"
    assert character.realm == "Calculus"

    assert character.personality == (
        "Curious",
        "Brave",
        "Observant",
    )

    assert character.metadata == {
        "source": "ai-generation",
    }


def test_factory_uses_name_as_default_title() -> None:
    generated = GeneratedCharacter(
        name="Lady Limit",
        mathematical_concept="Limit",
        description="Guardian of approaching values.",
        personality="Patient; Thoughtful",
        superpower="Sees what values approach.",
        weakness="Cannot cross undefined boundaries.",
        catchphrase="Closer reveals the answer!",
    )

    character = CharacterFactory().create(
        generated,
        character_id="NUM-CHR-000003",
        realm="Calculus",
    )

    assert character.title == "Lady Limit"
    assert character.slug == "lady-limit"
    assert character.personality == (
        "Patient",
        "Thoughtful",
    )
