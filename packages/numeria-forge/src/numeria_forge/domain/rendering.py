from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class RenderedFile:
    """A rendered output ready to be written."""

    destination: Path
    content: str