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

        packages: list[WorkspacePackage] = []

        for pattern in data.get("packages", []):
            matches = sorted(workspace_root.glob(pattern))

            if not matches:
                raise FileNotFoundError(
                    f"No packages matched '{pattern}'"
                )

            for package_directory in matches:
                manifest_file = (
                    package_directory / "manifest.yaml"
                )

                if not manifest_file.exists():
                    raise FileNotFoundError(
                        f"Package '{package_directory.relative_to(workspace_root)}' "
                        "is missing manifest.yaml"
                    )

                packages.append(
                    WorkspacePackage(
                        path=package_directory.relative_to(
                            workspace_root
                        )
                    )
                )

        return Workspace(
            root_directory=workspace_root,
            metadata=metadata,
            packages=tuple(packages),
        )
