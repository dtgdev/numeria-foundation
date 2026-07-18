from dataclasses import dataclass


@dataclass(slots=True)
class Concept:
    """Canonical representation of a knowledge concept."""

    name: str
    canonical_id: str
    domain: str
    version: str = "0.1.0"
    status: str = "draft"

    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")
