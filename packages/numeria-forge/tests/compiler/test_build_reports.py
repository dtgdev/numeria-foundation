import json
from pathlib import Path

from numeria_forge.compiler.build_reports import write_build_reports
from numeria_forge.compiler.report import CompilationReport
from numeria_forge.diagnostics import Diagnostic, Severity


def test_writes_all_three_report_files_for_a_clean_build(tmp_path: Path) -> None:
    report = CompilationReport(stages_executed=6)

    write_build_reports(tmp_path / "build", report)

    reports_dir = tmp_path / "build" / "reports"
    assert (reports_dir / "compile.json").exists()
    assert (reports_dir / "diagnostics.json").exists()
    assert (reports_dir / "diagnostics.md").exists()

    compile_data = json.loads((reports_dir / "compile.json").read_text())
    assert compile_data["success"] is True
    assert compile_data["stages_executed"] == 6

    diagnostics_data = json.loads((reports_dir / "diagnostics.json").read_text())
    assert diagnostics_data == {
        "error_count": 0,
        "warning_count": 0,
        "diagnostics": [],
    }

    assert (
        reports_dir / "diagnostics.md"
    ).read_text() == "# Diagnostics\n\nNo diagnostics.\n"


def test_diagnostics_files_reflect_errors_and_warnings(tmp_path: Path) -> None:
    report = CompilationReport(
        stages_executed=2,
        diagnostics=[
            Diagnostic(
                severity=Severity.ERROR,
                code="canon.schema",
                message="missing field",
            ),
            Diagnostic(
                severity=Severity.WARNING,
                code="canon.identity",
                message="duplicate name",
            ),
        ],
    )

    write_build_reports(tmp_path / "build", report)

    reports_dir = tmp_path / "build" / "reports"

    diagnostics_data = json.loads((reports_dir / "diagnostics.json").read_text())
    assert diagnostics_data["error_count"] == 1
    assert diagnostics_data["warning_count"] == 1
    assert len(diagnostics_data["diagnostics"]) == 2

    markdown = (reports_dir / "diagnostics.md").read_text()
    assert "1 error(s), 1 warning(s)." in markdown
    assert "canon.schema" in markdown
    assert "canon.identity" in markdown


def test_overwrites_on_repeated_calls(tmp_path: Path) -> None:
    write_build_reports(tmp_path / "build", CompilationReport(stages_executed=1))
    write_build_reports(tmp_path / "build", CompilationReport(stages_executed=99))

    compile_data = json.loads(
        (tmp_path / "build" / "reports" / "compile.json").read_text()
    )
    assert compile_data["stages_executed"] == 99
