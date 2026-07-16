from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from app.core import repository_root
from app.models.world import (
    PublishedRegion,
    RegionDraft,
    RegionValidationResult,
)
from app.services import graph_service


REGION_ID_PATTERN = re.compile(r"^NUM-REG-(\d{6})$")


def slugify(value: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower(),
    ).strip("-")

    return slug or "region"


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(
            path.read_text(encoding="utf-8"),
        ) or {}
    except (OSError, yaml.YAMLError):
        return {}

    return value if isinstance(value, dict) else {}


class RegionCreatorService:
    def _world_path(self) -> Path:
        return (
            repository_root()
            / "knowledge"
            / "world"
            / "entity.yaml"
        )

    def _regions_root(self) -> Path:
        return (
            repository_root()
            / "knowledge"
            / "world"
            / "regions"
        )

    def _existing_regions(self) -> list[dict[str, Any]]:
        regions: list[dict[str, Any]] = []
        root = self._regions_root()

        if not root.exists():
            return regions

        for path in root.rglob("entity.yaml"):
            data = load_yaml_mapping(path)

            if data.get("type") == "Region":
                regions.append(data)

        return regions

    def _world(self) -> dict[str, Any]:
        return load_yaml_mapping(self._world_path())

    def next_region_id(self) -> str:
        highest_number = 0

        for region in self._existing_regions():
            region_id = str(region.get("id", ""))
            match = REGION_ID_PATTERN.fullmatch(region_id)

            if match:
                highest_number = max(
                    highest_number,
                    int(match.group(1)),
                )

        return f"NUM-REG-{highest_number + 1:06d}"

    def validate(
        self,
        draft: RegionDraft,
    ) -> RegionValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        world = self._world()

        if not world:
            errors.append(
                "The canonical Numeria world could not be loaded."
            )
        elif world.get("id") != draft.world_id:
            errors.append(
                f"World '{draft.world_id}' does not exist."
            )

        duplicate = next(
            (
                region
                for region in self._existing_regions()
                if str(region.get("name", ""))
                .strip()
                .casefold()
                == draft.name.casefold()
            ),
            None,
        )

        if duplicate:
            errors.append(
                f"A region named '{draft.name}' already exists "
                f"with ID {duplicate.get('id')}."
            )

        if not draft.themes:
            warnings.append(
                "No region themes were supplied."
            )

        if not draft.atmosphere:
            warnings.append(
                "No visual atmosphere was supplied."
            )

        if not draft.landmark_ideas:
            warnings.append(
                "No landmark ideas were supplied."
            )

        proposed_id = self.next_region_id()

        proposed_path = (
            Path("knowledge")
            / "world"
            / "regions"
            / f"{proposed_id}-{slugify(draft.name)}"
            / "entity.yaml"
        )

        return RegionValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            proposed_id=proposed_id,
            proposed_path=str(proposed_path),
        )

    def publish(
        self,
        draft: RegionDraft,
    ) -> PublishedRegion:
        validation = self.validate(draft)

        if not validation.valid:
            raise ValueError(
                " ".join(validation.errors)
            )

        region_id = validation.proposed_id

        if region_id is None:
            raise RuntimeError(
                "Unable to generate region ID."
            )

        directory = (
            self._regions_root()
            / f"{region_id}-{slugify(draft.name)}"
        )

        if directory.exists():
            raise FileExistsError(
                f"Region directory already exists: {directory}"
            )

        directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        entity = {
            "id": region_id,
            "name": draft.name,
            "type": "Region",
            "status": "CANON",
            "version": "1.0.0",
            "world": {
                "id": draft.world_id,
            },
            "domain": {
                "name": draft.domain,
            },
            "summary": draft.summary,
            "educational_mission":
                draft.educational_mission,
            "themes": draft.themes,
            "visual_identity": {
                "atmosphere": draft.atmosphere,
                "landmarks": draft.landmark_ideas,
            },
        }

        entity_path = directory / "entity.yaml"
        readme_path = directory / "README.md"

        try:
            entity_path.write_text(
                yaml.safe_dump(
                    entity,
                    sort_keys=False,
                    allow_unicode=True,
                    width=88,
                ),
                encoding="utf-8",
            )

            readme_path.write_text(
                "\n".join(
                    [
                        f"# {draft.name}",
                        "",
                        f"**Region ID:** `{region_id}`",
                        "",
                        "## Summary",
                        "",
                        draft.summary,
                        "",
                        "## Educational Mission",
                        "",
                        draft.educational_mission,
                        "",
                        "## Domain",
                        "",
                        draft.domain,
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        except Exception:
            if entity_path.exists():
                entity_path.unlink()

            if readme_path.exists():
                readme_path.unlink()

            directory.rmdir()
            raise

        graph_service.refresh()

        relative_path = entity_path.relative_to(
            repository_root()
        )

        return PublishedRegion(
            id=region_id,
            name=draft.name,
            world_id=draft.world_id,
            path=str(relative_path),
            message=(
                "Region published to the Numeria world canon."
            ),
        )


region_creator_service = RegionCreatorService()
