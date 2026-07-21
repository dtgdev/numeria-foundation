
"""Compiler execution context."""

from __future__ import annotations

from dataclasses import dataclass, field

from pathlib import Path

from numeria_forge.publishing import PublishResult

@dataclass(slots=True)

class CompilerContext:

    """Shared mutable state for the compiler pipeline."""

    project_root: Path

    generated_assets: list[object] = field(

        default_factory=list,

    )

    published_assets: list[PublishResult] = field(

        default_factory=list,

    )

    diagnostics: list[str] = field(

        default_factory=list,

    )

