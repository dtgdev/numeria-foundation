from pathlib import Path

from numeria_forge.compiler import (
    CompilerContext,
    Diagnostic,
)


def test_context_collects_diagnostics() -> None:
    context = CompilerContext(
        project_root=Path("/tmp/project"),
        build_directory=Path("/tmp/project/build"),
    )

    diagnostic = Diagnostic(
        severity="warning",
        code="TEST001",
        message="Example",
    )

    context.add_diagnostic(diagnostic)

    assert context.diagnostics == [diagnostic]
