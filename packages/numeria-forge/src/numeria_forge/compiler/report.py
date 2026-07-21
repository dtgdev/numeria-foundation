"""Compiler result models."""

from dataclasses import dataclass

from numeria_forge.compiler.diagnostics import Diagnostic


@dataclass(frozen=True)
class CompilationReport:
    """Summary of a Forge compilation."""

    status: str
    duration_seconds: float
    diagnostics: tuple[Diagnostic, ...]
    generated_assets: int
    published_assets: int
    completed_stages: tuple[str, ...]

    @property
    def succeeded(self) -> bool:
        """Return whether compilation succeeded."""

        return self.status == "success"
