from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import yaml

from numeria_forge.knowledge import to_dict, to_graphml, to_json, to_yaml


def test_to_dict_has_the_expected_schema_and_shape(model) -> None:
    data = to_dict(model)

    assert data["schema"] == "numeria.knowledge-graph.v1"
    assert {n["id"] for n in data["nodes"]} == set(model.graph.nodes.keys())
    assert len(data["edges"]) == len(model.graph.edges)
    edge = next(e for e in data["edges"] if e["id"] == "REL-005")
    assert edge == {
        "id": "REL-005",
        "type": "REPRESENTED_BY",
        "source": "CON-DERIVATIVE",
        "target": "CHR-DETECTIVE",
    }


def test_nodes_are_sorted_by_id_and_edges_by_type_then_id(model) -> None:
    data = to_dict(model)

    node_ids = [n["id"] for n in data["nodes"]]
    assert node_ids == sorted(node_ids)

    edge_keys = [(e["type"], e["id"]) for e in data["edges"]]
    assert edge_keys == sorted(edge_keys)


def test_to_json_round_trips_to_the_same_dict(model) -> None:
    assert json.loads(to_json(model)) == to_dict(model)


def test_to_yaml_round_trips_to_the_same_dict(model) -> None:
    assert yaml.safe_load(to_yaml(model)) == to_dict(model)


def test_to_json_and_to_yaml_are_deterministic_across_calls(model) -> None:
    assert to_json(model) == to_json(model)
    assert to_yaml(model) == to_yaml(model)


def test_to_graphml_is_well_formed_xml_with_every_node_and_edge(model) -> None:
    xml_text = to_graphml(model)

    root = ET.fromstring(xml_text)
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}

    nodes = root.findall(".//g:graph/g:node", ns)
    edges = root.findall(".//g:graph/g:edge", ns)

    assert len(nodes) == len(model.graph.nodes)
    assert len(edges) == len(model.graph.edges)

    node_ids = {node.get("id") for node in nodes}
    assert node_ids == set(model.graph.nodes.keys())


def test_to_graphml_escapes_xml_special_characters(model) -> None:
    import dataclasses

    from numeria_forge.semantics.edge import GraphEdge

    tricky_edge = GraphEdge(
        id="REL-XML", type="Q&A <test>", source_id="CON-DERIVATIVE",
        target_id="CON-LIMIT",
    )
    graph = dataclasses.replace(model.graph, edges=model.graph.edges + (tricky_edge,))
    tricky_model = dataclasses.replace(model, graph=graph)

    xml_text = to_graphml(tricky_model)

    # Must not contain a raw, unescaped ampersand/angle bracket inside
    # the data payload -- ET.fromstring will raise on malformed XML if
    # escaping is missing, which is the real assertion here.
    ET.fromstring(xml_text)
    assert "Q&amp;A &lt;test&gt;" in xml_text
