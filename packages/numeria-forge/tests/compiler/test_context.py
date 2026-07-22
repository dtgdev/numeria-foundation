from pathlib import Path

from numeria_forge.compiler import CompilerContext


def test_context_defaults() -> None:
    context = CompilerContext(
        project_root=Path("."),
    )

    assert context.project_root == Path(".")
    assert context.source_directory == Path(".")
    assert context.characters == []
    assert context.published_assets == []
    assert context.diagnostics == []
    assert context.success is True
