
"""Compilation reporting."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True)

class CompilationReport:

    """Summary of a compilation run."""

    success: bool

    generated_assets: int

    published_assets: int

    diagnostics: int

