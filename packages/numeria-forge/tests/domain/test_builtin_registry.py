from numeria_forge.domain.artifacts import create_builtin_registry


def test_builtin_registry_contains_readme() -> None:
    registry = create_builtin_registry()

    definition = registry.lookup("readme")

    assert definition.name == "readme"
    assert definition.template == "concept/README.md.j2"
    assert definition.media_type == "text/markdown"
    assert definition.default_destination == "README.md"


def test_builtin_registry_contains_character_card() -> None:
    registry = create_builtin_registry()

    definition = registry.lookup("character_card")

    assert definition.name == "character_card"
    assert definition.template == "concept/CHARACTER_CARD.md.j2"
    assert definition.media_type == "text/markdown"
    assert definition.default_destination == "CHARACTER_CARD.md"
