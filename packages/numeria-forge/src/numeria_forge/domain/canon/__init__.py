"""Canonical Numeria domain entities."""

from numeria_forge.domain.canon.canon import Canon, CanonLoadError
from numeria_forge.domain.canon.character import Character
from numeria_forge.domain.canon.character_factory import (
    CharacterFactory,
)
from numeria_forge.domain.canon.entity import CanonEntity
from numeria_forge.domain.canon.loader import CanonLoader
from numeria_forge.domain.generated_character import GeneratedCharacter

from numeria_forge.util.slug import slugify

__all__ = [
    "Canon",
    "CanonEntity",
    "CanonLoadError",
    "CanonLoader",
    "Character",
    "CharacterFactory",
    "GeneratedCharacter",
    "slugify",
]
