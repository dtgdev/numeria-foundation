from pathlib import Path

import pytest

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import PublishGeneratedAssetsStage
from numeria_forge.domain.artifacts import Artifact


def test_requires_build_directory(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)
    context.generated_assets.append(
        Artifact(destination=Path("canon/concept/x/README.md"), content="hi")
    )

    with pytest.raises(RuntimeError):
        PublishGeneratedAssetsStage().execute(context)


def test_writes_every_generated_asset_under_build_directory(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path, build_directory=tmp_path / "build"
    )
    context.generated_assets.append(
        Artifact(destination=Path("canon/concept/x/README.md"), content="hi")
    )
    context.generated_assets.append(
        Artifact(
            destination=Path("stories/scene/y/README.md"), content="scene content"
        )
    )

    PublishGeneratedAssetsStage().execute(context)

    assert (tmp_path / "build" / "canon" / "concept" / "x" / "README.md").read_text(
        encoding="utf-8"
    ) == "hi"
    assert (tmp_path / "build" / "stories" / "scene" / "y" / "README.md").exists()
    assert len(context.published_assets) == 2


def test_overwrites_on_repeated_runs(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path, build_directory=tmp_path / "build"
    )
    context.generated_assets.append(
        Artifact(destination=Path("canon/concept/x/README.md"), content="first")
    )
    PublishGeneratedAssetsStage().execute(context)

    context.generated_assets.clear()
    context.generated_assets.append(
        Artifact(destination=Path("canon/concept/x/README.md"), content="second")
    )
    PublishGeneratedAssetsStage().execute(context)

    written = tmp_path / "build" / "canon" / "concept" / "x" / "README.md"
    assert written.read_text(encoding="utf-8") == "second"


def test_published_assets_are_publish_results(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path, build_directory=tmp_path / "build"
    )
    context.generated_assets.append(
        Artifact(destination=Path("canon/concept/x/README.md"), content="hi")
    )

    PublishGeneratedAssetsStage().execute(context)

    result = context.published_assets[0]
    assert result.publisher == "publish-generated-assets"
    assert result.path == tmp_path / "build" / "canon" / "concept" / "x" / "README.md"
    assert result.media_type == "text/markdown"
