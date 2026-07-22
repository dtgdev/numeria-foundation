"""A single directed edge in the semantic dependency graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """One relationship entity, as a directed graph edge.

    `id` is the relationship entity's own canonical id (`NUM-REL-...`);
    `type` is the relationship type (`REQUIRES`, `FRIEND_OF`, ...), the
    key into `RelationshipOntology.types`. `source_id`/`target_id` are
    the bare canonical IDs the relationship connects -- always bare IDs,
    never paths, per Canon Law #3.
    """

    id: str
    type: str
    source_id: str
    target_id: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None
