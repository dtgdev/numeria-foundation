"""Cycle detection over a SemanticGraph.

A cycle among a *dependency* relationship type (e.g. Concept A
`REQUIRES` Concept B `REQUIRES` Concept A) is a structural defect: it
means "you must already understand A to learn A". This module finds
such cycles -- restricted to whichever edge types the caller cares
about (normally `RelationshipOntology.acyclic_type_names()`) -- and
reports the actual path, not just a yes/no.

Classic three-color DFS (white/gray/black): a back-edge into a node
still on the current DFS stack (gray) is a cycle. Recursive, which is
fine at Numeria's current knowledge-base scale (low hundreds of
entities); a graph large enough to hit Python's recursion limit would
need an iterative rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from numeria_forge.semantics.graph import SemanticGraph

_WHITE, _GRAY, _BLACK = 0, 1, 2


@dataclass(frozen=True, slots=True)
class Cycle:
    """One cycle, as the ordered path of node ids that forms it.

    The first and last entries are the same node id, e.g.
    `("NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000001")`.
    """

    nodes: tuple[str, ...]

    def __str__(self) -> str:
        return " -> ".join(self.nodes)


class CycleDetector:
    """Find cycles in a SemanticGraph, restricted to a set of edge types."""

    def __init__(self, graph: SemanticGraph) -> None:
        self._graph = graph

    def find_cycles(self, *, types: Iterable[str] | None = None) -> tuple[Cycle, ...]:
        adjacency = self._graph.adjacency(types=types)
        color: dict[str, int] = {node_id: _WHITE for node_id in self._graph.nodes}
        path: list[str] = []
        cycles: list[Cycle] = []

        def visit(node_id: str) -> None:
            color[node_id] = _GRAY
            path.append(node_id)

            for neighbor in adjacency.get(node_id, ()):
                neighbor_color = color[neighbor]

                if neighbor_color == _WHITE:
                    visit(neighbor)
                elif neighbor_color == _GRAY:
                    start = path.index(neighbor)
                    cycles.append(Cycle(nodes=tuple(path[start:]) + (neighbor,)))

            path.pop()
            color[node_id] = _BLACK

        for node_id in self._graph.nodes:
            if color[node_id] == _WHITE:
                visit(node_id)

        return tuple(cycles)

    def has_cycle(self, *, types: Iterable[str] | None = None) -> bool:
        return len(self.find_cycles(types=types)) > 0
