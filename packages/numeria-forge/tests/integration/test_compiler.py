
"""Compiler integration tests."""

from pathlib import Path

from numeria_forge.compiler import (

    Compiler,

    CompilerContext,

)

def test_compiler_returns_report(

    tmp_path: Path,

) -> None:

    compiler = Compiler()

    context = CompilerContext(

        project_root=tmp_path,

    )

    report = compiler.compile(context)

    assert report.success is True

    assert report.generated_assets == 0

    assert report.published_assets == 0

    assert report.diagnostics == 0

