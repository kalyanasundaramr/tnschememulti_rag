
import json
import re
from pathlib import Path

import networkx as nx


ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT_DIR / "data" / "processed" / "tnrd_schemes_clean.json"
OUTPUT_FILE = ROOT_DIR / "data" / "processed" / "scheme_graph.json"


# Infrastructure categories used only when their terms occur in source text.
INFRASTRUCTURE_TERMS = {
    "Water Supply": ["water supply", "drinking water", "water pipeline"],
    "Rural Roads": ["rural roads", "village roads", "cement concrete roads"],
    "Street Lights": ["street lights", "streetlights"],
    "Burial Grounds": ["burial grounds"],
    "Anganwadi Centres": ["anganwadi centres", "anganwadi centers"],
    "Public Distribution Shops": [
        "public distribution system shops",
        "pds shops",
    ],
    "Self Help Group Buildings": ["shg buildings", "self help group buildings"],
    "Playgrounds": ["play ground", "playgrounds"],
    "Drainage": ["drainage", "drains"],
    "Sanitation": ["sanitation", "toilets"],
}


def contains_term(text, terms):
    text = text.lower()
    return any(term in text for term in terms)


def build_graph():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Scheme data not found: {INPUT_FILE}"
        )

    records = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    graph = nx.Graph()

    for record in records:
        name = record.get("scheme_name", "").strip()
        content = record.get("content", "").strip()
        source_url = record.get("source_url", "").strip()

        if not name:
            continue

        scheme_id = f"scheme::{name}"

        graph.add_node(
            scheme_id,
            label=name,
            node_type="scheme",
            source_url=source_url,
        )

        # Add only infrastructure categories explicitly mentioned
        # in this scheme's source text.
        for category, terms in INFRASTRUCTURE_TERMS.items():
            if contains_term(content, terms):
                category_id = f"infrastructure::{category}"

                graph.add_node(
                    category_id,
                    label=category,
                    node_type="infrastructure",
                )

                graph.add_edge(
                    scheme_id,
                    category_id,
                    relationship="mentions_infrastructure",
                    evidence=", ".join(
                        term for term in terms
                        if term in content.lower()
                    ),
                )

    nodes = [
        {"id": node_id, **attributes}
        for node_id, attributes in graph.nodes(data=True)
    ]

    edges = [
        {"source": source, "target": target, **attributes}
        for source, target, attributes in graph.edges(data=True)
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(
            {"nodes": nodes, "edges": edges},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Knowledge Graph created successfully.")
    print(f"Source schemes: {len(records)}")
    print(f"Graph nodes: {graph.number_of_nodes()}")
    print(f"Graph edges: {graph.number_of_edges()}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nSample relationships:")
    for source, target, attributes in list(graph.edges(data=True))[:10]:
        print(
            f"- {graph.nodes[source]['label']} "
            f"--[{attributes['relationship']}]--> "
            f"{graph.nodes[target]['label']}"
        )


if __name__ == "__main__":
    build_graph()
