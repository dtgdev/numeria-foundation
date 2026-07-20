from dataclasses import dataclass

from numeria_forge.domain.artifacts import ArtifactRegistry


@dataclass
class ExtensionContext:
    """Shared capabilities available during extension registration."""

    artifact_registry: ArtifactRegistry
