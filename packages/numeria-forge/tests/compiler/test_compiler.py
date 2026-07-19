from pathlib import Path

from numeria_forge.compiler import Compiler, CompilerContext
from numeria_forge.compiler.stages import LoadManifestStage


def test_compiler_returns_context(tmp_path: Path) -> None:
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

    context = Compiler(
        stages=[
            LoadManifestStage(),
        ]
    ).compile(package_directory)

    assert isinstance(context, CompilerContext)
    assert context.manifest is not None
    assert context.manifest.entity.slug == "derivative"