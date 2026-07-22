"""The loaded knowledge base: every canonical entity, indexed for lookup."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterator

from numeria_forge.domain.canon.entity import CanonEntity


class CanonLoadErrorCode(str, Enum):
    """Category of a load-time problem, so validators can filter by
    kind (e.g. DuplicateIdValidator only cares about DUPLICATE_ID)
    instead of pattern-matching error message strings."""

    MISSING_ROOT = "missing-root"
    READ_ERROR = "read-error"
    PARSE_ERROR = "parse-error"
    INVALID_SHAPE = "invalid-shape"
    MISSING_ID = "missing-id"
    MISSING_TYPE = "missing-type"
    DUPLICATE_ID = "duplicate-id"


@dataclass(frozen=True, slots=True)
class CanonLoadError:
    """A file-level problem encountered while loading the canon."""

    path: Path
    message: str
    code: CanonLoadErrorCode = CanonLoadErrorCode.READ_ERROR


@dataclass(slots=True)
class Canon:
    """The full set of canonical entities loaded from a knowledge root."""

    root: Path
    entities: dict[str, CanonEntity] = field(default_factory=dict)
    load_errors: list[CanonLoadError] = field(default_factory=list)

    def by_type(self, entity_type: str) -> tuple[CanonEntity, ...]:
        return tuple(
            entity
            for entity in self.entities.values()
            if entity.type == entity_type
        )

    def relationships(self) -> tuple[CanonEntity, ...]:
        return tuple(
            entity
            for entity in self.entities.values()
            if entity.is_relationship
        )

    def non_relationships(self) -> tuple[CanonEntity, ...]:
        return tuple(
            entity
            for entity in self.entities.values()
            if not entity.is_relationship
        )

    def __len__(self) -> int:
        return len(self.entities)

    def __iter__(self) -> Iterator[CanonEntity]:
        return iter(self.entities.values())

    def __contains__(self, entity_id: object) -> bool:
        return entity_id in self.entities
