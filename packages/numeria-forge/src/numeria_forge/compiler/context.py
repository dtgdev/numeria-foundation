from dataclasses import dataclass, field
from pathlib import Path

from numeria_forge.domain import ArtifactCollection
from numeria_forge.domain.artifacts import ArtifactRegistry
from numeria_forge.domain.manifests import Manifest


@dataclass(slots=True)
class CompilerContext:
    source_directory: Path
    manifest: Manifest | None = None
    artifact_registry: ArtifactRegistry | None = None
    artifacts: ArtifactCollection = field(
        default_factory=ArtifactCollection
    )
