from pathlib import Path

from numeria_forge.domain.workspaces import (
    Workspace,
    WorkspaceMetadata,
    WorkspacePackage,
)


def test_workspace_metadata_stores_identity() -> None:
    metadata = WorkspaceMetadata(
        id="numeria-foundation",
        name="Numeria Foundation",
        version="0.1.0",
    )

    assert metadata.id == "numeria-foundation"
    assert metadata.name == "Numeria Foundation"
    assert metadata.version == "0.1.0"


def test_workspace_package_exposes_directory_name() -> None:
    package = WorkspacePackage(
        path=Path("packages/concepts/derivative")
    )

    assert package.name == "derivative"


def test_workspace_contains_root_metadata_and_packages() -> None:
    metadata = WorkspaceMetadata(
        id="numeria-foundation",
        name="Numeria Foundation",
        version="0.1.0",
    )

    packages = (
        WorkspacePackage(
            path=Path("packages/concepts/derivative")
        ),
        WorkspacePackage(
            path=Path("packages/concepts/integral")
        ),
    )

    workspace = Workspace(
        root_directory=Path("/tmp/numeria-foundation"),
        metadata=metadata,
        packages=packages,
    )

    assert workspace.root_directory == Path(
        "/tmp/numeria-foundation"
    )
    assert workspace.metadata == metadata
    assert workspace.packages == packages
