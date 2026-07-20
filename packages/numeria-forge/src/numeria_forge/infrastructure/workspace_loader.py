from pathlib import Path

import yaml

from numeria_forge.domain.workspaces import (
    Workspace,
    WorkspaceMetadata,
    WorkspacePackage,
)


class WorkspaceLoader:
    """Load a Numeria Forge workspace from workspace.yaml."""

    def load(self, workspace_root: Path) -> Workspace:
        workspace_file = workspace_root / "workspace.yaml"

        if not workspace_file.exists():
            raise FileNotFoundError(workspace_file)

        data = yaml.safe_load(
            workspace_file.read_text(encoding="utf-8")
        )

        workspace_data = data["workspace"]

        metadata = WorkspaceMetadata(
            id=workspace_data["id"],
            name=workspace_data["name"],
            version=workspace_data["version"],
        )

        packages = []

        for package_path in data.get("packages", []):
            package_directory = workspace_root / package_path

            manifest_file = package_directory / "manifest.yaml"

            if not manifest_file.exists():
                raise FileNotFoundError(
                    f"Package '{package_path}' is missing manifest.yaml"
                )

            packages.append(
                WorkspacePackage(path=Path(package_path))
            )

        return Workspace(
            root_directory=workspace_root,
            metadata=metadata,
            packages=tuple(packages),
        )
