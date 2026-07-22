from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CompilationReport:
    """Summary of a Forge compilation."""

    stages_executed: int

    characters_processed: int

    assets_published: int

    diagnostics: int

    success: bool