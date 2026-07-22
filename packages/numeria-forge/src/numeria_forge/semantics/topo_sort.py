"""Topological ordering over a SemanticGraph.

Kahn's algorithm: repeatedly peel off nodes with no remaining incoming
edge (within the given edge types). If nodes remain once no more can be
peeled off, the graph has a cycle -- reported as a clean
`TopologicalSortError` (using `CycleDetector` to name the actual cycle)
rather than an infinite loop or a silently wrong partial order.

Nodes with no relevant edges at all (isolated with respect to the given
types) are included in the result -- topological order only constrains
nodes that actually depend on each other; unrelated nodes may appear in
any position consistent with the partial order, and this
implementation places them before anything that depends on them, in
node-id order, for a deterministic result.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable

from numeria_forge.semantics.cycle_detector import Cycle, CycleDetector
from numeria_forge.semantics.graph import SemanticGraph


class TopologicalSortError(ValueError):
    """Raised when the requested edge types do not form a DAG."""

    def __init__(self, cycles: tuple[Cycle, ...]) -> None:
        self.cycles = cycles
        cycle_text = "; ".join(str(cycle) for cycle in cycles)
        super().__init__(f"Graph contains {len(cycles)} cycle(s): {cycle_text}")


def topological_sort(
    graph: SemanticGraph, *, types: Iterable[str] | None = None
) -> tuple[str, ...]:
    """Return every node id in `graph`, ordered so that for every edge
    A -> B (of one of `types`), A comes before B.

    Raises `TopologicalSortError` if the restricted graph has a cycle.
    """

    adjacency = graph.adjacency(types=types)

    in_degree: dict[str, int] = {node_id: 0 for node_id in graph.nodes}

    for source_id, targets in adjacency.items():
        for target_id in targets:
            in_degree[target_id] += 1

    # Deterministic order: process ready nodes in sorted node-id order
    # rather than dict/insertion order, so the result doesn't depend on
    # Canon load order.
    ready = deque(
        sorted(node_id for node_id, degree in in_degree.items() if degree == 0)
    )
    ordered: list[str] = []

    while ready:
        node_id = ready.popleft()
        ordered.append(node_id)

        newly_ready = []

        for neighbor in adjacency.get(node_id, ()):
            in_degree[neighbor] -= 1

            if in_degree[neighbor] == 0:
                newly_ready.append(neighbor)

        for neighbor in sorted(newly_ready):
            _insert_sorted(ready, neighbor)

    if len(ordered) != len(graph.nodes):
        cycles = CycleDetector(graph).find_cycles(types=types)
        raise TopologicalSortError(cycles)

    return tuple(ordered)


def _insert_sorted(queue: deque[str], value: str) -> None:
    """Insert `value` into `queue` keeping it sorted (queues here stay
    small -- low hundreds of entities -- so linear insertion is fine)."""

    for index, existing in enumerate(queue):
        if value < existing:
            queue.insert(index, value)
            return

    queue.append(value)
