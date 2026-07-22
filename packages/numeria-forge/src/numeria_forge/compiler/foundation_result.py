"""Result of compiling an entire Numeria Foundation."""

from __future__ import annotations

from dataclasses import dataclass

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.report import CompilationReport
from numeria_forge.knowledge import CanonicalKnowledgeModel


@dataclass(frozen=True)
class FoundationCompilationResult:
    """Everything produced by one :class:`FoundationCompiler` run.

    Two things a caller almost always wants are promoted to first-class
    properties here rather than left as something you dig out of
    `.context`: the `CompilationReport` (`.report`, pre-existing) and,
    as of v0.16.0, the `CanonicalKnowledgeModel` (`.knowledge_model`).
    Both are compiler *artifacts* in the same sense -- durable,
    queryable output of a compilation, not incidental pipeline
    bookkeeping -- so both get a stable name on the result object
    instead of requiring `result.context.knowledge_model`.
    """

    context: CompilerContext
    report: CompilationReport
    package_results: tuple[CompilerContext, ...] = ()

    @property
    def success(self) -> bool:
        return self.report.success

    @property
    def knowledge_model(self) -> CanonicalKnowledgeModel | None:
        """The `CanonicalKnowledgeModel` built by `BuildKnowledgeModelStage`
        (v0.16.0), or `None` if compilation never reached that stage.
        See `docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md`.
        """

        return self.context.knowledge_model

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
