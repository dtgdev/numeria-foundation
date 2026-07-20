from dataclasses import dataclass
from pathlib import Path
from typing import Any

from numeria_forge.domain.artifacts import ArtifactDefinition
from numeria_forge.domain.validators import Validator
from numeria_forge.extensions.hook_registry import CompilerHook
from numeria_forge.extensions.hooks import HookPoint
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

    def register_compiler_hook(
        self,
        hook_point: HookPoint,
        name: str,
        hook: CompilerHook,
    ) -> None:
        self.registries.compiler_hooks.register(
            hook_point,
            name,
            hook,
        )

    def run_compiler_hooks(
        self,
        hook_point: HookPoint,
        compiler_context: Any,
    ) -> None:
        self.registries.compiler_hooks.run(
            hook_point,
            compiler_context,
        )
