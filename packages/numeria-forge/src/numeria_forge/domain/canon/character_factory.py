"""Factory for creating canonical Numeria characters."""

from __future__ import annotations

from numeria_forge.domain.canon.character import (
    Character,
)
from numeria_forge.domain.generated_character import (
    GeneratedCharacter,
)
from numeria_forge.util import slugify


class CharacterFactory:
    """Transform generated character data into trusted canon."""

    def create(
        self,
        generated: GeneratedCharacter,
        *,
        character_id: str,
        title: str | None = None,
        realm: str = "Mathematics",
        version: str = "1.0.0",
        age_range: str = "8-12",
        learning_objectives: tuple[str, ...] = (),
        tags: tuple[str, ...] = (),
    ) -> Character:
        """Create a validated canonical character."""

        normalized_name = generated.name.strip()

        personality = self._parse_personality(
            generated.personality,
        )

        normalized_tags = self._normalize_values(
            tags,
        )

        normalized_objectives = (
            self._normalize_values(
                learning_objectives,
            )
        )

        return Character(
            id=character_id.strip(),
            slug=slugify(normalized_name),
            version=version.strip(),
            name=normalized_name,
            title=(
                title.strip()
                if title is not None
                else normalized_name
            ),
            mathematical_concept=(
                generated.mathematical_concept.strip()
            ),
            realm=realm.strip(),
            description=generated.description.strip(),
            personality=personality,
            superpower=generated.superpower.strip(),
            weakness=generated.weakness.strip(),
            catchphrase=generated.catchphrase.strip(),
            learning_objectives=(
                normalized_objectives
            ),
            age_range=age_range.strip(),
            tags=normalized_tags,
            status="draft",
            metadata={
                "source": "ai-generation",
            },
        )

    def _parse_personality(
        self,
        value: str,
    ) -> tuple[str, ...]:
        separators_normalized = value.replace(
            ";",
            ",",
        )

        traits = tuple(
            part.strip()
            for part in separators_normalized.split(",")
            if part.strip()
        )

        if traits:
            return traits

        raise ValueError(
            "Generated character personality "
            "must contain at least one trait."
        )

    def _normalize_values(
        self,
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        return tuple(
            value.strip()
            for value in values
            if value.strip()
        )
