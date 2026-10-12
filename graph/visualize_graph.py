
import html
from pydoc import html
import json
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network


ROOT_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = ROOT_DIR / "data" / "processed" / "scheme_graph.json"
SCHEMES_FILE = ROOT_DIR / "data" / "processed" / "tnrd_schemes_clean.json"

def render_knowledge_graph(height=650):
    """Display all schemes or focus on one scheme and its relationships."""

    if not GRAPH_FILE.exists():
        st.warning(
            "Knowledge Graph not found. Run: python graph\\build_graph.py"
        )
        return

    graph_data = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.info("The Knowledge Graph contains no nodes.")
        return

    node_lookup = {node["id"]: node for node in nodes}
    scheme_nodes = [
        node for node in nodes
        if node.get("node_type") == "scheme"
    ]

    scheme_names = sorted(
        node.get("label", node["id"]) for node in scheme_nodes
    )

    selected_scheme = st.selectbox(
        "Select a government scheme",
        ["All schemes"] + scheme_names,
        key="knowledge_graph_scheme",
    )

    if selected_scheme != "All schemes":
        selected_ids = {
            node["id"]
            for node in scheme_nodes
            if node.get("label") == selected_scheme
        }

        visible_edges = [
            edge for edge in edges
            if edge["source"] in selected_ids
            or edge["target"] in selected_ids
        ]

        visible_ids = set(selected_ids)
        for edge in visible_edges:
            visible_ids.add(edge["source"])
            visible_ids.add(edge["target"])

        visible_nodes = [
            node for node in nodes
            if node["id"] in visible_ids
        ]
    else:
        visible_nodes = nodes
        visible_edges = edges

    network = Network(
        height=f"{height}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
        notebook=False,
        cdn_resources="in_line",
    )

    network.barnes_hut(
        gravity=-3000,
        central_gravity=0.5,
        spring_length=130,
        spring_strength=0.03,
        damping=0.15,
    )

    for node in visible_nodes:
        node_type = node.get("node_type", "unknown")
        is_scheme = node_type == "scheme"

        network.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            title=(
                f"Type: {node_type}\n"
                f"Source: {node.get('source_url', 'Not available')}"
            ),
            color="#2563eb" if is_scheme else "#16a34a",
            shape="dot",
            size=18 if is_scheme else 13,
            font={"size": 12, "face": "Arial"},
        )

    for edge in visible_edges:
        source = node_lookup.get(edge["source"], {})
        target = node_lookup.get(edge["target"], {})

        relationship = edge.get("relationship", "related to")
        evidence = edge.get("evidence", "")

        network.add_edge(
            edge["source"],
            edge["target"],
            title=(
                f"{source.get('label', edge['source'])} "
                f"--[{relationship}]--> "
                f"{target.get('label', edge['target'])}\n"
                f"Evidence: {evidence}"
            ),
            label="",
            color="#94a3b8",
        )

    with tempfile.TemporaryDirectory() as temp_dir:

        html_path = Path(temp_dir) / "knowledge_graph.html"
        html = network.generate_html(notebook=False)
        html_path.write_text(html, encoding="utf-8")


    components.html(html, height=height, scrolling=True)

    st.caption(
        "Blue: government schemes | Green: infrastructure categories. "
        "Drag nodes to rearrange them and hover over connections for details."
    )
    st.caption(
        f"Showing {len(visible_nodes)} nodes and "
        f"{len(visible_edges)} relationships."
    )

    # Scheme details panel
    if selected_scheme != "All schemes":
        schemes = json.loads(
            SCHEMES_FILE.read_text(encoding="utf-8")
        )

        selected_record = next(
            (
                record for record in schemes
                if record.get("scheme_name", "").strip() == selected_scheme
            ),
            None,
        )

        st.divider()
        st.subheader("ðŸ“‹ Scheme Details")

        if selected_record:
            st.markdown(f"**{selected_record['scheme_name']}**")

            source_url = selected_record.get("source_url", "")
            if source_url:
                st.markdown(f"[Open official source document]({source_url})")

            with st.expander("View source document content"):
                st.text(selected_record.get("content", "No content available."))

            st.markdown("**Connected infrastructure**")

            connected_categories = []
            for edge in visible_edges:
                if edge["source"] in selected_ids:
                    other_id = edge["target"]
                elif edge["target"] in selected_ids:
                    other_id = edge["source"]
                else:
                    continue

                other_node = node_lookup.get(other_id, {})
                if other_node.get("node_type") == "infrastructure":
                    connected_categories.append(other_node.get("label", other_id))

            if connected_categories:
                for category in sorted(set(connected_categories)):
                    st.write(f"- {category}")
            else:
                st.info("No infrastructure relationships found for this scheme.")
        else:
            st.info("No source record found for the selected scheme.")
