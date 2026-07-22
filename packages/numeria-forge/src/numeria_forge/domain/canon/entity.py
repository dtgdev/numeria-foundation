"""A single loaded knowledge-base entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from numeria_forge.domain.canon.prefixes import RELATIONSHIPS_DIRECTORY_NAME


@dataclass(frozen=True, slots=True)
class CanonEntity:
    """Permissive, loosely-typed representation of one `entity.yaml`.

    Unlike :class:`numeria_forge.domain.canon.character.Character`, this
    does not enforce a fixed schema -- the real knowledge base contains
    many entity types (Concept, Scene, Book, relationship entities, ...)
    with very different shapes, so this wraps the raw parsed mapping and
    lets validators decide what's required.
    """

    id: str
    type: str
    source_path: Path
    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    @property
    def is_relationship(self) -> bool:
        return RELATIONSHIPS_DIRECTORY_NAME in self.source_path.parts
