from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspaceMetadata:
    """Descriptive metadata for a Numeria Forge workspace."""

    id: str
    name: str
    version: str


@dataclass(frozen=True)
class WorkspacePackage:
    """A package declared inside a workspace."""

    path: Path

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class Workspace:
    """A loaded Numeria Forge workspace."""

    root_directory: Path
    metadata: WorkspaceMetadata
    packages: tuple[WorkspacePackage, ...]
