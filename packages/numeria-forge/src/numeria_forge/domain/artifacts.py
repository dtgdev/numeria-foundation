from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Artifact:
    """
    A compiler artifact produced during compilation.
    """

    destination: Path
    content: str
    media_type: str = "text/markdown"