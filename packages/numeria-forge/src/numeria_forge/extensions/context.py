from dataclasses import dataclass
from pathlib import Path

from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.domain.validators import Validator
from numeria_forge.extensions.registries import ForgeRegistries


@dataclass
class ExtensionContext:
    """Shared capabilities available during extension registration."""

    registries: ForgeRegistries

    def register_artifact(
        self,
        definition: ArtifactDefinition,
    ) -> None:
        self.registries.artifacts.register(definition)

    def register_template_root(
        self,
        root: Path,
    ) -> None:
        self.registries.templates.register(root)

    def register_validator(
        self,
        validator: Validator,
    ) -> None:
        self.registries.validators.register(validator)
