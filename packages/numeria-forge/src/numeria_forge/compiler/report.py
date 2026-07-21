"""Compilation report."""

from __future__ import annotations

from dataclasses import dataclass, field

from numeria_forge.compiler.diagnostic import Diagnostic


@dataclass(slots=True)
class CompilationReport:
    """Summary of a compilation."""

    diagnostics: list[Diagnostic] = field(default_factory=list)

    generated_files: int = 0

    published_files: int = 0

    duration_seconds: float = 0.0

    @property
    def success(self) -> bool:
        return not any(
            d.severity.lower() == "error"
            for d in self.diagnostics
        )
