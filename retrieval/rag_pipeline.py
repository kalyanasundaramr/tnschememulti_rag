
import json
from pathlib import Path

from generation.answer_generator import generate_answer
from retrieval.hybrid_retriever import search_hybrid


ROOT_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = ROOT_DIR / "data" / "processed" / "scheme_graph.json"


def get_graph_insights(scheme_names=None):
    """Find local Knowledge Graph relationships for retrieved schemes."""

    if not GRAPH_FILE.exists():
        return "Knowledge Graph file not found. Run graph/build_graph.py."

    graph_data = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    node_lookup = {node["id"]: node for node in nodes}
    selected_names = {
        name.strip().casefold()
        for name in (scheme_names or [])
    }

    insights = []

    for edge in edges:
        source = node_lookup.get(edge["source"], {})
        target = node_lookup.get(edge["target"], {})

        source_name = source.get("label", edge["source"])
        target_name = target.get("label", edge["target"])

        # Show relationships for retrieved schemes when available.
        if selected_names and (
            source_name.strip().casefold() not in selected_names
            and target_name.strip().casefold() not in selected_names
        ):
            continue

        relationship = edge.get("relationship", "related to")
        evidence = edge.get("evidence", "")

        line = f"- {source_name} --[{relationship}]--> {target_name}"
        if evidence:
            line += f" (source terms: {evidence})"

        insights.append(line)

    if not insights:
        return (
            "No matching graph relationships were found for the retrieved "
            "schemes."
        )

    return "\n".join(insights)


def ask_scheme_question(question: str, limit: int = 5) -> dict:
    """Retrieve document evidence, add local graph insights, and answer."""

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    results = search_hybrid(question, limit=limit)

    retrieved_schemes = [
        result["scheme_name"]
        for result in results
    ]

    graph_answer = get_graph_insights(retrieved_schemes)

    context_parts = [
        "Knowledge Graph relationships:\n" + graph_answer
    ]
    sources = []

    for result in results:
        scheme_name = result["scheme_name"]
        source_url = result["source_url"]
        content = result["content"]

        context_parts.append(
            f"Scheme: {scheme_name}\n"
            f"Source URL: {source_url}\n"
            f"Document content:\n{content}"
        )

        if source_url and source_url not in sources:
            sources.append(source_url)

    if not results:
        return {
            "question": question,
            "answer": (
                "The available scheme documents did not provide enough "
                "information to answer this question."
            ),
            "graph_answer": graph_answer,
            "sources": [],
            "retrieved_schemes": [],
        }

    context = "\n\n---\n\n".join(context_parts)
    answer = generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "graph_answer": graph_answer,
        "sources": sources,
        "retrieved_schemes": retrieved_schemes,
    }


if __name__ == "__main__":
    question = "Which scheme improves village roads and rural connectivity?"
    result = ask_scheme_question(question)

    print("\nQuestion:")
    print(result["question"])

    print("\nAnswer:")
    print(result["answer"])

    print("\nKnowledge Graph Insights:")
    print(result["graph_answer"])

    print("\nRetrieved schemes:")
    for scheme in result["retrieved_schemes"]:
        print(f"- {scheme}")

    print("\nSource URLs:")
    for source in result["sources"]:
        print(f"- {source}")
