"""Publishing context models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class PublishContext:
    """Configuration shared with a publisher."""

    output_directory: Path
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.output_directory, Path):
            raise TypeError(
                "Publish context output_directory must be a Path."
            )
