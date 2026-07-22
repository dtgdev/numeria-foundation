from __future__ import annotations

import json
from dataclasses import dataclass, field

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.diagnostics import Diagnostic
from numeria_forge.diagnostics import Severity as DiagnosticSeverity


@dataclass(slots=True, frozen=True)
class CompilationReport:
    """Summary of a Forge compilation."""

    stages_executed: int = 0

    characters_processed: int = 0

    assets_published: int = 0

    generated_assets: int = 0

    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is DiagnosticSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is DiagnosticSeverity.WARNING
        )

    @property
    def success(self) -> bool:
        return not any(self._is_error(d) for d in self.diagnostics)

    @staticmethod
    def _is_error(diagnostic: Diagnostic) -> bool:
        severity = diagnostic.severity

        if isinstance(severity, DiagnosticSeverity):
            return severity is DiagnosticSeverity.ERROR

        return str(severity).lower() == "error"

    @classmethod
    def from_context(
        cls,
        context: CompilerContext,
        stages_executed: int = 0,
    ) -> "CompilationReport":
        """Build a report by summarizing a compiled context."""

        return cls(
            stages_executed=stages_executed,
            characters_processed=len(context.characters),
            assets_published=len(context.published_assets),
            generated_assets=len(context.generated_assets),
            diagnostics=list(context.diagnostics),
        )

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "stages_executed": self.stages_executed,
            "characters_processed": self.characters_processed,
            "assets_published": self.assets_published,
            "generated_assets": self.generated_assets,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "diagnostics": [
                {
                    "severity": diagnostic.severity.value,
                    "code": diagnostic.code,
                    "message": diagnostic.message,
                    "location": (
                        str(diagnostic.location)
                        if diagnostic.location is not None
                        else None
                    ),
                }
                for diagnostic in self.diagnostics
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def format_human_readable(self) -> str:
        lines = [
            f"Compiled {self.stages_executed} stage(s): "
            f"{self.characters_processed} character(s) processed, "
            f"{self.generated_assets} asset(s) generated, "
            f"{self.assets_published} asset(s) published.",
            "",
        ]

        if not self.diagnostics:
            lines.append("No diagnostics.")
        else:
            for diagnostic in self.diagnostics:
                location = (
                    f" ({diagnostic.location})"
                    if diagnostic.location is not None
                    else ""
                )

                lines.append(
                    f"[{diagnostic.severity.value.upper()}] "
                    f"{diagnostic.code}: {diagnostic.message}{location}"
                )

            lines.append("")
            lines.append(
                f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)."
            )

        lines.append("Build succeeded." if self.success else "Build failed.")

        return "\n".join(lines)
