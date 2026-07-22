from __future__ import annotations

from dataclasses import dataclass

from numeria_forge.compiler.diagnostics import Diagnostic


@dataclass(slots=True, frozen=True)
class CompilerResult:
    success: bool
    diagnostics: list[Diagnostic]