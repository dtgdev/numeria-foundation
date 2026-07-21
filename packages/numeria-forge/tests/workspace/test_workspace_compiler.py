from pathlib import Path

from numeria_forge.compiler import Compiler
from numeria_forge.compiler.stages import (
    LoadManifestStage,
    LoadManifestStage,
    RenderTemplatesStage,
)
from numeria_forge.infrastructure.workspace_loader import (
    WorkspaceLoader,
)
from numeria_forge.workspace import WorkspaceCompiler


def create_package(
    workspace: Path,
    relative_path: str,
    title: str,
) -> None:
    package = workspace / relative_path
    package.mkdir(parents=True)

    slug = title.lower()

    (package / "manifest.yaml").write_text(
        f"""
schema_version: "1.0"

entity:
  type: concept
  id: numeria:concept:{slug}
  slug: {slug}
  title: {title}

outputs:
  - artifact: readme
""".strip(),
        encoding="utf-8",
    )


def create_workspace(tmp_path: Path) -> None:
    create_package(
        tmp_path,
        "packages/concepts/derivative",
        "Derivative",
    )

    create_package(
        tmp_path,
        "packages/concepts/integral",
        "Integral",
    )

    (tmp_path / "workspace.yaml").write_text(
        """
schema_version: "1.0"

workspace:
  id: numeria
  name: Numeria Foundation
  version: "0.1.0"

packages:
  - packages/concepts/*
""".strip(),
        encoding="utf-8",
    )


def build_workspace(tmp_path: Path):
    workspace = WorkspaceLoader().load(tmp_path)

    template_root = (
        Path(__file__).resolve().parents[2]
        / "templates"
    )

    compiler = Compiler(
        stages=[
            LoadManifestStage(),
            LoadManifestStage(),
            RenderTemplatesStage(template_root),
        ]
    )

    result = WorkspaceCompiler(
        compiler
    ).compile(workspace)

    return workspace, result


def test_workspace_compiles_multiple_packages(
    tmp_path: Path,
) -> None:
    create_workspace(tmp_path)

    _, result = build_workspace(tmp_path)

    assert result.package_count == 2
    assert result.artifact_count == 2
    assert result.package_names == (
        "derivative",
        "integral",
    )


def test_workspace_build_result_formats_report(
    tmp_path: Path,
) -> None:
    create_workspace(tmp_path)

    workspace, result = build_workspace(tmp_path)

    report = result.format_report(
        workspace.metadata.name
    )

    assert report == """
Building Numeria Foundation...

✓ derivative
✓ integral

2 packages compiled
2 artifacts generated

Build succeeded.
""".strip()
