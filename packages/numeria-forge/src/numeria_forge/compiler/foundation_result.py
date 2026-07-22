"""Result of compiling an entire Numeria Foundation."""

from __future__ import annotations

from dataclasses import dataclass

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.report import CompilationReport


@dataclass(frozen=True)
class FoundationCompilationResult:
    """Everything produced by one :class:`FoundationCompiler` run."""

    context: CompilerContext
    report: CompilationReport
    package_results: tuple[CompilerContext, ...] = ()

    @property
    def success(self) -> bool:
        return self.report.success

    @property
    def artifact_count(self) -> int:
        return sum(len(result.artifacts) for result in self.package_results)

    def format_report(self, foundation_name: str) -> str:
        lines = [f"Building {foundation_name}...", ""]

        if self.report.diagnostics:
            lines.append(
                f"{len(self.report.diagnostics)} validation diagnostic(s):"
            )

            for diagnostic in self.report.diagnostics:
                lines.append(f"- [{diagnostic.code}] {diagnostic.message}")

            lines.append("")

        lines.append(f"{len(self.package_results)} package(s) compiled")
        lines.append(f"{self.artifact_count} artifact(s) generated")
        lines.append("")
        lines.append("Build succeeded." if self.success else "Build failed.")

        return "\n".join(lines)
