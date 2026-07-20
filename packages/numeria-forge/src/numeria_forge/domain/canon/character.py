"""Canonical Numeria character domain model."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


CHARACTER_ID_PATTERN = re.compile(
    r"^NUM-CHR-\d{6}$"
)

ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "review",
        "approved",
        "published",
        "retired",
    }
)


@dataclass(frozen=True, slots=True)
class Character:
    """Trusted canonical representation of a Numeria character."""

    id: str
    slug: str
    version: str

    name: str
    title: str
    mathematical_concept: str
    realm: str

    description: str
    personality: tuple[str, ...]
    superpower: str
    weakness: str
    catchphrase: str

    learning_objectives: tuple[str, ...] = ()
    age_range: str = "8-12"
    tags: tuple[str, ...] = ()

    status: str = "draft"
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        if not CHARACTER_ID_PATTERN.fullmatch(
            self.id
        ):
            raise ValueError(
                "Character id must use the format "
                "NUM-CHR-000001."
            )

        required_text = {
            "slug": self.slug,
            "version": self.version,
            "name": self.name,
            "title": self.title,
            "mathematical_concept": (
                self.mathematical_concept
            ),
            "realm": self.realm,
            "description": self.description,
            "superpower": self.superpower,
            "weakness": self.weakness,
            "catchphrase": self.catchphrase,
            "age_range": self.age_range,
        }

        for field_name, value in (
            required_text.items()
        ):
            if not value.strip():
                raise ValueError(
                    f"Character {field_name} "
                    "must not be empty."
                )

        if not self.personality:
            raise ValueError(
                "Character personality must contain "
                "at least one trait."
            )

        if any(
            not trait.strip()
            for trait in self.personality
        ):
            raise ValueError(
                "Character personality traits "
                "must not be empty."
            )

        if self.status not in ALLOWED_STATUSES:
            allowed = ", ".join(
                sorted(ALLOWED_STATUSES)
            )
            raise ValueError(
                "Character status must be one of: "
                f"{allowed}."
            )
