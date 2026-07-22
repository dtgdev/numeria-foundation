"""Compiler stage: generate default output for every Canon entity.

Closes the gap `FORGE_COMPILER.md` has documented since v0.14.0:
package generation (`LoadManifestStage` / `RenderTemplatesStage`) only
ever produces output for hand-authored `packages/*/manifest.yaml`
files, which use a completely different identity scheme
(`numeria:type:slug`) than the real Canon's `NUM-XXX-000001` entities
under `knowledge/`. This stage renders a default artifact set --
`readme`, plus `character_card` for Characters -- directly from each
Canon entity's own data, so the real Canon produces build output
without requiring every entity to also have a hand-authored manifest.

Deliberately simple: only the two builtin artifact templates that
already exist (`domain.artifacts.create_builtin_registry`) are
rendered; there is no Story/Lesson/Assessment-specific template today.
Entities missing `title`/`slug` (most of the real Canon predates
Canon Law #1's slug requirement) fall back to `name`/`id` so rendering
never fails on `StrictUndefined` -- see `_entity_view` below.
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.domain.artifacts import Artifact, create_builtin_registry
from numeria_forge.domain.canon.entity import CanonEntity
from numeria_forge.rendering import TemplateEnvironment, TemplateRenderer

#: Where each entity type's generated output lands under `build/`.
#: Numeria's Canon has no literal "Story" entity type -- Scene and Book
#: are the closest narrative-adjacent types, so they're routed to
#: `stories/` to match the target `build/` layout. Every other type
#: falls back to `canon/`.
TYPE_DIRECTORY_BY_ENTITY_TYPE: dict[str, str] = {
    "Lesson": "lessons",
    "Assessment": "assessments",
    "Scene": "stories",
    "Book": "stories",
}
DEFAULT_TYPE_DIRECTORY = "canon"

#: Artifact names (from create_builtin_registry()) rendered for every
#: entity, plus extra artifacts rendered only for specific types.
BASE_ARTIFACT_NAMES: tuple[str, ...] = ("readme",)
EXTRA_ARTIFACT_NAMES_BY_TYPE: dict[str, tuple[str, ...]] = {
    "Character": ("character_card",)
}


def _bucket_for(entity_type: str) -> str:
    return TYPE_DIRECTORY_BY_ENTITY_TYPE.get(entity_type, DEFAULT_TYPE_DIRECTORY)


def _entity_view(entity: CanonEntity) -> dict:
    """A template-friendly dict for `entity` -- Jinja2's dot syntax
    (`entity.title`) works against dict keys just as well as
    attributes, so no dedicated adapter class is needed. Falls back
    `title` -> name -> id and `slug` -> id so rendering never raises
    on `StrictUndefined` for the ~90 real entities that predate Canon
    Law #1's slug requirement.
    """

    return {
        "id": entity.id,
        "type": entity.type,
        "title": entity.get("title") or entity.get("name") or entity.id,
        "slug": entity.get("slug") or entity.id,
    }


def _folder_name(entity: CanonEntity) -> str:
    slug = entity.get("slug")
    return f"{entity.id}-{slug}" if slug else entity.id


class GenerateMissingAssetsStage(CompilerStage):
    """Render default artifacts for every Canon entity into
    `context.generated_assets`."""

    def __init__(self, template_root: Path) -> None:
        self._renderer = TemplateRenderer(TemplateEnvironment(template_root))
        self._registry = create_builtin_registry()

    @property
    def name(self) -> str:
        return "generate-missing-assets"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.loaded_canon is None:
            raise RuntimeError(
                "GenerateMissingAssetsStage requires LoadCanonStage to run first."
            )

        for entity in context.loaded_canon.non_relationships():
            artifact_names = BASE_ARTIFACT_NAMES + EXTRA_ARTIFACT_NAMES_BY_TYPE.get(
                entity.type, ()
            )
            bucket = _bucket_for(entity.type)
            folder_name = _folder_name(entity)
            view = _entity_view(entity)

            for artifact_name in artifact_names:
                definition = self._registry.lookup(artifact_name)

                content = self._renderer.render(
                    definition.template, {"entity": view}
                )

                destination = (
                    Path(bucket)
                    / entity.type.lower()
                    / folder_name
                    / definition.default_destination
                )

                context.generated_assets.append(
                    Artifact(destination=destination, content=content)
                )

        return context
