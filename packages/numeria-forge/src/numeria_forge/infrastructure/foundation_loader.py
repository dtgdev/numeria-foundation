"""Load the root `numeria.yaml` manifest for a Numeria Foundation."""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.domain.foundation import (
    FoundationManifest,
    FoundationMetadata,
)


class FoundationLoader:
    """Load `numeria.yaml` from a Numeria Foundation's root directory."""

    MANIFEST_FILENAME = "numeria.yaml"

    def load(self, root: Path) -> FoundationManifest:
        manifest_path = root / self.MANIFEST_FILENAME

        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)

        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"{manifest_path}: root must be a mapping")

        foundation_data = data.get("foundation")

        if not isinstance(foundation_data, dict):
            raise ValueError(
                f"{manifest_path}: missing required 'foundation' mapping"
            )

        try:
            metadata = FoundationMetadata(
                id=foundation_data["id"],
                name=foundation_data["name"],
                version=foundation_data["version"],
            )
        except KeyError as exc:
            raise ValueError(
                f"{manifest_path}: foundation is missing required field {exc}"
            ) from exc

        knowledge_root = root / data.get("knowledge_root", "knowledge")

        workspaces = tuple(
            root / workspace for workspace in data.get("workspaces", [])
        )

        return FoundationManifest(
            root_directory=root,
            metadata=metadata,
            knowledge_root=knowledge_root,
            workspaces=workspaces,
        )
