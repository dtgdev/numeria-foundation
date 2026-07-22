"""Export a `CanonicalKnowledgeModel`'s graph in machine-readable
formats (v0.17.0): JSON, YAML, and GraphML.

    canon/
    knowledge/
        |
        v
    CanonicalKnowledgeModel
        |
        v
    export.to_json / to_yaml / to_graphml
        |
        v
    build/graph/knowledge.{json,yaml,graphml}  (PublishKnowledgeGraphStage)

All three formats serialize the same underlying data -- every
`GraphNode` and `GraphEdge` in `model.graph` -- so a consumer can pick
whichever tool reads it best: `knowledge.json`/`knowledge.yaml` for
anything that already speaks JSON/YAML (a Studio frontend, a script),
`knowledge.graphml` for graph-analysis tools that expect the GraphML
standard (Gephi, yEd, NetworkX's `read_graphml`).

Deterministic ordering (Compiler Law #1): nodes sorted by id, edges
sorted by `(type, id)` -- the same two files exported from the same
Canon twice are byte-identical.
"""

from __future__ import annotations

import json
from typing import Any
from xml.sax.saxutils import escape as _xml_escape

import yaml

GRAPH_EXPORT_SCHEMA = "numeria.knowledge-graph.v1"


def _sorted_nodes(graph) -> list:
    return sorted(graph.nodes.values(), key=lambda node: node.id)


def _sorted_edges(graph) -> list:
    return sorted(graph.edges, key=lambda edge: (edge.type, edge.id))


def to_dict(model) -> dict[str, Any]:
    """The shared, format-agnostic representation every export format
    is built from."""

    graph = model.graph

    return {
        "schema": GRAPH_EXPORT_SCHEMA,
        "nodes": [
            {"id": node.id, "type": node.type} for node in _sorted_nodes(graph)
        ],
        "edges": [
            {
                "id": edge.id,
                "type": edge.type,
                "source": edge.source_id,
                "target": edge.target_id,
                **({"description": edge.description} if edge.description else {}),
            }
            for edge in _sorted_edges(graph)
        ],
    }


def to_json(model, *, indent: int = 2) -> str:
    return json.dumps(to_dict(model), indent=indent)


def to_yaml(model) -> str:
    return yaml.safe_dump(to_dict(model), sort_keys=False)


def to_graphml(model) -> str:
    """A minimal, valid GraphML document -- hand-written rather than
    pulling in a graph library (`networkx` et al.) as a new dependency
    for one export format. Two `<key>` declarations (`d0` for node
    `type`, `d1` for edge `type`), scoped with `for="node"` /
    `for="edge"` per the GraphML spec, since a node's `type` (e.g.
    "Concept") and an edge's `type` (e.g. "REQUIRES") are different
    attributes even though they share a name.
    """

    graph = model.graph
    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="d0" for="node" attr.name="type" attr.type="string"/>',
        '  <key id="d1" for="edge" attr.name="type" attr.type="string"/>',
        '  <graph id="G" edgedefault="directed">',
    ]

    for node in _sorted_nodes(graph):
        lines.append(f'    <node id="{_xml_escape(node.id)}">')
        lines.append(f'      <data key="d0">{_xml_escape(node.type)}</data>')
        lines.append("    </node>")

    for edge in _sorted_edges(graph):
        lines.append(
            f'    <edge id="{_xml_escape(edge.id)}" '
            f'source="{_xml_escape(edge.source_id)}" '
            f'target="{_xml_escape(edge.target_id)}">'
        )
        lines.append(f'      <data key="d1">{_xml_escape(edge.type)}</data>')
        lines.append("    </edge>")

    lines.append("  </graph>")
    lines.append("</graphml>")

    return "\n".join(lines) + "\n"
