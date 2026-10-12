
from retrieval.hybrid_retriever import search_hybrid
from generation.answer_generator import generate_answer


def ask_scheme_question(question: str, limit: int = 5) -> dict:
    """Retrieve scheme evidence and generate a grounded answer."""

    results = search_hybrid(question, limit=limit)

    if not results:
        return {
            "question": question,
            "answer": (
                "The available scheme documents do not provide "
                "enough information to answer this question."
            ),
            "sources": [],
            "retrieved_schemes": [],
        }

    context_parts = []
    sources = []
    retrieved_schemes = []

    for result in results:
        scheme_name = result["scheme_name"]
        source_url = result["source_url"]
        content = result["content"]

        context_parts.append(
            f"Scheme: {scheme_name}\n"
            f"Source URL: {source_url}\n"
            f"Document content:\n{content}"
        )

        retrieved_schemes.append(scheme_name)

        if source_url and source_url not in sources:
            sources.append(source_url)

    context = "\n\n---\n\n".join(context_parts)
    answer = generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
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

    print("\nRetrieved schemes:")
    for scheme in result["retrieved_schemes"]:
        print(f"- {scheme}")

    print("\nSource URLs:")
    for source in result["sources"]:
        print(f"- {source}")
