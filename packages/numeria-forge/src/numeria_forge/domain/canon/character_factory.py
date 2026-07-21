"""Factory for constructing canonical Character objects."""

from __future__ import annotations

# from numeria_forge.domain import GeneratedCharacter
from numeria_forge.domain.canon.character import Character
from numeria_forge.util.slug import slugify
from numeria_forge.domain.generated_character import (
    GeneratedCharacter,
)


class CharacterFactory:
    """Create canonical Character instances from generated characters."""

    def create(
        self,
        generated: GeneratedCharacter,
        *,
        character_id: str,
    ) -> Character:
        return Character(
            id=character_id,
            slug=slugify(generated.name),
            version="1.0.0",
            status="draft",
            name=generated.name,
            title=generated.name,
            mathematical_concept=generated.mathematical_concept,
            realm="Core Mathematics",
            description=generated.description,
            personality=tuple(generated.personality),
            superpower=generated.superpower,
            weakness=generated.weakness,
            catchphrase=generated.catchphrase,
            learning_objectives=(),
            age_range="8-12",
            tags=(),
            metadata={},
        )

    def _parse_personality(
        self,
        value: str | list[str] | tuple[str, ...],
    ) -> tuple[str, ...]:
        """Normalize personality into a tuple."""

        if isinstance(value, tuple):
            return value

        if isinstance(value, list):
            return tuple(
                item.strip()
                for item in value
                if item.strip()
            )

        separators_normalized = value.replace(
            ";",
            ",",
        )

        return tuple(
            part.strip()
            for part in separators_normalized.split(",")
            if part.strip()
        )
