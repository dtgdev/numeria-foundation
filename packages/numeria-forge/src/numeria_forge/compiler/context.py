from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from numeria_forge.publishing import PublishResult


@dataclass(slots=True)
class CompilerContext:
    """Shared mutable state passed through the compiler pipeline."""

    project_root: Path

    project: Any | None = None

    canon: dict[str, Any] = field(default_factory=dict)

    diagnostics: list[Any] = field(default_factory=list)

    generated_assets: list[Any] = field(default_factory=list)

    published_assets: list[PublishResult] = field(default_factory=list)