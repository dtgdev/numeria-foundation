from pathlib import Path

import pytest

from numeria_forge.infrastructure.workspace_loader import WorkspaceLoader


def test_workspace_loader_loads_metadata_and_packages(
    tmp_path: Path,
) -> None:
    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria-foundation
  name: Numeria Foundation
  version: "0.1.0"

packages:
  - packages/concepts/derivative
  - packages/concepts/integral
""".strip(),
        encoding="utf-8",
    )

    workspace = WorkspaceLoader().load(tmp_path)

    assert workspace.root_directory == tmp_path
    assert workspace.metadata.id == "numeria-foundation"
    assert workspace.metadata.name == "Numeria Foundation"
    assert workspace.metadata.version == "0.1.0"

    assert tuple(
        package.name for package in workspace.packages
    ) == (
        "derivative",
        "integral",
    )

    assert workspace.packages[0].path == Path(
        "packages/concepts/derivative"
    )


def test_workspace_loader_supports_empty_packages(
    tmp_path: Path,
) -> None:
    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: empty-workspace
  name: Empty Workspace
  version: "0.1.0"
""".strip(),
        encoding="utf-8",
    )

    workspace = WorkspaceLoader().load(tmp_path)

    assert workspace.packages == ()


def test_workspace_loader_raises_when_workspace_file_is_missing(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError) as error:
        WorkspaceLoader().load(tmp_path)

    assert error.value.args[0] == tmp_path / "workspace.yaml"
