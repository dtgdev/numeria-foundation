"""Compiler execution context."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from numeria_forge.compiler.diagnostic import Diagnostic
from numeria_forge.publishing.result import PublishResult


@dataclass(slots=True)
class CompilerContext:
    """Shared state flowing through compiler stages."""

    project_root: Path

    build_directory: Path

    diagnostics: list[Diagnostic] = field(
        default_factory=list
    )

    published: list[PublishResult] = field(
        default_factory=list
    )

    generated_files: int = 0

    def add_diagnostic(
        self,
        diagnostic: Diagnostic,
    ) -> None:
        self.diagnostics.append(diagnostic)
