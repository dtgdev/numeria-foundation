from pathlib import Path

import pytest

from numeria_forge.infrastructure.workspace_loader import WorkspaceLoader


def test_workspace_loader_loads_metadata_and_packages(
    tmp_path: Path,
) -> None:
    package = (
        tmp_path
        / "packages"
        / "concepts"
        / "derivative"
    )

    package.mkdir(parents=True)

    (package / "manifest.yaml").write_text(
        "schema_version: '1.0'",
        encoding="utf-8",
    )

    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria-foundation
  name: Numeria Foundation
  version: "0.1.0"

packages:
  - packages/concepts/derivative
""".strip(),
        encoding="utf-8",
    )

    workspace = WorkspaceLoader().load(tmp_path)

    assert workspace.root_directory == tmp_path
    assert workspace.metadata.id == "numeria-foundation"
    assert workspace.metadata.name == "Numeria Foundation"
    assert workspace.metadata.version == "0.1.0"

    assert len(workspace.packages) == 1
    assert workspace.packages[0].name == "derivative"


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
    with pytest.raises(FileNotFoundError):
        WorkspaceLoader().load(tmp_path)


def test_workspace_loader_validates_package_manifest(
    tmp_path: Path,
) -> None:
    package = (
        tmp_path
        / "packages"
        / "concepts"
        / "integral"
    )

    package.mkdir(parents=True)

    (package / "manifest.yaml").write_text(
        "schema_version: '1.0'",
        encoding="utf-8",
    )

    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria
  name: Numeria
  version: "0.1"

packages:
  - packages/concepts/integral
""".strip(),
        encoding="utf-8",
    )

    workspace = WorkspaceLoader().load(tmp_path)

    assert len(workspace.packages) == 1
    assert workspace.packages[0].name == "integral"


def test_workspace_loader_rejects_package_without_manifest(
    tmp_path: Path,
) -> None:
    (
        tmp_path
        / "packages"
        / "concepts"
        / "limit"
    ).mkdir(parents=True)

    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria
  name: Numeria
  version: "0.1"

packages:
  - packages/concepts/limit
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        WorkspaceLoader().load(tmp_path)
