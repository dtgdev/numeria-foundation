"""A single node in the semantic dependency graph."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GraphNode:
    """One non-relationship canonical entity, as a graph node.

    Deliberately minimal: just enough to identify the entity (`id`,
    `type`). The graph is a view over the Canon for structural analysis
    (cycles, ordering) -- it is not a second copy of entity content.
    Look the full entity up in `Canon.entities[node.id]` if you need
    more.
    """

    id: str
    type: str
