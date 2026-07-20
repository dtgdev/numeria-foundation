"""Publishing result models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Describe one artifact produced by a publisher."""

    publisher: str
    path: Path
    media_type: str

    def __post_init__(self) -> None:
        if not self.publisher.strip():
            raise ValueError(
                "Publish result publisher must not be empty."
            )

        if not isinstance(self.path, Path):
            raise TypeError(
                "Publish result path must be a Path."
            )

        if not self.media_type.strip():
            raise ValueError(
                "Publish result media_type must not be empty."
            )
