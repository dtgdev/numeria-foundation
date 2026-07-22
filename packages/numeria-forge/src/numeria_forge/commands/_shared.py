"""Small helpers shared across `forge` CLI command modules."""

from __future__ import annotations

from pathlib import Path


def resolve_knowledge_root(path: Path) -> Path:
    """Resolve a knowledge root from a foundation root, a parent of
    `knowledge/`, or a knowledge root passed directly.

    Shared by `cli.py`'s top-level commands (`validate`, `compile`,
    `doctor`) and `commands/graph.py`'s `forge graph *` commands, so
    both accept the same three kinds of path argument identically.
    """

    from numeria_forge.infrastructure.foundation_loader import FoundationLoader

    resolved = path.resolve()

    if (resolved / "numeria.yaml").is_file():
        return FoundationLoader().load(resolved).knowledge_root

    if (resolved / "knowledge").is_dir():
        return resolved / "knowledge"

    return resolved
