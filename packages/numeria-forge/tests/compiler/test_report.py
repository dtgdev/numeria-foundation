from numeria_forge.compiler.diagnostic import Diagnostic
from numeria_forge.compiler.report import CompilationReport


def test_report_success() -> None:
    report = CompilationReport()

    assert report.success


def test_report_failure() -> None:
    report = CompilationReport(
        diagnostics=[
            Diagnostic(
                severity="error",
                code="ERR001",
                message="Boom",
            )
        ]
    )

    assert not report.success
