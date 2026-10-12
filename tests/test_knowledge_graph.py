
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = ROOT_DIR / "data" / "processed" / "scheme_graph.json"


def load_graph():
    assert GRAPH_FILE.exists(), (
        f"Knowledge Graph file not found: {GRAPH_FILE}"
    )
    return json.loads(GRAPH_FILE.read_text(encoding="utf-8"))


def test_graph_contains_nodes_and_edges():
    graph = load_graph()

    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0


def test_graph_contains_thai_scheme():
    graph = load_graph()

    scheme_names = [
        node["label"]
        for node in graph["nodes"]
        if node.get("node_type") == "scheme"
    ]

    assert any("THAI" in name for name in scheme_names)


def test_thai_is_connected_to_rural_roads():
    graph = load_graph()

    nodes = {node["id"]: node for node in graph["nodes"]}
    thai_ids = {
        node_id
        for node_id, node in nodes.items()
        if node.get("node_type") == "scheme"
        and "THAI" in node.get("label", "")
    }

    rural_roads_ids = {
        node_id
        for node_id, node in nodes.items()
        if node.get("label") == "Rural Roads"
    }

    assert thai_ids, "THAI scheme node was not found."
    assert rural_roads_ids, "Rural Roads node was not found."

    assert any(
        (
            edge["source"] in thai_ids
            and edge["target"] in rural_roads_ids
        )
        or (
            edge["target"] in thai_ids
            and edge["source"] in rural_roads_ids
        )
        for edge in graph["edges"]
    ), "THAI should be connected to Rural Roads."
