from pathlib import Path

import yaml

from numeria_forge.domain.manifests import (
    EntityDefinition,
    Manifest,
    OutputDefinition,
)


class ManifestLoader:
    """Load manifest.yaml into domain objects."""

    def load(self, package_directory: Path) -> Manifest:
        manifest_path = package_directory / "manifest.yaml"

        if not manifest_path.is_file():
            raise ValueError(f"Manifest not found: {manifest_path}")

        try:
            data = yaml.safe_load(
                manifest_path.read_text(encoding="utf-8")
            )
        except yaml.YAMLError as exc:
            raise ValueError(
                f"Invalid YAML in manifest: {manifest_path}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("Manifest root must be a mapping")

        for field in ("schema_version", "entity", "outputs"):
            if field not in data:
                raise ValueError(
                    f"Missing required manifest field: {field}"
                )

        entity_data = data["entity"]
        outputs_data = data["outputs"]

        if not isinstance(entity_data, dict):
            raise ValueError("Manifest entity must be a mapping")

        if not isinstance(outputs_data, list):
            raise ValueError("Manifest outputs must be a list")

        try:
            entity = EntityDefinition(
                type=entity_data["type"],
                id=entity_data["id"],
                slug=entity_data["slug"],
                title=entity_data["title"],
            )

            outputs = tuple(
                OutputDefinition(
                    template=output["template"],
                    destination=output["destination"],
                )
                for output in outputs_data
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(
                f"Invalid manifest structure: {exc}"
            ) from exc

        return Manifest(
            schema_version=str(data["schema_version"]),
            entity=entity,
            outputs=outputs,
        )
