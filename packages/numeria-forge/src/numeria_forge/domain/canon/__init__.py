"""Canonical Numeria domain entities."""

from numeria_forge.domain.canon.character import Character
from numeria_forge.domain.canon.character_factory import (
    CharacterFactory,
)
from numeria_forge.domain.generated_character import GeneratedCharacter

from numeria_forge.util.slug import slugify

__all__ = [
    "Character",
    "CharacterFactory",
    "GeneratedCharacter",
    "slugify",
]