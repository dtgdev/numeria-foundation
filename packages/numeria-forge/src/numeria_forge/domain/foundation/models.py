"""Domain model for the root `numeria.yaml` foundation manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FoundationMetadata:
    """Descriptive metadata for a Numeria Foundation."""

    id: str
    name: str
    version: str


@dataclass(frozen=True)
class FoundationManifest:
    """The loaded root `numeria.yaml` manifest.

    This is the single source of truth referenced at the top of the
    architecture diagram: it tells the Forge Compiler where the knowledge
    base (canon) lives and which workspaces contain compilable packages.
    """

    root_directory: Path
    metadata: FoundationMetadata
    knowledge_root: Path
    workspaces: tuple[Path, ...]
