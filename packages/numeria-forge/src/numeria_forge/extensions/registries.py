from dataclasses import dataclass, field

from numeria_forge.domain.artifacts import (
    ArtifactRegistry,
    create_builtin_registry,
)
from numeria_forge.domain.templates import TemplateRegistry


@dataclass
class ForgeRegistries:
    """Collection of registries exposed to Forge extensions."""

    artifacts: ArtifactRegistry = field(
        default_factory=create_builtin_registry
    )
    templates: TemplateRegistry = field(
        default_factory=TemplateRegistry
    )
