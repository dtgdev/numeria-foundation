"""Write the final Compilation Report to `build/reports/`.

Deliberately a plain function, not a `CompilerStage`: a `CompilerStage`
only ever sees `CompilerContext`, but `CompilationReport` is a derived
object `FoundationCompiler` builds *after* every stage (including
Package-adjacent bookkeeping) has run, since it needs the final
`stages_executed` count. Forcing report-writing into the
`execute(context)` shape would mean smuggling the report through
`context` just to satisfy an interface it doesn't need -- simpler to
call this directly once the report exists.

Three files, matching the target `build/reports/` layout:

* `compile.json` -- the full `CompilationReport`, same shape as
  `forge compile --json`.
* `diagnostics.json` -- just the diagnostics slice of that same report
  (`error_count`, `warning_count`, `diagnostics`), for tooling that
  only cares about problems, not build statistics.
* `diagnostics.md` -- the same diagnostics, formatted for humans.

Like all `build/` output, these are overwritten unconditionally on
every compile -- there is nothing hand-authored here to protect.
"""

from __future__ import annotations

import json
from pathlib import Path

from numeria_forge.compiler.report import CompilationReport
from numeria_forge.infrastructure.repository import RepositoryWriter


def write_build_reports(
    build_directory: Path,
    report: CompilationReport,
    writer: RepositoryWriter | None = None,
) -> None:
    writer = writer or RepositoryWriter()
    reports_directory = build_directory / "reports"

    report_dict = report.to_dict()

    writer.write(
        destination=reports_directory / "compile.json",
        content=json.dumps(report_dict, indent=2),
        overwrite=True,
    )

    diagnostics_dict = {
        "error_count": report_dict["error_count"],
        "warning_count": report_dict["warning_count"],
        "diagnostics": report_dict["diagnostics"],
    }

    writer.write(
        destination=reports_directory / "diagnostics.json",
        content=json.dumps(diagnostics_dict, indent=2),
        overwrite=True,
    )

    writer.write(
        destination=reports_directory / "diagnostics.md",
        content=_format_diagnostics_markdown(report),
        overwrite=True,
    )


def _format_diagnostics_markdown(report: CompilationReport) -> str:
    lines = ["# Diagnostics", ""]

    if not report.diagnostics:
        lines.append("No diagnostics.")
        return "\n".join(lines) + "\n"

    lines.append(
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    lines.append("")

    for diagnostic in report.diagnostics:
        location = (
            f" ({diagnostic.location})" if diagnostic.location is not None else ""
        )
        lines.append(
            f"- **[{diagnostic.severity.value.upper()}]** "
            f"`{diagnostic.code}`: {diagnostic.message}{location}"
        )

    return "\n".join(lines) + "\n"
