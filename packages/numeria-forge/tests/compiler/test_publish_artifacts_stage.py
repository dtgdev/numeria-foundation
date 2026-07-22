from pathlib import Path

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import PublishArtifactsStage
from numeria_forge.domain.artifacts import Artifact


def test_writes_relative_to_output_directory(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path,
        output_directory=tmp_path / "package",
    )
    context.artifacts.add(
        Artifact(destination=Path("README.md"), content="# Hello")
    )

    PublishArtifactsStage().execute(context)

    written = tmp_path / "package" / "README.md"
    assert written.exists()
    assert written.read_text(encoding="utf-8") == "# Hello"


def test_falls_back_to_source_directory_when_no_output_directory(
    tmp_path: Path,
) -> None:
    package_directory = tmp_path / "derivative"
    package_directory.mkdir()

    context = CompilerContext(
        project_root=package_directory,
        source_directory=package_directory,
    )
    context.artifacts.add(
        Artifact(destination=Path("README.md"), content="# Hello")
    )

    PublishArtifactsStage().execute(context)

    assert (package_directory / "README.md").exists()


def test_explicit_output_directory_constructor_arg_wins(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path,
        output_directory=tmp_path / "ignored",
    )
    context.artifacts.add(
        Artifact(destination=Path("README.md"), content="# Hello")
    )

    PublishArtifactsStage(output_directory=tmp_path / "explicit").execute(context)

    assert (tmp_path / "explicit" / "README.md").exists()
    assert not (tmp_path / "ignored" / "README.md").exists()


def test_overwrites_by_default(tmp_path: Path) -> None:
    context = CompilerContext(
        project_root=tmp_path,
        output_directory=tmp_path,
    )
    context.artifacts.add(
        Artifact(destination=Path("README.md"), content="first")
    )
    PublishArtifactsStage().execute(context)

    context.artifacts.clear()
    context.artifacts.add(
        Artifact(destination=Path("README.md"), content="second")
    )
    PublishArtifactsStage().execute(context)

    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "second"
