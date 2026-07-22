"""Compiler integration tests."""

from pathlib import Path

from numeria_forge.compiler import (
    CompilationReport,
    Compiler,
    CompilerContext,
)


def test_compiler_returns_report(tmp_path: Path) -> None:
    compiler = Compiler(stages=[])

    context = CompilerContext(project_root=tmp_path)

    result_context = compiler.compile(context)

    report = CompilationReport.from_context(result_context)

    assert report.success is True
    assert report.generated_assets == 0
    assert report.assets_published == 0
    assert report.diagnostics == []
