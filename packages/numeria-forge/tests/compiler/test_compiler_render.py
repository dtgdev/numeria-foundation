from pathlib import Path

from numeria_forge.compiler import Compiler
from numeria_forge.compiler.stages import (
    LoadManifestStage,
    RegisterBuiltinArtifactsStage,
    RenderTemplatesStage,
)


def test_compiler_renders_manifest_outputs(tmp_path: Path) -> None:
    package_directory = tmp_path / "derivative"
    package_directory.mkdir()

    manifest = """
schema_version: "1.0"

entity:
  type: concept
  id: numeria:concept:derivative
  slug: derivative
  title: Derivative

outputs:
  - template: concept/README.md.j2
    destination: README.md
""".strip()

    (package_directory / "manifest.yaml").write_text(
        manifest,
        encoding="utf-8",
    )

    template_root = Path(__file__).resolve().parents[2] / "templates"

    context = Compiler(
        stages=[
            LoadManifestStage(),
            RegisterBuiltinArtifactsStage(),
            RenderTemplatesStage(template_root),
        ]
    ).compile(package_directory)

    assert len(context.artifacts) == 1

    artifact = next(iter(context.artifacts))

    assert artifact.destination == Path("README.md")
    assert "Derivative" in artifact.content


def test_compiler_renders_builtin_artifact(tmp_path: Path) -> None:
    package_directory = tmp_path / "derivative"
    package_directory.mkdir()

    manifest = """
schema_version: "1.0"

entity:
  type: concept
  id: numeria:concept:derivative
  slug: derivative
  title: Derivative

outputs:
  - artifact: readme
""".strip()

    (package_directory / "manifest.yaml").write_text(
        manifest,
        encoding="utf-8",
    )

    template_root = Path(__file__).resolve().parents[2] / "templates"

    context = Compiler(
        stages=[
            LoadManifestStage(),
            RegisterBuiltinArtifactsStage(),
            RenderTemplatesStage(template_root),
        ]
    ).compile(package_directory)

    assert len(context.artifacts) == 1

    artifact = next(iter(context.artifacts))

    assert artifact.destination == Path("README.md")
    assert "Derivative" in artifact.content


def test_compiler_renders_multiple_builtin_artifacts(
    tmp_path: Path,
) -> None:
    package_directory = tmp_path / "derivative"
    package_directory.mkdir()

    manifest = """
schema_version: "1.0"

entity:
  type: concept
  id: numeria:concept:derivative
  slug: derivative
  title: Derivative

outputs:
  - artifact: readme
  - artifact: character_card
""".strip()

    (package_directory / "manifest.yaml").write_text(
        manifest,
        encoding="utf-8",
    )

    template_root = Path(__file__).resolve().parents[2] / "templates"

    context = Compiler(
        stages=[
            LoadManifestStage(),
            RegisterBuiltinArtifactsStage(),
            RenderTemplatesStage(template_root),
        ]
    ).compile(package_directory)

    assert len(context.artifacts) == 2

    destinations = {
        artifact.destination.name
        for artifact in context.artifacts
    }

    assert destinations == {
        "README.md",
        "CHARACTER_CARD.md",
    }
