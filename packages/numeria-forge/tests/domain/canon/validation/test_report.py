import json
from pathlib import Path

from numeria_forge.domain.canon.validation import CanonDiagnostic, CanonSeverity
from numeria_forge.domain.canon.validation.report import CanonValidationReport


def test_empty_report_is_successful() -> None:
    report = CanonValidationReport(
        knowledge_root=Path("knowledge"), entity_count=3, diagnostics=()
    )

    assert report.success is True
    assert report.errors == ()
    assert report.warnings == ()
    assert "internally consistent" in report.format_human_readable()


def test_report_with_only_warnings_is_still_successful() -> None:
    report = CanonValidationReport(
        knowledge_root=Path("knowledge"),
        entity_count=1,
        diagnostics=(
            CanonDiagnostic(
                severity=CanonSeverity.WARNING, code="x", message="a warning"
            ),
        ),
    )

    assert report.success is True
    assert len(report.warnings) == 1
    assert len(report.errors) == 0


def test_report_with_an_error_fails() -> None:
    report = CanonValidationReport(
        knowledge_root=Path("knowledge"),
        entity_count=1,
        diagnostics=(
            CanonDiagnostic(
                severity=CanonSeverity.ERROR,
                code="x",
                message="an error",
                location=Path("knowledge/x/entity.yaml"),
            ),
        ),
    )

    assert report.success is False
    assert len(report.errors) == 1

    human = report.format_human_readable()
    assert "[ERROR] x: an error" in human
    assert "NOT internally consistent" in human


def test_to_json_round_trips() -> None:
    report = CanonValidationReport(
        knowledge_root=Path("knowledge"),
        entity_count=2,
        diagnostics=(
            CanonDiagnostic(
                severity=CanonSeverity.ERROR,
                code="canon.naming",
                message="bad id",
                location=Path("knowledge/x/entity.yaml"),
            ),
        ),
    )

    data = json.loads(report.to_json())

    assert data["success"] is False
    assert data["entity_count"] == 2
    assert data["error_count"] == 1
    assert data["warning_count"] == 0
    assert data["diagnostics"][0]["code"] == "canon.naming"
    assert data["diagnostics"][0]["location"] == "knowledge/x/entity.yaml"
