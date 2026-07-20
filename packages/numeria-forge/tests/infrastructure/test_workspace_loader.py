from pathlib import Path

import pytest

from numeria_forge.infrastructure.workspace_loader import WorkspaceLoader


def create_package(
    workspace: Path,
    relative_path: str,
) -> None:
    package = workspace / relative_path
    package.mkdir(parents=True)

    (package / "manifest.yaml").write_text(
        "schema_version: '1.0'",
        encoding="utf-8",
    )


def test_workspace_loader_supports_glob_patterns(
    tmp_path: Path,
) -> None:
    create_package(
        tmp_path,
        "packages/concepts/derivative",
    )

    create_package(
        tmp_path,
        "packages/concepts/integral",
    )

    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria
  name: Numeria
  version: "0.1"

packages:
  - packages/concepts/*
""".strip(),
        encoding="utf-8",
    )

    workspace = WorkspaceLoader().load(tmp_path)

    assert tuple(
        package.name
        for package in workspace.packages
    ) == (
        "derivative",
        "integral",
    )


def test_workspace_loader_rejects_missing_glob_matches(
    tmp_path: Path,
) -> None:
    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria
  name: Numeria
  version: "0.1"

packages:
  - packages/stories/*
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        WorkspaceLoader().load(tmp_path)
