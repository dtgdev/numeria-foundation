
"""Domain models for Forge manifests."""

from dataclasses import dataclass, field
from pathlib import PurePosixPath

@dataclass(frozen=True, slots=True)
class OutputDefinition:
    template: str | None = None
    artifact: str | None = None
    destination: str | None = None

    def __post_init__(self) -> None:
        has_template = self.template is not None
        has_artifact = self.artifact is not None

        if has_template == has_artifact:
            raise ValueError(
                "Exactly one of 'template' or 'artifact' must be specified."
            )

        if has_template:
            if not self.template.strip():
                raise ValueError("Output template cannot be empty.")

            if self.destination is None:
                raise ValueError(
                    "Template outputs must specify a destination."
                )

            if not self.destination.strip():
                raise ValueError(
                    "Output destination cannot be empty."
                )

            destination = PurePosixPath(self.destination)

            if destination.is_absolute() or ".." in destination.parts:
                raise ValueError(
                    f"Output destination must remain inside the package: "
                    f"{self.destination}"
                )

        if has_artifact:
            if not self.artifact.strip():
                raise ValueError(
                    "Artifact name cannot be empty."
                )


@dataclass(frozen=True, slots=True)
class EntityDefinition:
    """Canonical identity information for a Forge entity."""

    type: str
    id: str
    slug: str
    title: str

    def __post_init__(self) -> None:
        required_fields = {
            "type": self.type,
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
        }

        for field_name, value in required_fields.items():
            if not value.strip():
                raise ValueError(
                    f"Entity field '{field_name}' cannot be empty."
                )

        expected_prefix = f"numeria:{self.type}:"

        if not self.id.startswith(expected_prefix):
            raise ValueError(
                f"Entity ID must start with '{expected_prefix}'."
            )

        if self.id != f"{expected_prefix}{self.slug}":
            raise ValueError(
                "Entity ID must match the entity type and slug."
            )

            
@dataclass(frozen=True, slots=True)
class Manifest:
    """Complete in-memory representation of a Forge manifest."""

    schema_version: str
    entity: EntityDefinition
    outputs: tuple[OutputDefinition, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("Manifest schema version cannot be empty.")

        destinations = [
            output.destination
            for output in self.outputs
            if output.destination is not None
        ]

        if len(destinations) != len(set(destinations)):
            raise ValueError(
                "Manifest output destinations must be unique."
            )