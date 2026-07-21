"""Serialize canonical characters into YAML-compatible documents."""

from __future__ import annotations

from typing import Any

from numeria_forge.domain import Character


class CharacterYamlSerializer:
    """Convert a canonical Character into a YAML-compatible dictionary."""

    SCHEMA = "numeria.character.v1"

    def to_dict(
        self,
        character: Character,
    ) -> dict[str, Any]:
        """Return the canonical YAML document."""

        if not isinstance(character, Character):
            raise TypeError(
                "Character YAML serializer requires a Character."
            )

        return {
            "schema": self.SCHEMA,
            "id": character.id,
            "version": character.version,
            "status": character.status,
            "name": character.name,
            "title": character.title,
            "slug": character.slug,
            "realm": character.realm,
            "mathematical_concept": character.mathematical_concept,
            "description": character.description,
            "personality": list(character.personality),
            "superpower": character.superpower,
            "weakness": character.weakness,
            "catchphrase": character.catchphrase,
            "learning_objectives": list(
                character.learning_objectives
            ),
            "age_range": character.age_range,
            "tags": list(character.tags),
            "metadata": dict(character.metadata),
        }
